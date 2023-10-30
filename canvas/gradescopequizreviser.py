import canvas.grader

from canvas import styles
from string import Template
from dateutil.tz import gettz
from canvas.bullet import YesNo
from canvasapi.quiz import Quiz
from bullet import Bullet, Input
from dateutil.parser import parse
from canvasapi.assignment import Assignment
from canvas.configmanager import ConfigManager

class GradescopeQuizReviser(canvas.grader.Grader):

  def do(self) -> None:
    print('Now setting revisions for Gradescope quiz')

    receptacle = None
    submissions = None

    # Repeat receptacle or submissions selection until we have submissions.
    while not submissions:
      receptacle = self.get_receptacle()
      submissions = self.get_scores(receptacle)

    # Find students eligible for revisions.
    students = self.get_applicable_students(submissions)

    if not students:
      print('No students are eligible for revisions.')
      exit()

    print(f'Found {len(students)} students eligible for revisions.')
    print()

    if not YesNo(f'Make a revision? ', default='y', **styles.inputs).launch():
      print('Nothing left to do.')
      exit()

    # Create a new revision quiz.
    revision = self.get_revision(receptacle)

    due_iso = None

    # Set revision due date.
    while not due_iso:
      due = Input(f'Enter due date for revision (mm/dd/yyyy hh:mm:ss): ', **styles.inputs).launch()
      try:
        due_parsed = parse(due, ignoretz=True)
      except Exception:
        print('Could not parse due date! Try again.')
        print()
        continue
      due_zoned = due_parsed.replace(tzinfo=gettz('America/New_York'))
      due_human = due_zoned.strftime('%m/%d/%Y at %H:%M:%S')
      if not YesNo(f'Due date will be {due_human}. Ok? ', default='y', **styles.inputs).launch():
        print()
        continue
      due_iso = due_zoned.isoformat(timespec='seconds')

    assignment = self.course.get_assignment(revision.assignment_id)
    assignment.create_override(assignment_override={
      'due_at': due_iso,
      'lock_at': due_iso,
      'student_ids': students,
    })
    assignment.edit(assignment={
      'only_visible_to_overrides': True,
    })

    print(f'\nAssigned revision to {len(students)} students.')
    print()

    # Publish revision quiz.
    publish = YesNo(f'Publish revision quiz? ', default='y', **styles.inputs).launch()

    revision.edit(quiz={
      'only_visible_to_overrides': True,
      'published': publish,
    })

    if publish:
      print('Published revision.')

    print('\nDone.')


  def get_receptacle(self) -> Assignment:
    collection = [a for a in self.get_assignments()
      if a.grading_type == 'points' and a.submission_types == ['none'] and not a.is_quiz_assignment]

    _, index = Bullet(f'\nSelect receptacle assignment:', **styles.bullets, choices=list(map(str, collection))).launch()
    print(f'\nReceptacle:', collection[index])
    return collection[index]


  def get_scores(self, receptacle: Assignment):
    submissions = [s for s in receptacle.get_submissions()
      if getattr(s, 'score', None) is not None and s.graded_at]

    # Validate submissions.
    if not submissions:
      print('That quiz has no submissions! Please select another.')
      return

    print(f'Found {len(submissions)} submissions.')

    return submissions


  def get_applicable_students(self, submissions):
    return [s.user_id for s in submissions if float(s.score) == 2.0]


  def get_revision(self, receptacle: Assignment) -> Quiz:
    name = getattr(receptacle, 'name', None)
    url = getattr(receptacle, 'html_url', None)

    title = Input(f'\nEnter name for revision quiz: ', default=f'{name} Revision' if name else '', **styles.inputs).launch()

    # Select an assignment group.
    groups = self.course_manager.get_assignment_groups(self.course)
    _, index = Bullet(f'\nSelect assignment group for revision quiz:', **styles.bullets, choices=list(map(str, groups))).launch()
    print()

    # Prepare questions.
    questions = [self.parse_question_tokens(q, {'assignment': name})
      for q in self.config.get_revision_questions()]

    texts = f'\n{styles.tab}'.join([f'{i}. {q["question_text"]}' for i, q in enumerate(questions, 1)])

    # Confirm revision question text.
    confirm = YesNo(f'The revision quiz questions will be:\n{styles.tab}{texts}\nOk? ', default='y', **styles.inputs).launch()
    if not confirm:
      print(f'\nPlease update the configured revision questions in {ConfigManager.CONFIG_FILE}, then run again.')
      exit()

    # Create revision.
    revision = self.course.create_quiz({
      'assignment_group_id': getattr(groups[index], 'id', ''),
      'description': f'Revision for <a href="{url}">{name}</a>.' if name and url else '',
      'quiz_type': 'assignment',
      'shuffle_answers': False,
      'title': title,
    })

    points = []

    # Add questions.
    for question in questions:
      revision.create_question(question=question)
      points.append(float(question.get('points_possible', 0)))

    revision.edit(quiz={'points_possible': sum(points)})

    id = f' ({revision.id})' if getattr(revision, 'id', None) else ''
    print(f'\nCreated revision quiz {title}{id} in group {groups[index]}.')
    if url := getattr(revision, 'html_url', None):
      print('View new quiz here:', url)
    print()

    return revision


  def parse_question_tokens(self, question: dict, tokens: dict) -> dict:
    return {key: Template(value).safe_substitute(**tokens)
      for key, value in question.items()}
