import time

from canvas import CourseManager
from canvasapi.progress import Progress
from canvas.cli import confirm, menu, text
from canvasapi.assignment import Assignment
from canvas.configcourse import ConfigCourse

class Grader(object):
  # Assignment properties
  assignment_defaults = {
    'receptacle': {
      'grading_type': 'points',
      'name': None,
      'notify_of_update': False,
      'omit_from_final_grade': True,
      'points_possible': 3,
      'submission_types': ['none'],
      'use_rubric_for_grading': False,
    },
  }

  assignment_defaults['mastery'] = {
    **assignment_defaults['receptacle'],
  }


  def __init__(self, config: ConfigCourse) -> None:
    self.config = config

    print("Starting...")

    # Connect to Canvas course.
    self.course_manager = CourseManager(self.config)
    self.course = self.course_manager.get_course()

    # Pre-load existing assignments.
    self.invalidate_assignments()
    self.get_assignments()

    # Set state.
    self.receptacle_upload_progress = None
    self.outcomes = {}

    print('Course:', self.course)
    print()


  def get_assignments(self):
    if not self.assignments:
      self.assignments = sorted(self.course.get_assignments(), key=lambda a: getattr(a, 'name', None))

    return self.assignments


  def invalidate_assignments(self):
    self.assignments = []


  def get_mastery(self, receptacle: Assignment) -> Assignment:
    # Use same assignment for mastery?
    mastery_same = confirm('Use the same assignment for mastery? ')
    print()

    if mastery_same:
      # Use receptacle as mastery.
      return receptacle

    name = getattr(receptacle, 'name', None)

    # Select or create mastery.
    return self.select_or_create(
      [a for a in self.get_assignments()
        if a.grading_type == 'points' and a.submission_types == ['none'] and not a.is_quiz_assignment],
      type='mastery',
      default=f'{name} Mastery' if name else '',
    )


  def select_or_create(self, collection, type = 'assignment', default = '', properties = {}) -> Assignment:
    if type not in self.assignment_defaults:
      raise ValueError('Type must be defined in assignment_defaults.')

    select_choice = 'Select from list'
    choices = [select_choice, 'Create new']
    index = menu(
      f'\nSelect existing {type} assignment or create new?', choices,
    )
    selection = choices[index]

    # Select an existing assignment.
    if selection == select_choice:
      index = menu(f'\nSelect {type} assignment:', list(map(str, collection)))
      print(f'\n{str(type).capitalize()}:', collection[index])
      return collection[index]

    # Create a new assignment.
    name = text(f'\nEnter name for new {type}: ', default=default)

    # Select an assignment group.
    groups = self.course_manager.get_assignment_groups(self.course)
    index = menu(f'\nSelect assignment group for new {type}:', list(map(str, groups)))

    data = {
      **self.assignment_defaults[type],
      **properties,
      'assignment_group_id': getattr(groups[index], 'id', ''),
      'name': name,
    }
    assignment = self.course.create_assignment(data)
    id = f' ({assignment.id})' if getattr(assignment, 'id', None) else ''
    print(f'\nCreated assignment {name}{id} in group {groups[index]}.')
    if url := getattr(assignment, 'html_url', None):
      print('View new assignment here:', url)
    print()

    self.invalidate_assignments()

    return assignment


  def get_outcome(self, id):
    if id not in self.outcomes:
      self.outcomes[id] = self.course_manager.canvas.get_outcome(id)
      print(f'Retrieved outcome {id}.')
    return self.outcomes[id]


  def upload(self, receptacle, mastery, grades):
    if not grades:
      print('No grades were processed. Please try again.')
      return

    print(f'Grades were processed for {len(grades)} students.')

    # Push scores to Canvas.
    print()
    push_notice = 'This will publish the mastery assignment. ' if not mastery.published else ''
    push_grades = confirm(f'Upload mastery scores to Canvas? {push_notice}')

    if not push_grades:
      print('Nothing left to do.')
      return

    # Publish mastery assignment.
    if not mastery.published:
      mastery.edit(assignment={
        'published': True,
      })
      print('Published mastery.')

    print()
    progress = mastery.submissions_bulk_update(grade_data=grades)
    pushed_receptacle = isinstance(self.receptacle_upload_progress, Progress)

    # Choose to post receptacle grades.
    post_receptacle_grades = (
      pushed_receptacle
      and mastery is not receptacle
      and confirm('Post receptacle grades to all students? ')
    )
    if post_receptacle_grades:
      self.await_upload_progress(self.receptacle_upload_progress)
      self.course_manager.post_grades(receptacle.id, graded_only=True)
      print('Posted receptacle grades.')
      print()

    # Choose to post mastery grades.
    post_mastery_grades = confirm('Post mastery grades to all students? ')
    if post_mastery_grades:
      self.await_upload_progress(progress)
      self.course_manager.post_grades(mastery.id, graded_only=True)
      print('Posted mastery grades.')

    print('\nDone.')


  def await_upload_progress(self, progress):
    if progress.workflow_state == 'complete':
      return

    print('\nWaiting for scores to upload to Canvas.', end='')
    while progress.query().workflow_state not in ['completed', 'failed']:
      print('.', end='')
      # Wait one second between queries.
      time.sleep(1)
    print()

    if progress.workflow_state == 'failed':
      print('Upload failed.')
      exit()

    print('Upload complete.')
    return
