import re
import pandas as pd
import canvas.grader

from os import path
from tkinter import Tk
from canvas import styles
from dateutil.tz import gettz
from canvasapi.quiz import Quiz
from dateutil.parser import parse
from bullet import Bullet, Input, YesNo
from tkinter.filedialog import askopenfilename

class GradescopeExamReviser(canvas.grader.Grader):

  def do(self) -> None:
    print('Now setting revisions for Gradescope exam')
    print()

    submissions = None

    # Repeat submissions selection until we have submissions.
    while not isinstance(submissions, pd.DataFrame) or submissions.empty:
      submissions = self.get_scores()

    # Find scores eligible for revisions.
    scores = self.get_applicable_scores(submissions)

    if scores.empty:
      print('No exam questions require revisions.')
      exit()

    print(f'Found {scores.columns.size} questions and {scores.index.size} students eligible for revisions.')
    print()

    if not YesNo(f'Make revisions? ', default='y', **styles.inputs).launch():
      print('Nothing left to do.')
      exit()

    exam = Input(f'\nEnter name for exam. This will be used as the prefix for all revision quizzes: ', **styles.inputs, strip=True).launch().strip(':')

    while not scores.empty:
      columns = scores.columns.values.tolist()
      _, index = Bullet(f'\nSelect question for revision:', **styles.bullets, choices=list(map(str, columns))).launch()
      print()
      self.process_question(exam, scores.pop(columns[index]))

    print('\nDone.')


  def get_scores(self):
    box = Tk()

    # Show only file window, not full GUI.
    box.withdraw()
    box.attributes('-topmost', True)
    data_path = path.abspath(askopenfilename(filetypes=[('CSV', '*.csv')]))
    box.destroy()

    data = pd.read_csv(data_path, header=0, index_col=3)

    # Validate submissions.
    if data.empty:
      print('That CSV file does not contain submissions. Please select another.')
      return None

    data.drop(data[data['Status'] == 'Missing'].index, inplace=True)

    students = {u.email: u.id for u in self.course.get_users(enrollment_type=['student']) if getattr(u, 'email', None)}

    # Convert emails to Canvas user IDs and rename the index to match.
    data.index = data.index.map(students).rename('user_id')

    return data


  def get_applicable_scores(self, submissions):
    filtered = submissions.filter(regex=r'^[0-9]+: (.*?) \([0-9.]+ pts\)$')
    return filtered[filtered == 2.0].dropna(axis='index', how='all').dropna(axis='columns', how='all')


  def process_question(self, exam, column):
    print(f'Question:', column.name)

    students = column.dropna().index.values.tolist()

    if not students:
      print('No students are eligible for revisions.')
      return

    # Create a new revision quiz.
    revision, question = self.get_revision(exam, column.name)

    # Make a section to assign the revision.
    section = self.course.create_course_section(course_section={
      'name': f'Revisions: {exam}; {question}',
    })
    id = f' ({section.id})' if getattr(section, 'id', None) else ''
    print(f'Created section {section.name}{id} for eligible students.')

    for student in students:
      # Assign student to section.
      self.course.enroll_user(student, enrollment={
        'course_section_id': section.id,
        'enrollment_state': 'active',
        'type': 'StudentEnrollment',
      })

    print()

    # Set revision due date.
    due_iso = None

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
        continue
      due_iso = due_zoned.isoformat(timespec='seconds')

    assignment = self.course.get_assignment(revision.assignment_id)
    assignment.create_override(assignment_override={
      'course_section_id': section.id,
      'due_at': due_iso,
    })
    assignment.edit(assignment={
      'only_visible_to_overrides': True,
    })

    print(f'\nAssigned revision to section {section.name}.')
    print()

    # Publish revision quiz.
    publish = YesNo(f'Publish revision quiz? ', default='y', **styles.inputs).launch()

    revision.edit(quiz={
      'only_visible_to_overrides': True,
      'published': publish,
    })

    if publish:
      print(f'Published revision {revision.title}.')


  def get_revision(self, exam: str, question: str) -> Quiz:
    name = self.parse_question_name(question)

    title = Input(f'\nEnter name for question: ', default=f'{exam} Revision: {name}' if name else '', **styles.inputs).launch()

    # Select an assignment group.
    groups = self.course_manager.get_assignment_groups(self.course)
    _, index = Bullet(f'\nSelect assignment group for revision quiz:', **styles.bullets, choices=list(map(str, groups))).launch()

    # Create revision.
    revision = self.course.create_quiz({
      'assignment_group_id': getattr(groups[index], 'id', ''),
      'description': f'Revision for {exam}, question {name}.' if name else '',
      'quiz_type': 'assignment',
      'shuffle_answers': False,
      'title': title,
    })

    # Add work question.
    revision.create_question(question={
      'question_name': 'Revised Work',
      'question_text': 'Upload your revised work. Be sure to follow the revision rules.',
      'question_type': 'file_upload_question',
      'points_possible': 1,
    })

    revision.edit(quiz={'points_possible': 1})

    id = f' ({revision.id})' if getattr(revision, 'id', None) else ''
    print(f'\nCreated revision quiz {title}{id} in group {groups[index]}.')
    if url := getattr(revision, 'html_url', None):
      print('View new quiz here:', url)
    print()

    return revision, name


  def parse_question_name(self, question: str) -> str:
    question_pattern = re.compile(r'^[0-9]+: (.*?) \([0-9.]+ pts\)$')
    name = match.group(1).strip() if (match := question_pattern.search(question)) else question
    parts = re.split(r'\[(.*?)\] ?', name)
    return parts[2] or parts[1] if len(parts) > 2 else name