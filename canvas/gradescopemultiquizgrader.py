import re
import pandas as pd

from os import path
from tkinter import Tk
from tkinter.filedialog import askopenfilenames
from canvas.gradescopeexamgrader import GradescopeExamGrader

class GradescopeMultiQuizGrader(GradescopeExamGrader):

  def do(self) -> None:
    print('Now grading Gradescope quiz (multiple)')

    receptacle = None
    submissions = None

    # Repeat receptacle or submissions selection until we have submissions.
    while not isinstance(submissions, pd.DataFrame) or submissions.empty:
      receptacle = self.get_receptacle()
      submissions = self.get_all_scores()

    # Push scores to receptacle?
    self.push_grades(receptacle, submissions)

    mastery, rubric = self.get_rubric(receptacle, submissions)

    grades = {}

    # Calculate rubric scores.
    for user_id, submission in submissions.iterrows():
      score = {
        'posted_grade': submission['Total Score'],
        'rubric_assessment': {},
      }

      for criterion in rubric:
        question = next(m['question'] for m in self.matches.values() if m['outcome'] == criterion['description'])
        try:
          rating = next(r for r in criterion['ratings'] if r['points'] == submission.loc[question])
        except StopIteration:
          print('No rating match for score:', submission.loc[question])
          continue

        score['rubric_assessment'][criterion['id']] = {
          'rating_id': rating['id'],
          'points': rating['points'],
        }

      grades[user_id] = score

    self.upload(receptacle, mastery, grades)


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
      print('Selected files contain duplicate student emails. Please correct and try again.')
      data_paths = set()
      return None

    return submissions


  def get_scores(self, data_paths: set) -> list:
    data = []

    # Retrieve users.
    users = {user.email: user.id
      for user in self.course.get_users(enrollment_type=['student'])
      if getattr(user, 'email', None)}

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

      df_users = pd.DataFrame.from_dict(users, orient='index', columns=['user_id'])

      # Map emails to Canvas user IDs and set the index to match.
      df_mapped = df_data.join(df_users, on='Email', how='inner').set_index('user_id')

      if df_mapped.index.has_duplicates:
        print(f'WARNING: Duplicate student emails in {data_path}')
        continue

      data.append(df_mapped)

    return data


  def normalize_column(self, name):
    # Only affect numbered question columns.
    if not re.match(r'^[0-9]+: (.*?) \([0-9.]+ pts\)$', name):
      return name

    # Change any question number to a constant.
    return re.sub(r'^[0-9]+:', '0:', name)
