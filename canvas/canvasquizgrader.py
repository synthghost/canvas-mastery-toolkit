import canvas.grader

from canvas import styles
from bullet import Bullet, YesNo
from canvasapi.assignment import Assignment

class CanvasQuizGrader(canvas.grader.Grader):

  def do(self) -> None:
    print('Now grading Canvas quiz')

    receptacle = None
    submissions = None

    # Repeat receptacle or submissions selection until we have submissions.
    while not submissions:
      receptacle = self.get_quiz()
      submissions = self.get_scores(receptacle)

    mastery, rubric = self.get_rubric(receptacle)

    grades = {}

    # Map scores to rubric.
    self.map_scores(receptacle, rubric)

    # Calculate rubric scores.
    for submission in submissions:
      score = {
        'posted_grade': submission.score,
        'rubric_assessment': {},
      }

      criterion = rubric[0]

      try:
        points = next((v for k, v in self.score_map.items() if k <= submission.score))
        rating = next(r for r in criterion['ratings'] if r['points'] == points)
      except StopIteration:
        print('No rating match for score:', submission.score)
        continue

      score['rubric_assessment'][criterion['id']] = {
        'rating_id': rating['id'],
        'points': rating['points'],
      }

      grades[submission.user_id] = score

    self.upload(receptacle, mastery, grades)


  def get_quiz(self) -> Assignment:
    # Select an existing assignment.
    quizzes = [a for a in self.get_assignments()
      if a.published and a.is_quiz_assignment and a.grading_type == 'points']

    _, index = Bullet(f'\nSelect quiz:', **styles.bullets, choices=[str(c) for c in quizzes]).launch()
    print('\nQuiz:', quizzes[index])
    print()

    return quizzes[index]


  def get_scores(self, receptacle: Assignment):
    submissions = [s for s in receptacle.get_submissions() if getattr(s, 'score', None) is not None and s.graded_at]

    # Validate submissions.
    if not submissions:
      print('That quiz has no submissions! Please select another.')
      return

    print(f'Found {len(submissions)} submissions.')

    return submissions


  def get_rubric(self, receptacle: Assignment):
    mastery, _ = self.get_mastery(receptacle)

    settings = getattr(mastery, 'rubric_settings', {})
    rubric = getattr(mastery, 'rubric', None)

    # Replace rubric if has rubric?
    replace_notice = f'The mastery assignment has rubric "{settings.get("title")}". Replace rubric? '
    replace_rubric = rubric and YesNo(replace_notice, default='n', **styles.inputs).launch()
    print()

    # Use or select rubric.
    if not rubric or replace_rubric:
      rubric = self.apply_rubric(mastery)

    return mastery, rubric


  def apply_rubric(self, mastery: Assignment):
    # Show list of pre-made rubrics.
    rubrics = self.course_manager.get_outcome_rubrics(self.course)

    if not rubrics:
      print('No rubrics found! Cannot proceed.')
      exit()

    # Select pre-made rubric.
    _, index = Bullet(f'\nSelect a rubric:', **styles.bullets, choices=[str(r) for r in rubrics]).launch()
    print('\nRubric:', rubrics[index])
    rubric = rubrics[index]

    # Apply rubric, overwriting existing rubrics on the assignment.
    self.course.create_rubric_association(rubric_association={
      'rubric_id': rubric.id,
      'association_id': mastery.id,
      'association_type': 'Assignment',
      'hide_outcome_results': False,
      'hide_points': False,
      'purpose': 'grading',
      'use_for_grading': False,
    })
    print('Applied rubric:', getattr(rubric, 'title', None))

    return rubric.data


  def map_scores(self, receptacle: Assignment, rubric):
    max_points = int(getattr(receptacle, 'points_possible', rubric[0]['points']))

    print('\nMapping scores onto a maximum of', max_points, 'points')
    print()

    ratings = [r for r in rubric[0]['ratings'] if r.get('points') is not None]
    ratings_sorted = sorted(ratings, key=lambda r: int(r['points']), reverse=True)

    used_ratings = []
    score_map = {0: 0}

    for r in ratings_sorted:
      # List the yet-unmapped possible scores in descending order.
      values = range(min(used_ratings, default=max_points + 1) - 1, -1, -1)

      if not r['points'] or len(values) <= 1:
        break

      _, index = Bullet(f'Select minimum point bound for rating "{r["points"]} {r["description"]}":', **styles.bullets, choices=list(map(str, values))).launch()
      used_ratings.append(values[index])
      score_map[values[index]] = r['points']
      print()

    self.score_map = dict(sorted(score_map.items(), reverse=True))
