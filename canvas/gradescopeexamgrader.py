import re
import pandas as pd
import canvas.grader

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
        match = next(m['question'] for m in self.matches.values() if m['outcome'] == criterion['description'])
        try:
          rating = next(r for r in criterion['ratings'] if r['points'] == submission.loc[match])
        except StopIteration:
          print('No rating match for score:', submission.loc[match])
          continue

        score['rubric_assessment'][criterion['id']] = {
          'rating_id': rating['id'],
          'points': rating['points'],
        }

      grades[user_id] = score

    self.upload(receptacle, mastery, grades)


  def get_receptacle(self) -> Assignment:
    # Select or create receptacle.
    receptacle = self.select_or_create(
      [a for a in self.get_assignments()
        if a.grading_type == 'points' and a.submission_types == ['none'] and not a.is_quiz_assignment],
      type='receptacle',
    )

    return receptacle


  def get_scores(self):
    box = Tk()

    # Show only file window, not full GUI.
    box.withdraw()
    box.attributes('-topmost', True)
    data_path = path.normpath(askopenfilename(filetypes=[('CSV files', '*.csv')]))
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
    print('Published receptacle')

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
    columns = submissions.columns.values.tolist()
    pattern = re.compile(r'^[0-9]+: (.+) \([0-9.]+ pts\)$')
    questions = list(filter(pattern.search, columns))
    questions_keyed = {pattern.match(q).group(1).strip(): q for q in questions}

    outcome_links = list(self.course.get_all_outcome_links_in_context())
    outcomes = [link.outcome for link in outcome_links if hasattr(link, 'outcome')]
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    outcomes_tupled = [([convert(c) for c in re.split('^([0-9]+)', o.get('title'))], o) for o in outcomes]
    outcomes_sorted = [o for _, o in sorted(outcomes_tupled)]
    outcomes_keyed = {re.split('^[0-9]+\.', o.get('title'))[1].strip(): o for o in outcomes_sorted}

    matches = {}

    for k, q in questions_keyed.items():
      if k in outcomes_keyed and outcomes_keyed[k].get('title'):
        print('Question', q, 'will map to outcome:', outcomes_keyed[k].get('title'))
        matches[k] = {
          'question': q,
          'outcome': outcomes_keyed[k]['title'],
        }
        continue

      _, index = Bullet(
        f'\nQuestion {q} does not have a match. Select an outcome:', **styles.bullets,
        choices=[str(o.get('title')) for o in outcomes_sorted],
      ).launch()
      l = re.split('^[0-9]+\.', outcomes_sorted[index]['title'])[1].strip()
      matches[l] = {
        'question': q,
        'outcome': outcomes_keyed[l]['title'],
      }
      print()

    self.matches = matches

    criteria = {}
    points = 0

    for i, match in enumerate(matches.keys()):
      if not outcomes_keyed[match].get('id'): continue
      outcome = self.get_outcome(outcomes_keyed[match]['id'])
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
      print('Retrieving outcome', id)
      self.outcomes[id] = self.course_manager.canvas.get_outcome(id)
    return self.outcomes[id]
