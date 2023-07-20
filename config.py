from dotenv import load_dotenv
from os import getenv as env, path

load_dotenv()

config = {
  # The institution's Canvas URL.
  'canvas_url': 'https://canvas.cornell.edu',

  # Keyring configuration for system-wide storage of the Canvas
  # access token. Disabling the keyring forces the application
  # to use the CANVAS_API_TOKEN environment value. The default
  # keyring name and user ("canvas_test_token1" and "canvas")
  # match those used in D.Savransky's cornellGrading package.
  'canvas_keyring_disable': env('CANVAS_KEYRING_DISABLE', 'false'),
  'canvas_keyring_name': env('CANVAS_KEYRING_NAME', 'canvas_test_token1'),
  'canvas_keyring_user': env('CANVAS_KEYRING_USER', 'canvas'),

  # A user-specific access token for the Canvas API.
  # New tokens can be generated in Canvas > Account > Settings.
  # Click "New Access Token" under Approved Integrations.
  'canvas_api_token': env('CANVAS_API_TOKEN'),

  # The absolute path where Canvas API logs will be saved.
  'canvas_logs_dir': path.join(path.abspath(path.dirname(__file__)), 'logs'),

  # A unique numeric identifier for the course of interest on
  # Canvas. Can usually be found in the course's Canvas URL.
  'canvas_course_id': env('CANVAS_COURSE_ID'),
}
