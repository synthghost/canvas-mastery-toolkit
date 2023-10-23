import re
import math
import numpy as np
import pandas as pd
import canvas.grader

from os import path
from tkinter import Tk
from canvas import styles
from dateutil.tz import gettz
from canvasapi.quiz import Quiz
from collections import Counter
from bullet import Bullet, Input
from dateutil.parser import parse
from canvas.bullet import Numbers, YesNo
from canvasapi.exceptions import BadRequest
from tkinter.filedialog import askopenfilename

class CanvasQuizScheduler(canvas.grader.Grader):

  def do_accommodations(self) -> None:
    print('Now setting accommodations for timed Canvas quizzes')

    quiz = self.get_quiz(check_time_limits=True)

    self.assign_extra_time(quiz)

    # Publish quiz.
    if not quiz.published and YesNo(f'Publish quiz? ', default='y', **styles.inputs).launch():
      quiz.edit(quiz={
        'published': True,
      })
      print(f'Published quiz {quiz.title}.')
      print()

    print('Done.')


  def do_checkpoints(self) -> None:
    print('Now assigning Canvas checkpoint opportunities')

    quiz = self.get_quiz(check_unpublished=True)

    outcome = self.get_learning_outcome()

    checks = Numbers(
      f'Enter number of checks needed for outcome mastery: ', **styles.inputs,
    ).launch(default=getattr(outcome, 'calculation_int', None))
    print()

    # Find students with full scores on outcome opportunities.
    scored_users = [int(o.links['user'])
      for o in self.course.get_outcome_results()
        if o.links['learning_outcome'] == str(getattr(outcome, 'id', None))
          and o.score and int(o.score) >= 3]

    # Find students who meet the previously specified number of checks.
    mastered_users = [user for user, count in Counter(scored_users).items() if count >= checks]

    students = self.course.get_users(enrollment_type=['student'])

    eligible_students = [s for s in students
      if getattr(s, 'email', None) and s.id not in mastered_users]

    print(f'Found {len(eligible_students)} students eligible for the checkpoint.')
    print()

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

    # Assign the quiz to eligible students.
    assignment = self.course.get_assignment(quiz.assignment_id)

    try:
      assignment.create_override(assignment_override={
        'due_at': due_iso,
        'lock_at': due_iso,
        'student_ids': [s.id for s in eligible_students],
      })
    except BadRequest:
      print('\nCannot make student-specific assignments if overrides already exist.')
      exit()

    assignment.edit(assignment={
      'only_visible_to_overrides': True,
    })

    print(f'\nAssigned checkpoint to {len(eligible_students)} students.')
    print()

    if getattr(quiz, 'time_limit', None):
      self.assign_extra_time(quiz, eligible_students)

    # Publish quiz.
    publish = YesNo(f'Publish quiz? ', default='y', **styles.inputs).launch()

    quiz.edit(quiz={
      'only_visible_to_overrides': True,
      'published': publish,
    })

    if publish:
      print(f'Published quiz {quiz.title}.')

    print('\nDone.')


  def assign_extra_time(self, quiz: Quiz, students: list = None) -> None:
    accommodations = None

    # Repeat accommodation selection until we have accommodations.
    while not isinstance(accommodations, pd.DataFrame) or accommodations.empty:
      accommodations = self.get_accommodations(students)

    # Find time accommodations.
    times = self.get_applicable_accommodations(accommodations)

    if times.empty:
      print('No students have time accommodations.')
      exit()

    print(f'Found {times.columns.size} accommodations and {times.index.size} eligible students.')

    # Cast column names to scalar multipliers.
    multipliers = times.columns.map(lambda c: float(re.search(r'([0-9]{1,3})\%', c).group(1).strip()) / 100)

    # Apply multipliers to dataframe, then merge by row and by column.
    times[:] = np.where(times.notnull(), multipliers, times)
    df_max = times.groupby(times.index, axis='index').max()
    sr_max = df_max.max(axis='columns')

    extensions = [{
        'user_id': math.floor(user_id),
        'extra_time': math.ceil(quiz.time_limit * time),
      } for user_id, time in sr_max.to_dict().items()]

    quiz.set_extensions(extensions)

    print(f'\nAssigned extensions to {len(extensions)} students.')
    print()


  def get_quiz(self, check_time_limits = False, check_unpublished = False) -> Quiz:
    passes_limit = lambda q: getattr(q, 'time_limit', None) if check_time_limits else True
    passes_unpublished = lambda q: not q.published if check_unpublished else True

    # Select an existing assignment.
    quizzes = sorted([q for q in self.course.get_quizzes()
      if q.quiz_type == 'assignment' and passes_limit(q) and passes_unpublished(q)],
      key=lambda q: getattr(q, 'title', None))

    if not quizzes:
      limited = 'time-limited ' if check_time_limits else ''
      print(f'\nNo {limited}quizzes found! Cannot proceed.')
      exit()

    _, index = Bullet(f'\nSelect quiz:', **styles.bullets, choices=list(map(str, quizzes))).launch()
    print('\nQuiz:', quizzes[index])
    print()

    return quizzes[index]


  def get_learning_outcome(self):
    outcomes_unsorted = {outcome['id']: outcome.get('title', outcome.get('display_name', ''))
      for link in self.course.get_all_outcome_links_in_context()
        if (outcome := getattr(link, 'outcome'))}

    if not outcomes_unsorted:
      print('No learning outcomes found! Cannot proceed.')
      exit()

    # Sort the outcomes using natural numeric ordering (i.e. 2 before 10).
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    split_numbers = lambda o: tuple(convert(s) for s in re.split('([0-9]+)', o[1]))
    outcomes = dict(sorted(outcomes_unsorted.items(), key=split_numbers))

    # Make dictionary numerically subscriptable, yielding [(key, value), ...].
    choices = list(outcomes.items())

    # Select outcome.
    _, index = Bullet(
      f'Select a learning outcome:', **styles.bullets,
      choices=[str(c[1]) for c in choices],
    ).launch()

    outcome = self.get_outcome(choices[index][0])
    print('\nLearning Outcome:', getattr(outcome, 'title', None))
    print()

    return outcome


  def get_accommodations(self, students = None):
    print('Select a CSV file of accommodations.')

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
      print('That CSV file does not contain submissions. Please select another.')
      return None

    # Drop the test student.
    df_data.drop(df_data[df_data['School ID'] == 'X889900'].index, inplace=True)

    users = students or self.course.get_users(enrollment_type=['student'])

    # Retrieve users.
    users = {user.email: user.id for user in users if getattr(user, 'email', None)}

    df_users = pd.DataFrame.from_dict(users, orient='index', columns=['user_id'])

    # Map emails to Canvas user IDs and set the index to match.
    return df_data.join(df_users, on='Email', how='inner').set_index('user_id')


  def get_applicable_accommodations(self, accommodations: pd.DataFrame):
    filtered = accommodations.filter(regex=r'^Exams- ?[0-9]{1,3}\%-')
    return filtered[filtered == 'Yes'].dropna(axis='index', how='all').dropna(axis='columns', how='all')
