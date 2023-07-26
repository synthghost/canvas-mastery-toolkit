from os import getenv, path
from dotenv import load_dotenv

base_path = path.abspath(path.dirname(__file__))

load_dotenv(path.join(base_path, '.env'))

config = {
  # The institution's Canvas URL.
  'canvas_url': 'https://canvas.cornell.edu',

  # Keyring configuration for system-wide storage of the Canvas
  # access token. Disabling the keyring forces the application
  # to use the CANVAS_API_TOKEN environment value. The default
  # keyring name and user ("canvas_test_token1" and "canvas")
  # match those used in D.Savransky's cornellGrading package.
  'canvas_keyring_disable': getenv('CANVAS_KEYRING_DISABLE', 'false'),
  'canvas_keyring_name': getenv('CANVAS_KEYRING_NAME', 'canvas_test_token1'),
  'canvas_keyring_user': getenv('CANVAS_KEYRING_USER', 'canvas'),

  # A user-specific access token for the Canvas API.
  # New tokens can be generated in Canvas > Account > Settings.
  # Click "New Access Token" under Approved Integrations.
  'canvas_api_token': getenv('CANVAS_API_TOKEN'),

  # The absolute path where Canvas API logs will be saved.
  'canvas_logs_dir': path.join(base_path, 'logs'),

  # A unique numeric identifier for the course of interest on
  # Canvas. Can usually be found in the course's Canvas URL.
  'canvas_course_id': getenv('CANVAS_COURSE_ID'),

  # A unique numeric identifier for the folder on Canvas in which
  # to store uploaded figures. Can possibly be found on Canvas,
  # or by calling CourseManager().get_course().get_folders() to
  # get a list of Folder objects, each with an 'id' property.
  'canvas_folder_id': getenv('CANVAS_FOLDER_ID'),
}
