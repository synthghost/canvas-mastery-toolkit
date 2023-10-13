import re
import math
import getpass
import keyring

from canvasapi import Canvas
from canvasapi.course import Course, Folder
from canvas.configcourse import ConfigCourse
from canvasapi.exceptions import Forbidden, InvalidAccessToken, ResourceDoesNotExist, Unauthorized

class CourseManager:

  def __init__(self, config: ConfigCourse) -> None:
    self.course = config
    self.config = self.course.manager

    if self.config.get('canvas_keyring_disable').lower() == 'true':
      return self._init_without_keyring()

    keyring_name = self.config.get('canvas_keyring_name')
    keyring_user = self.config.get('canvas_keyring_user')

    token = keyring.get_password(keyring_name, keyring_user)

    if token:
      try:
        self._connect(token)
        return
      except InvalidAccessToken:
        print('Invalid Canvas access token.')
        pass

    # Fall back to config value if possible, or ask the user for input otherwise.
    token = self.config.get('canvas_api_token') or getpass.getpass('Enter new Canvas access token:')

    try:
      self._connect(token)
      keyring.set_password(keyring_name, keyring_user, token)
      print('Access token saved.')
      return
    except InvalidAccessToken:
      raise KeyError('Invalid Canvas access token. Try again.')


  def get_course(self, course_id = None) -> Course:
    id = course_id or self.course.get('canvas_course_id')

    if not id:
      raise KeyError('Missing Canvas course ID (canvas_course_id).')

    try:
      return self.canvas.get_course(id)
    except (Forbidden, ResourceDoesNotExist, Unauthorized, TypeError):
      raise KeyError('Invalid Canvas course ID (canvas_course_id).')


  def get_folder(self, course = None, folder_id = None) -> Folder:
    id = folder_id or self.course.get('canvas_folder_id')

    if not id:
      raise KeyError('Missing Canvas folder ID (canvas_folder_id).')

    if course and not isinstance(course, Course):
      raise TypeError('Course argument must be of type canvasapi.Course.')

    try:
      return course.get_folder(id) if course else self.canvas.get_folder(id)
    except (Forbidden, ResourceDoesNotExist, Unauthorized, TypeError):
      raise KeyError('Invalid Canvas folder ID (canvas_folder_id).')


  def get_assignment_groups(self, course) -> list:
    if not isinstance(course, Course):
      raise TypeError('Course argument must be of type canvasapi.Course.')

    # Sort the groups by position.
    return sorted(course.get_assignment_groups(), key=lambda g: getattr(g, 'position', math.inf))


  def get_outcome_rubrics(self, course) -> list:
    if not isinstance(course, Course):
      raise TypeError('Course argument must be of type canvasapi.Course.')

    # Find course rubrics that follow the single-outcome-style naming
    # convention and have at least one criteria linked to an outcome.
    rubrics = [r for r in course.get_rubrics()
      if r.title.startswith('Outcome Rubric:')
        and any(x.get('learning_outcome_id', None) for x in r.data)
    ]

    # Sort the rubrics using natural numeric ordering (i.e. 2 before 10).
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    split_numbers = lambda r: ([convert(b) for b in re.split('([0-9]+)', getattr(r, 'title', ''))], r)
    return sorted(rubrics, key=split_numbers)


  def post_grades(self, assignment_id, graded_only = False) -> dict:
    response = self.canvas.graphql((
      'mutation PostGrades {postAssignmentGrades(input: {'
      f'assignmentId: {assignment_id}, gradedOnly: {str(graded_only).lower()}'
      '}) {progress {_id\nstate\n__typename}\n__typename} }'
    ))
    if response.get('errors'):
      print('Posting grades failed.')
    return response


  def _init_without_keyring(self) -> None:
    token = self.config.get('canvas_api_token')

    if not token:
      raise KeyError('Missing Canvas access token (canvas_api_token).')

    try:
      self._connect(token)
      return
    except InvalidAccessToken:
      raise KeyError('Invalid Canvas access token (canvas_api_token).')


  def _connect(self, token) -> None:
    canvas = Canvas(self.config.get('canvas_url').rstrip('/'), token)
    canvas.get_current_user()
    self.canvas = canvas
    print('Connected to Canvas.')
