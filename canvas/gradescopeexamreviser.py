import re
import pandas as pd
import canvas.grader

from os import path
from tkinter import Tk
from canvas import styles
from string import Template
from dateutil.tz import gettz
from canvasapi.quiz import Quiz
from dateutil.parser import parse
from canvas.cli import confirm, menu, text
from canvas.configmanager import ConfigManager
from tkinter.filedialog import askopenfilename

class GradescopeExamReviser(canvas.grader.Grader):

  due_date = None

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

    if not confirm('Make revisions? '):
      print('Nothing left to do.')
      exit()

    print()
    exam = text(
      'Enter name for exam. This will be used as the prefix for all revision quizzes: ', strip=True,
    ).strip(':')

    while not scores.empty:
      columns = scores.columns.values.tolist()
      index = menu('\nSelect question for revision:', list(map(str, columns)))
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

    # Read CSV data without assigning an index column.
    df_data = pd.read_csv(data_path, header=0, index_col=False)

    # Validate submissions.
    if df_data.empty:
      print('That CSV file does not contain data. Please select another.')
      return None

    # Drop missing records.
    df_data.drop(df_data[df_data['Status'] == 'Missing'].index, inplace=True)

    # Retrieve users.
    users = {user.email: user.id
      for user in self.course.get_users(enrollment_type=['student'])
      if getattr(user, 'email', None)}

    df_users = pd.DataFrame.from_dict(users, orient='index', columns=['user_id'])

    # Map emails to Canvas user IDs and set the index to match.
    df_mapped = df_data.join(df_users, on='Email', how='inner').set_index('user_id')

    if df_mapped.index.has_duplicates:
      print('That CSV file contains duplicate student emails. Please correct and try again.')
      return None

    return df_mapped


  def get_applicable_scores(self, submissions):
    filtered = submissions.filter(regex=r'^[0-9]+: (.*?) \([0-9.]+ pts\)$')
    return filtered[filtered == 2.0].dropna(axis='index', how='all').dropna(axis='columns', how='all')


  def process_question(self, exam, column):
    print('Question:', re.sub(r'^[0-9]+: ', '', str(column.name)))

    students = column.dropna().index.values.tolist()

    if not students:
      print('No students are eligible for revisions.')
      return

    # Create a new revision quiz.
    revision = self.get_revision(exam, column.name)

    # Set revision due date.
    due_iso = None

    due_previous = self.due_date.strftime('%m/%d/%Y at %H:%M:%S') if self.due_date else None
    if due_previous and confirm(f'Use previous due date, {due_previous}? '):
      due_iso = self.due_date.isoformat(timespec='seconds')

    while not due_iso:
      due = text('Enter due date for revision (mm/dd/yyyy hh:mm:ss): ')
      try:
        due_parsed = parse(due, ignoretz=True)
      except Exception:
        print('Could not parse due date! Try again.')
        print()
        continue
      due_zoned = due_parsed.replace(tzinfo=gettz('America/New_York'))
      due_human = due_zoned.strftime('%m/%d/%Y at %H:%M:%S')
      if not confirm(f'Due date will be {due_human}. Ok? '):
        print()
        continue
      due_iso = due_zoned.isoformat(timespec='seconds')
      self.due_date = due_zoned

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
    publish = confirm('Publish revision quiz? ')

    revision.edit(quiz={
      'only_visible_to_overrides': True,
      'published': publish,
    })

    if publish:
      print(f'Published revision {revision.title}.')


  def get_revision(self, exam: str, question_name: str) -> Quiz:
    name = self.parse_question_name(question_name)

    title = text('\nEnter name for question: ', default=f'{exam} Revision: {name}' if name else '')

    # Select an assignment group.
    groups = self.course_manager.get_assignment_groups(self.course)
    index = menu('\nSelect assignment group for revision quiz:', list(map(str, groups)))
    print()

    # Prepare questions.
    questions = [self.parse_question_tokens(q, {'assignment': exam})
      for q in self.config.get_revision_questions()]

    texts = f'\n{styles.tab}'.join([f'{i}. {q["question_text"]}' for i, q in enumerate(questions, 1)])

    # Confirm revision question text.
    if not confirm(f'The revision quiz questions will be:\n{styles.tab}{texts}\nOk? '):
      print(f'\nPlease update the configured revision questions in {ConfigManager.CONFIG_FILE}, then run again.')
      exit()

    # Create revision.
    revision = self.course.create_quiz({
      'assignment_group_id': getattr(groups[index], 'id', ''),
      'description': f'Revision for {exam}, question {name}.' if name else '',
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


  def parse_question_name(self, question: str) -> str:
    question_pattern = re.compile(r'^[0-9]+: (.*?) \([0-9.]+ pts\)$')
    name = match.group(1).strip() if (match := question_pattern.search(question)) else question
    parts = re.split(r'\[(.*?)\] ?', name)
    return parts[2] or parts[1] if len(parts) > 2 else name


  def parse_question_tokens(self, question: dict, tokens: dict) -> dict:
    return {key: Template(value).safe_substitute(**tokens)
      for key, value in question.items()}
