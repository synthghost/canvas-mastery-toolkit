from os import path
from canvas.cli import error, info, text
from configparser import ConfigParser
from canvas.configcourse import ConfigCourse

class ConfigManager:

  # Constants
  CORE = 'core'
  CONFIG_FILE = '.canvas-toolkit-config'

  config_path = path.join(path.expanduser('~'), CONFIG_FILE)

  def __init__(self) -> None:
    self.config = ConfigParser()

    # Read global config.
    self.config.read(self.config_path)


  def install(self) -> None:
    if path.isfile(self.config_path):
      info(f'Global configuration file already installed at {self.config_path}')
      return

    # Ask for Canvas URL.
    canvas_url = text('Enter Canvas base URL: ')

    self.config[self.CORE] = {
      # The institution's Canvas base URL.
      'canvas_url': canvas_url,

      # A name and username for system-wide keyring storage of
      # a Canvas API access token. Disabling the keyring forces
      # the application to use the canvas_api_token value below.
      'canvas_keyring_disable': False,
      'canvas_keyring_name': 'canvas_toolkit_api_token',
      'canvas_keyring_user': 'canvas',

      # A user-specific access token for the Canvas API. New
      # tokens can be generated in Canvas > Account > Settings.
      # Click "New Access Token" under Approved Integrations.
      'canvas_api_token': '',

      # A path to the directory where logs will be stored
      # and a log severity level, which can be one of:
      # CRITICAL, FATAL, ERROR, WARNING, INFO, DEBUG.
      'canvas_log_dir': path.expanduser('~'),
      'canvas_log_level': 'ERROR',
    }

    self.save()

    info(f'Generated global configuration file at {self.config_path}')


  def get(self, address: str) -> str:
    section, key = self.split_address(address)
    return self.config.get(section, key)


  def set(self, address: str, value: str) -> None:
    section, key = self.split_address(address)
    self.config.set(section, key, value)
    self.save()


  def get_courses(self) -> list[str]:
    return [section for section in self.config.sections()
      if section != self.CORE and '.' not in section]


  def get_course(self, name: str) -> ConfigCourse:
    sections = self.get_courses()
    section = sections[0] if name is None and len(sections) > 0 else name
    if not self.course_name_valid_and_exists(section):
      error(f'No course found for "{section}".')
      exit()
    return ConfigCourse(self, section)


  def add_course(self, name: str, canvas_id: str, folder_id: str) -> None:
    if self.course_name_valid_and_exists(name):
      error(f'Course "{name}" already exists. Try a different name.')
      exit()

    self.config[name] = {
      # A unique numeric identifier for the course of interest on
      # Canvas. Can usually be found in the course's Canvas URL.
      'canvas_course_id': canvas_id,

      # A unique numeric identifier for the folder on Canvas in which
      # to store uploaded figures. Can possibly be found on Canvas,
      # or by calling CourseManager().get_course().get_folders() to
      # get a list of Folder objects, each with an 'id' property.
      'canvas_folder_id': folder_id or '',
    }

    self.save()

    # Add revision questions.
    course = ConfigCourse(self, name)
    course.add_revision_questions()

    info(f'Added course {name} ({canvas_id}).')


  def remove_course(self, name: str) -> None:
    if not self.course_name_valid_and_exists(name):
      error(f'No course found for "{name}".')
      exit()

    self.config.remove_section(name)

    self.save()

    course = ConfigCourse(self, name)
    course.remove_revision_questions()

    info(f'Removed course {name}.')


  def save(self) -> None:
    with open(self.config_path, 'w') as file:
      self.config.write(file)


  def split_address(self, address: str) -> (str, str):
    if '.' not in address:
      return self.CORE, address
    return address.rsplit('.', 1)


  def course_name_valid_and_exists(self, name: str) -> bool:
    if name.lower() == self.CORE:
      error(f'Cannot use "{self.CORE}" as a course name.')
      exit()
    if '.' in name:
      error('Course name cannot contain "." character.')
      exit()
    return self.config.has_section(name)
