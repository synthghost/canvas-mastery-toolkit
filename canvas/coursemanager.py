import re
import math
import getpass
import keyring
import logging

from os import path
from config import config
from canvasapi import Canvas
from canvasapi.course import Course, Folder
from canvasapi.exceptions import Forbidden, InvalidAccessToken, ResourceDoesNotExist, Unauthorized

class CourseManager:

  def __init__(self) -> None:
    if config['canvas_keyring_disable'].lower() == 'true':
      return self._init_without_keyring()

    keyring_name = config['canvas_keyring_name']
    keyring_user = config['canvas_keyring_user']

    token = keyring.get_password(keyring_name, keyring_user)

    if token:
      try:
        self._connect(token)
        return
      except InvalidAccessToken:
        print('Invalid Canvas access token.')
        pass

    # Fall back to environmental variable, if possible, or ask the user for input otherwise.
    token = config['canvas_api_token'] or getpass.getpass('Enter new Canvas access token:')

    try:
      self._connect(token)
      keyring.set_password(keyring_name, keyring_user, token)
      print('Access token saved.')
      return
    except InvalidAccessToken:
      raise KeyError('Invalid Canvas access token. Try again.')


  def set_logging(self, level: int = logging.WARNING) -> None:
    logger = logging.getLogger('canvasapi')
    handler = logging.FileHandler(path.join(config['canvas_logs_dir'], 'canvas.log'))
    formatter = logging.Formatter('%(asctime)s %(levelname)s [%(name)s] %(message)s')

    handler.setLevel(level)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(level)


  def get_course(self, course_id = None) -> Course:
    id = course_id or config['canvas_course_id']

    if not id:
      raise KeyError('Missing Canvas course ID (CANVAS_COURSE_ID).')

    try:
      return self.canvas.get_course(id)
    except (Forbidden, ResourceDoesNotExist, Unauthorized, TypeError):
      raise KeyError('Invalid Canvas course ID (CANVAS_COURSE_ID).')


  def get_folder(self, course = None, folder_id = None) -> Folder:
    id = folder_id or config['canvas_folder_id']

    if not id:
      raise KeyError('Missing Canvas folder ID (CANVAS_FOLDER_ID).')

    if course and not isinstance(course, Course):
      raise TypeError('Course argument must be of type canvasapi.Course.')

    try:
      return course.get_folder(id) if course else self.canvas.get_folder(id)
    except (Forbidden, ResourceDoesNotExist, Unauthorized, TypeError):
      raise KeyError('Invalid Canvas folder ID (CANVAS_FOLDER_ID).')


  def get_assignment_groups(self, course) -> list:
    if not isinstance(course, Course):
      raise TypeError('Course argument must be of type canvasapi.Course.')

    groups = list(course.get_assignment_groups())

    # Sort the groups by position.
    return sorted(groups, key=lambda g: getattr(g, 'position', math.inf))


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
    token = config['canvas_api_token']

    if not token:
      raise KeyError('Missing Canvas access token (CANVAS_API_TOKEN).')

    try:
      self._connect(token)
      return
    except InvalidAccessToken:
      raise KeyError('Invalid Canvas access token (CANVAS_API_TOKEN).')


  def _connect(self, token) -> None:
    canvas = Canvas(config['canvas_url'], token)
    canvas.get_current_user()
    self.canvas = canvas
    print('Connected to Canvas.')
