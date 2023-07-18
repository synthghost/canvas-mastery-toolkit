from os import path
from dotenv import dotenv_values

env = dotenv_values()

config = {
  'base_path': path.abspath(path.dirname(__file__)),
  'canvas_api_url': 'https://canvas.cornell.edu',
  'canvas_api_token': env['CANVAS_API_TOKEN'],
  'canvas_course_id': env['CANVAS_COURSE_ID'],
}
