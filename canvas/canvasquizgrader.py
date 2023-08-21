import canvas.grader

from canvas import styles
from bullet import Bullet, YesNo
from canvas.bullet import Numbers
from canvasapi.assignment import Assignment

class CanvasQuizGrader(canvas.grader.Grader):

  def do(self) -> None:
    print('Now grading Canvas quiz')

    quiz = None
    submissions = None

    # Repeat quiz or submissions selection until we have submissions.
    while not submissions:
      quiz = self.get_quiz()
      submissions = self.get_scores(quiz)

    mastery, rubric = self.get_rubric(quiz)

    grades = {}

    # Map scores to rubric.
    score_map = self.map_scores(quiz, rubric)

    # Calculate rubric scores.
    for submission in submissions:
      score = {
        'posted_grade': submission.score,
        'rubric_assessment': {},
      }

      try:
        points = next((v for k, v in score_map.items() if k <= submission.score))
        rating = next(r for r in rubric['ratings'] if r['points'] == points)
      except StopIteration:
        print('No rating match for score:', submission.score)
        continue

      score['rubric_assessment'][rubric['id']] = {
        'rating_id': rating['id'],
        'points': rating['points'],
      }

      grades[submission.user_id] = score

    self.upload(quiz, mastery, grades)


  def get_quiz(self) -> Assignment:
    # Select an existing assignment.
    quizzes = [a for a in self.get_assignments()
      if a.published and a.is_quiz_assignment and a.grading_type == 'points']

    _, index = Bullet(f'\nSelect quiz:', **styles.bullets, choices=list(map(str, quizzes))).launch()
    print('\nQuiz:', quizzes[index])
    print()

    return quizzes[index]


  def get_scores(self, receptacle: Assignment):
    submissions = [s for s in receptacle.get_submissions()
      if getattr(s, 'score', None) is not None and s.graded_at]

    # Validate submissions.
    if not submissions:
      print('That quiz has no submissions! Please select another.')
      return

    print(f'Found {len(submissions)} submissions.')

    return submissions


  def get_rubric(self, receptacle: Assignment):
    mastery = self.get_mastery(receptacle)

    settings = getattr(mastery, 'rubric_settings', {})
    rubric = getattr(mastery, 'rubric', None)

    # Replace rubric if has rubric?
    replace_notice = f'The mastery assignment has rubric "{settings.get("title")}". Replace rubric? '
    replace_rubric = rubric and YesNo(replace_notice, default='n', **styles.inputs).launch()
    print()

    # Use or select rubric.
    if not rubric or replace_rubric:
      rubric = self.apply_rubric(mastery)

    return mastery, rubric[0]


  def apply_rubric(self, mastery: Assignment):
    # Show list of pre-made rubrics.
    rubrics = self.course_manager.get_outcome_rubrics(self.course)

    if not rubrics:
      print('No rubrics found! Cannot proceed.')
      exit()

    # Select pre-made rubric.
    _, index = Bullet(f'\nSelect a rubric:', **styles.bullets, choices=list(map(str, rubrics))).launch()
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
    max_points = float(getattr(receptacle, 'points_possible', rubric['points']))

    print(f'Assignment "{receptacle.name}" has a maximum score of {max_points} points.\n')

    ratings = [r for r in rubric['ratings'] if r.get('points') is not None]
    ratings_sorted = sorted(ratings, key=lambda r: float(r['points']), reverse=True)

    score_map = {}

    for r in ratings_sorted:
      text = f"{r['points']} {r['description']}"

      # Skip manually mapping a rating of zero.
      if r['points'] <= 0:
        print(f'Automatically set minimum point threshold for rating "{text}" to zero.')
        score_map[0] = r['points']
        break

      # When no ratings have been assigned, ask the user for the minimum
      # max-score bound, which could be less than or equal to the max score.
      if len(score_map) == 0:
        while (value := self.ask_score_threshold(text, max_points)) > max_points or value <= 0:
          print(f'The threshold must be positive and no greater than the maximum score, {max_points}.\n')
        score_map[value] = r['points']
        continue

      # Otherwise, repeatedly ask the user for the next lower bound,
      # which must be less than the previously defined minimum bound.
      bound = min(score_map.keys())
      while (value := self.ask_score_threshold(text)) >= bound or value < 0:
        print(f'The threshold must be positive and less than the previous one, {bound}.\n')

      score_map[value] = r['points']

      if value == 0:
        print('Remaining ratings will not be applied.')
        break

    print()

    return dict(sorted(score_map.items(), reverse=True))


  def ask_score_threshold(self, rating, default = None):
    return Numbers(
      f'Enter minimum point threshold for rating "{rating}": ', **styles.inputs,
    ).launch(default=default)
