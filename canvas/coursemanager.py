from config import config
from canvasapi import Canvas
from canvasapi.course import Course
from canvasapi.exceptions import Forbidden, InvalidAccessToken, ResourceDoesNotExist, Unauthorized

class CourseManager:

  def __init__(self) -> None:
    token = config['canvas_api_token']

    if not token:
      raise KeyError('Missing Canvas API token. Please define CANVAS_API_TOKEN in the environment.')

    try:
      canvas = Canvas(config['canvas_api_url'], token)
      canvas.get_current_user()
    except InvalidAccessToken:
      raise KeyError('Invalid Canvas API token. Please check CANVAS_API_TOKEN in the environment.')

    self.canvas = canvas


  def getCourse(self) -> Course:
    id = config['canvas_course_id']

    if not id:
      raise KeyError('Missing Canvas course ID. Please define CANVAS_COURSE_ID in the environment.')

    try:
      course = self.canvas.get_course(id)
    except (Forbidden, ResourceDoesNotExist, Unauthorized, TypeError):
      raise KeyError('Invalid Canvas course ID. Please check CANVAS_COURSE_ID in the environment.')

    return course
