import logging

from canvas import styles
from bullet import Bullet, Input, YesNo
from canvasapi.assignment import Assignment
from canvas.coursemanager import CourseManager

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


  def __init__(self) -> None:
    # Connect to Canvas course.
    self.course_manager = CourseManager()
    self.course_manager.set_logging(logging.DEBUG)
    self.course = self.course_manager.get_course()

    # Pre-load existing assignments.
    self.invalidate_assignments()
    self.get_assignments()

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
    mastery_same = YesNo('Use the same assignment for mastery? ', default='y', **styles.inputs).launch()
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
    selection, _ = Bullet(
      f'\nSelect existing {type} assignment or create new?', **styles.bullets, choices=[select_choice, 'Create new'],
    ).launch()

    # Select an existing assignment.
    if selection == select_choice:
      _, index = Bullet(f'\nSelect {type} assignment:', **styles.bullets, choices=list(map(str, collection))).launch()
      print(f'\n{str(type).capitalize()}:', collection[index])
      return collection[index]

    # Create a new assignment.
    name = Input(f'\nEnter name for new {type}: ', default=default, **styles.inputs).launch()

    # Select an assignment group.
    groups = self.course_manager.get_assignment_groups(self.course)
    _, index = Bullet(f'\nSelect assignment group for new {type}:', **styles.bullets, choices=list(map(str, groups))).launch()

    data = {
      **self.assignment_defaults[type],
      **properties,
      'assignment_group_id': getattr(groups[index], 'id', ''),
      'name': name,
    }
    assignment = self.course.create_assignment(data)
    id = f' ({assignment.id})' if getattr(assignment, 'id', None) else ''
    print(f'\nCreated assignment {name}{id} in group {groups[index]}.')
    print()

    self.invalidate_assignments()

    return assignment


  def upload(self, receptacle, mastery, grades):
    if not grades:
      print('No grades were processed. Please try again.')
      return

    print(f'Grades were processed for {len(grades)} students.')

    # Push scores to Canvas.
    print()
    push_notice = 'This will publish the mastery assignment. ' if not mastery.published else ''
    push_grades = YesNo(f'Upload mastery scores to Canvas? {push_notice}', default='y', **styles.inputs).launch()

    if not push_grades:
      print('Nothing left to do.')
      return

    # Publish mastery assignment.
    if not mastery.published:
      mastery.edit(assignment={
        'published': True,
      })
      print('Published mastery.')

    progress = mastery.submissions_bulk_update(grade_data=grades)
    print('Uploaded scores to Canvas. See progress here:', progress.url)

    # Choose to post receptacle grades.
    print()
    post_receptacle_grades = YesNo('Post receptacle grades to all students? ', default='y', **styles.inputs).launch()
    if post_receptacle_grades:
      self.course_manager.post_grades(receptacle.id, graded_only=True)
      print('Posted receptacle grades.')

    if mastery is not receptacle:
      # Choose to post mastery grades.
      print()
      post_mastery_grades = YesNo('Post mastery grades to all students? ', default='y', **styles.inputs).launch()
      if post_mastery_grades:
        self.course_manager.post_grades(mastery.id, graded_only=True)
        print('Posted mastery grades.')

    print('\nDone.')
