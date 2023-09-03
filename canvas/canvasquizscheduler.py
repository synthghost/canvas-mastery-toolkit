import re
import math
import numpy as np
import pandas as pd
import canvas.grader

from os import path
from tkinter import Tk
from bullet import Bullet
from canvas import styles
from canvas.bullet import YesNo
from canvasapi.assignment import Assignment
from tkinter.filedialog import askopenfilename

class CanvasQuizScheduler(canvas.grader.Grader):

  def do(self) -> None:
    print('Now scheduling accommodations for Canvas quiz')

    quiz = self.get_quiz()

    accommodations = None

    # Repeat accommodation selection until we have accommodations.
    while not isinstance(accommodations, pd.DataFrame) or accommodations.empty:
      accommodations = self.get_accommodations()

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

    # Publish quiz.
    if not quiz.published and YesNo(f'Publish quiz? ', default='y', **styles.inputs).launch():
      quiz.edit(quiz={
        'published': True,
      })
      print(f'Published quiz {quiz.title}.')

    print('\nDone.')


  def get_quiz(self) -> Assignment:
    # Select an existing assignment.
    quizzes = sorted([q for q in self.course.get_quizzes()
      if q.quiz_type == 'assignment' and getattr(q, 'time_limit', None)],
      key=lambda q: getattr(q, 'title', None))

    if not quizzes:
      print('\nNo time-limited quizzes found! Cannot proceed.')
      exit()

    _, index = Bullet(f'\nSelect quiz:', **styles.bullets, choices=list(map(str, quizzes))).launch()
    print('\nQuiz:', quizzes[index])
    print()

    return quizzes[index]


  def get_accommodations(self):
    box = Tk()

    # Show only file window, not full GUI.
    box.withdraw()
    box.attributes('-topmost', True)
    data_path = path.abspath(askopenfilename(filetypes=[('CSV', '*.csv')]))
    box.destroy()

    data = pd.read_csv(data_path, header=0, index_col=2)

    # Validate accommodations.
    if data.empty:
      print('That CSV file does not contain data. Please select another.')
      return None

    # Drop the test student.
    data.drop(data[data['School ID'] == 'X889900'].index, inplace=True)

    students = {u.email: u.id for u in self.course.get_users(enrollment_type=['student']) if getattr(u, 'email', None)}

    # Convert emails to Canvas user IDs and rename the index to match.
    data.index = data.index.map(students).rename('user_id')

    # Remove unmapped rows (students not in the course roster).
    return data[data.index.notnull()]


  def get_applicable_accommodations(self, accommodations: pd.DataFrame):
    filtered = accommodations.filter(regex=r'^Exams- ?[0-9]{1,3}\%-')
    return filtered[filtered == 'Yes'].dropna(axis='index', how='all').dropna(axis='columns', how='all')
