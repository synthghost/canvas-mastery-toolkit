import logging

from bullet import Bullet
from canvas import styles
from canvas.coursemanager import CourseManager

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


  def generate_single_outcome_rubrics(self) -> None:
    self.course_manager = CourseManager()
    self.course_manager.set_logging(logging.DEBUG)
    course = self.course_manager.get_course()
    print('Course:', course)
    print()

    rubrics = []
    outcome_links = list(course.get_all_outcome_links_in_context())

    for link in outcome_links:
      if not hasattr(link, 'outcome'): continue

      outcome = self.get_outcome(link.outcome['id'])
      rubrics.append(course.create_rubric(rubric={
        'title': f'Outcome Rubric: {getattr(outcome, "title", None)}',
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

    print('\nCreated', len(rubrics), 'rubrics')


  def get_outcome(self, id):
    if id not in self.outcomes:
      print('Retrieving outcome', id)
      self.outcomes[id] = self.course_manager.canvas.get_outcome(id)
    return self.outcomes[id]
