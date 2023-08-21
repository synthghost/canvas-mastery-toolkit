import re
import canvas.grader
import pandas as pd

from os import path
from tkinter import Tk
from canvas import styles
from bullet import Bullet, YesNo
from canvasapi.assignment import Assignment
from tkinter.filedialog import askopenfilename

class GradescopeExamGrader(canvas.grader.Grader):

  def __init__(self) -> None:
    super().__init__()

    self.outcomes = {}


  def do(self) -> None:
    print('Now grading Gradescope exam')

    receptacle = None
    submissions = None

    # Repeat receptacle or submissions selection until we have submissions.
    while not isinstance(submissions, pd.DataFrame) or submissions.empty:
      receptacle = self.get_receptacle()
      submissions = self.get_scores()

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


  def get_receptacle(self) -> Assignment:
    # Select or create receptacle.
    return self.select_or_create(
      [a for a in self.get_assignments()
        if a.grading_type == 'points' and a.submission_types == ['none'] and not a.is_quiz_assignment],
      type='receptacle',
    )


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


  def push_grades(self, receptacle: Assignment, submissions) -> None:
    push_notice = 'This will publish the receptacle assignment. ' if not receptacle.published else ''
    push_grades = YesNo(f'Upload receptacle scores to Canvas? {push_notice}', default='n', **styles.inputs).launch()
    if not push_grades:
      return

    # Publish receptacle assignment.
    receptacle.edit(assignment={
      'points_possible': submissions['Max Points'].iloc[0],
      'published': True,
    })
    print('Published receptacle.')

    grades = submissions['Total Score'].rename('posted_grade').to_frame().to_dict('index')

    # Update assignment.
    progress = receptacle.submissions_bulk_update(grade_data=grades)

    print('May take a few minutes to show up. See progress here:', progress.url)


  def get_rubric(self, receptacle: Assignment, submissions):
    mastery = self.get_mastery(receptacle)

    # Always overwrite existing rubrics for Gradescope exams.
    rubric = self.apply_rubric(mastery, submissions)

    return mastery, rubric


  def apply_rubric(self, mastery: Assignment, submissions):
    # Find question columns given the format "1: Question Text (3.0 pts)".
    question_pattern = re.compile(r'^[0-9]+: (.*?) \([0-9.]+ pts\)$')
    token_pattern = re.compile(r'\[(.*?)\]')

    tokenize = lambda text: token.group(1).strip() if (token := token_pattern.search(text)) else text
    questions = {tokenize(match.group(1).strip()): column
      for column in submissions.columns.values.tolist()
        if (match := question_pattern.search(column))}

    outcomes_unsorted = {match.group(1).strip(): outcome
      for link in self.course.get_all_outcome_links_in_context()
        if (outcome := getattr(link, 'outcome'))
          and (match := token_pattern.search(outcome.get('title', '')))}

    # Sort the outcomes using natural numeric ordering (i.e. 2 before 10).
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    split_numbers = lambda o: tuple(convert(s) for s in re.split('([0-9]+)', o[1]['title']))
    outcomes = dict(sorted(outcomes_unsorted.items(), key=split_numbers))

    matches = {}

    # Find a match for each question so none get missed.
    for id, column in questions.items():
      if id in outcomes:
        print(f'Question "{column}" will map to outcome "{outcomes[id]["title"]}"')
        matches[id] = {
          'question': column,
          'outcome': outcomes[id]['title'],
        }
        continue

      # Make dictionary numerically subscriptable, yielding [(key, value), ...].
      choices = list(outcomes.items())

      _, index = Bullet(
        f'\nQuestion "{column}" does not have a match. Select an outcome:', **styles.bullets,
        choices=[str(c[1]['title']) for c in choices],
      ).launch()

      key = choices[index][0]
      print(f'\nQuestion "{column}" will map to outcome "{outcomes[key]["title"]}"')

      matches[key] = {
        'question': column,
        'outcome': outcomes[key]['title'],
      }

    print()

    self.matches = matches

    criteria = {}
    points = 0

    for i, id in enumerate(matches.keys()):
      if not outcomes[id].get('id'):
        continue

      outcome = self.get_outcome(outcomes[id]['id'])
      points += outcome.points_possible
      # The Canvas API requires the criteria object to be an indexed list.
      criteria[i] = {
        'learning_outcome_id': outcome.id,
        'description': outcome.title,
        'criterion_use_range': False,
        'mastery_points': outcome.mastery_points,
        'points': outcome.points_possible,
        # The Canvas API requires the ratings object to be an indexed list.
        'ratings': {j: rating for j, rating in enumerate(outcome.ratings)},
      }

    # Apply rubric, overwriting existing rubrics on the assignment.
    rubric = self.course.create_rubric(rubric={
      'title': f'{mastery.name} Rubric',
      'points_possible': points,
      'free_form_criterion_comments': False,
      'skip_updating_points_possible': False,
      'criteria': criteria,
    }, rubric_association={
      'association_id': mastery.id,
      'association_type': 'Assignment',
      'hide_outcome_results': False,
      'hide_points': False,
      'purpose': 'grading',
      'use_for_grading': False,
    })

    rubric = rubric['rubric']
    print('Applied rubric:', getattr(rubric, 'title', None))

    return rubric.data


  def get_outcome(self, id):
    if id not in self.outcomes:
      self.outcomes[id] = self.course_manager.canvas.get_outcome(id)
      print(f'Retrieved outcome {id}.')
    return self.outcomes[id]
