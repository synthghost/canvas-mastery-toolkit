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
