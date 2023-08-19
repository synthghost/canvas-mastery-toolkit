import re
import logging
import pandas as pd

from os import path
from tkinter import Tk
from bullet import Bullet
from canvas import styles
from canvas.coursemanager import CourseManager
from tkinter.filedialog import asksaveasfilename

graders = []

class GradingManager(object):

  def __init__(self) -> None:
    self.outcomes = {}


  def start(self) -> None:
    _, grading_index = Bullet('\nWhat kind of grading?', **styles.bullets,
      choices=['Gradescope Quiz', 'Canvas Quiz', 'Gradescope Exam'],
    ).launch()
    print()

    grader = graders[grading_index]()
    grader.do()


  def get_course(self):
    self.course_manager = CourseManager()
    self.course_manager.set_logging(logging.DEBUG)
    course = self.course_manager.get_course()
    print('Course:', course)
    print()
    return course


  def generate_single_outcome_rubrics(self) -> None:
    course = self.get_course()

    rubrics = []

    for link in course.get_all_outcome_links_in_context():
      if not hasattr(link, 'outcome'): continue

      outcome = self.get_outcome(link.outcome['id'])
      rubrics.append(course.create_rubric(rubric={
        'title': f'Outcome Rubric: {getattr(outcome, "display_name", None)}',
        'points_possible': outcome.mastery_points,
        'free_form_criterion_comments': False,
        'criteria': {
          0: {
            'learning_outcome_id': outcome.id,
            'description': outcome.title,
            'criterion_use_range': False,
            'mastery_points': outcome.mastery_points,
            'points': outcome.points_possible,
            'ratings': {i: rating for i, rating in enumerate(outcome.ratings)},
          },
        },
      }, rubric_association={
        'association_id': course.id,
        'association_type': 'Course',
        'hide_outcome_results': False,
        'hide_points': False,
        'purpose': 'bookmark',
        'use_for_grading': False,
      }))

    print('\nCreated', len(rubrics), 'rubrics.')


  def export_learning_mastery_gradebook(self):
    print()
    course = self.get_course()

    # Get all course outcomes and shorten their names if possible.
    outcome_pattern = re.compile(r'\[(.*?)\]')
    outcome_column = lambda t: f'{parts[0]}[{parts[1]}]' if (parts := outcome_pattern.split(t, maxsplit=1)) else t
    outcomes = {outcome['id']: outcome_column(outcome.get('title', ''))
      for link in course.get_all_outcome_links_in_context()
        if (outcome := getattr(link, 'outcome'))}

    print(f'Retrieved {len(outcomes)} outcomes.')

    # Find all point-based assignments, including quizzes, since some may
    # have had mastery rubrics applied as part of the grading process.
    assignments = {a.id: a.name for a in course.get_assignments() if a.grading_type == 'points'}

    print(f'Retrieved {len(assignments)} assignments.')

    data = [(
      outcomes.get(int(o.links['learning_outcome']), o.links['learning_outcome']),
      assignments.get(int(o.links['alignment'].replace('assignment_', '')), o.links['alignment']),
      int(o.links['user']),
      o.score,
    ) for o in course.get_outcome_results()]

    print(f'Retrieved {len(data)} results.')

    # An opportunity is any instance of a rubric criterion that is linked to a
    # learning outcome. Since there will be multiple assignments and questions
    # within assignments that will score against any given outcome, each of that
    # outcome's rubric instances represent an opportunity to achieve mastery.
    # Opportunity format = outcome_name: opportunity_name

    columns = ['outcome', 'assignment', 'student', 'score']

    # Construct a dataframe and add columns for opportunity counts.
    df_flat = pd.DataFrame(data, columns=columns)
    df_pivot = df_flat.pivot(columns=['outcome', 'assignment'], index='student', values='score')
    opportunity_counts = df_pivot.groupby(axis='columns', level=0, sort=False).count()
    df_pivot.columns = df_pivot.columns.map(': '.join)
    df_counts = df_pivot.join(opportunity_counts)

    print('Constructed dataframe.')

    # Sort the dataframe's columns using natural numeric ordering (i.e. 2 before 10).
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    split_numbers = lambda c: tuple(list(map(convert, l)) for l in c.str.split(re.compile('([0-9]+)')))
    df_sorted = df_counts.sort_index(axis='columns', key=split_numbers)

    # Make the count columns stand out. This has to be done after sorting to retain order.
    df_sorted.columns = [c if ':' in c else f'{c} Opportunities' for c in df_sorted.columns]

    print('Sorted columns.')

    students = {s.id: {
      'Student': s.sortable_name, # student.name
      'ID': s.id,
      'SIS User ID': s.sis_user_id,
      'SIS Login ID': s.login_id,
      # Section as well?
    } for s in course.get_users(enrollment_type=['student']) if getattr(s, 'email', None)}

    # Map student details onto the sorted dataframe.
    df_students = pd.DataFrame.from_dict(students, orient='index')
    df_gradebook = df_students.join(df_sorted)

    print(f'Added {len(students)} students.')

    box = Tk()
    # Show only file window, not full GUI.
    box.withdraw()
    box.attributes('-topmost', True)
    save_path = path.abspath(asksaveasfilename(initialfile='gradebook', defaultextension='.csv'))
    box.destroy()

    # Save dataframe to the selected path.
    df_gradebook.to_csv(save_path, index=False, encoding='utf-8')

    print('Saved gradebook to:', save_path)


  def get_outcome(self, id):
    if id not in self.outcomes:
      print('Retrieving outcome', id)
      self.outcomes[id] = self.course_manager.canvas.get_outcome(id)
    return self.outcomes[id]
