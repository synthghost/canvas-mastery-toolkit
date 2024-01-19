import canvas.grader

from canvas.cli import confirm, menu
from canvasapi.assignment import Assignment

class GradescopeQuizGrader(canvas.grader.Grader):

  def do(self) -> None:
    print('Now grading Gradescope quiz')

    receptacle = None
    submissions = None

    # Repeat receptacle or submissions selection until we have submissions.
    while not submissions:
      receptacle = self.get_receptacle()
      submissions = self.get_scores(receptacle)

    mastery, rubric = self.get_rubric(receptacle)

    grades = {}

    # Calculate rubric scores.
    for submission in submissions:
      score = {
        'posted_grade': submission.score,
        'rubric_assessment': {},
      }

      try:
        rating = next(r for r in rubric['ratings'] if r['points'] == submission.score)
      except StopIteration:
        print('No rating match for score:', submission.score)
        continue

      score['rubric_assessment'][rubric['id']] = {
        'rating_id': rating['id'],
        'points': rating['points'],
      }

      grades[submission.user_id] = score

    self.upload(receptacle, mastery, grades)


  def get_receptacle(self) -> Assignment:
    # Select or create receptacle.
    receptacle = self.select_or_create(
      [a for a in self.get_assignments()
        if a.grading_type == 'points' and a.submission_types == ['none'] and not a.is_quiz_assignment],
      'receptacle',
    )

    # Publish receptacle assignment.
    if not receptacle.published:
      if not confirm('Publish receptacle? This is needed to sync Gradescope. '):
        print('\nCannot proceed without syncing Gradescope.')
        exit()

      receptacle.edit(assignment={
        'published': True,
      })
      print('Published receptacle.')

    input('\nPlease go to Gradescope and click "Post Grades" to sync scores to Canvas. Press <Enter> when syncing complete.')
    print()

    return receptacle


  def get_scores(self, receptacle: Assignment):
    submissions = [s for s in receptacle.get_submissions()
      if getattr(s, 'score', None) is not None and s.graded_at]

    # Validate submissions.
    if not submissions:
      print('That assignment has no submissions! Please select another.')
      return

    print(f'Found {len(submissions)} submissions.')

    return submissions


  def get_rubric(self, receptacle: Assignment):
    mastery = self.get_mastery(receptacle)

    settings = getattr(mastery, 'rubric_settings', {})
    rubric = getattr(mastery, 'rubric', None)

    # Replace rubric if has rubric?
    replace_notice = f'The mastery assignment has rubric "{settings.get("title")}". Replace rubric? '
    replace_rubric = rubric and confirm(replace_notice, default='n')
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
    index = menu('\nSelect a rubric:', list(map(str, rubrics)))
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
