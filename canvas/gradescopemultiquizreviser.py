import re
import pandas as pd

from os import path
from tkinter import Tk
from canvas.cli import confirm, menu, text
from tkinter.filedialog import askopenfilenames
from canvas.gradescopeexamreviser import GradescopeExamReviser

class GradescopeMultiQuizReviser(GradescopeExamReviser):

  def do(self) -> None:
    print('Now setting revisions for Gradescope quiz (multiple)')
    print()

    submissions = None

    # Repeat submissions selection until we have submissions.
    while not isinstance(submissions, pd.DataFrame) or submissions.empty:
      submissions = self.get_all_scores()

    # Find scores eligible for revisions.
    scores = self.get_applicable_scores(submissions)

    if scores.empty:
      print('No quiz questions require revisions.')
      exit()

    print(f'Found {scores.columns.size} questions and {scores.index.size} students eligible for revisions.')
    print()

    if not confirm('Make revisions? '):
      print('Nothing left to do.')
      exit()

    print()
    quiz = text(
      'Enter a name for the quiz. This will be used as the prefix for all revision quizzes: ', strip=True,
    ).strip(':')

    while not scores.empty:
      columns = scores.columns.values.tolist()
      index = menu('\nSelect question for revision:', self.get_question_names(columns))
      print()
      self.process_question(quiz, scores.pop(columns[index]))

    print('\nDone.')


  def get_all_scores(self):
    box = Tk()

    # Show only file window, not full GUI.
    box.withdraw()
    box.attributes('-topmost', True)
    files = askopenfilenames(filetypes=[('CSV', '*.csv')])
    box.destroy()

    if not files:
      print('Selection canceled! Cannot proceed.')
      exit()

    data_paths = set([path.abspath(file) for file in files])

    data = self.get_scores(data_paths)

    if not data:
      print('Insufficient data. Please select other files.')
      return None

    try:
      # Concatenate submissions
      submissions = pd.concat(data)
    except Exception:
      print('Provided data is incompatible for merging. Please try again.')
      data_paths = set()
      return None

    if submissions.index.has_duplicates:
      print(f'Selected files contain duplicate student emails. Please correct and try again.')
      data_paths = set()
      return None

    return submissions


  def get_scores(self, data_paths: set) -> list:
    data = []

    for data_path in data_paths:
      # Read CSV data without assigning an index column.
      df_data = pd.read_csv(data_path, header=0, index_col=False)

      # Validate submissions.
      if df_data.empty:
        print(f'WARNING: No data found in {data_path}')
        continue

      # Drop missing records.
      df_data.drop(df_data[df_data['Status'] == 'Missing'].index, inplace=True)

      # Normalize columns to allow merging.
      df_data.rename(columns=self.normalize_column, inplace=True)

      # Retrieve users.
      users = {user.email: user.id
        for user in self.course.get_users(enrollment_type=['student'])
        if getattr(user, 'email', None)}

      df_users = pd.DataFrame.from_dict(users, orient='index', columns=['user_id'])

      # Map emails to Canvas user IDs and set the index to match.
      df_mapped = df_data.join(df_users, on='Email', how='inner').set_index('user_id')

      if df_mapped.index.has_duplicates:
        print(f'WARNING: Duplicate student emails in {data_path}')
        continue

      data.append(df_mapped)

    return data


  def get_question_names(self, columns):
    # Remove the question number from each column.
    return list(map(lambda c: re.sub(r'^[0-9]+: ', '', str(c)), columns))


  def normalize_column(self, name):
    # Only affect numbered question columns.
    if not re.match(r'^[0-9]+: (.*?) \([0-9.]+ pts\)$', name):
      return name

    # Change any question number to a constant.
    return re.sub(r'^[0-9]+:', '0:', name)
