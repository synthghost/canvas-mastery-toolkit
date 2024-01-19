import canvas.console as console

from canvas import ConfigManager
from canvas.cli import confirm, menu, number, text

class App(object):
  def __init__(self) -> None:
    self.config_manager = ConfigManager()

  def start(self) -> None:
    choices = [
      'assign: \t Assign checkpoint opportunities to students.',
      'config: \t View or modify configuration values.',
      'courses: \t Manage Canvas course entries.',
      'export: \t Export a Learning Mastery gradebook as a CSV file.',
      'grade: \t Grade quizzes or exams from Gradescope or Canvas.',
      'install: \t Perform one-time application installation.',
      'revise: \t Create and assign revisions for quizzes or exams.',
      'rubrics: \t Generate single-outcome Learning Mastery rubrics.',
      'sds: \t Set Canvas quiz time extensions from SDS CSV file.',
    ]

    index = menu('\nWhat would you like to do?', choices)
    print()

    method = choices[index].split(':')[0]

    if hasattr(self, method):
      getattr(self, method)()
      return

    self.run(method)


  def config(self) -> None:
    address = text('The configuration item address as "section.key": ')

    try:
      current = self.config_manager.get(address)
      print(current)
    except Exception:
      print(f'No entry found for "{address}".')
      return

    print()
    if not confirm('Update value? ', default='n'):
      return

    value = text('\nThe configuration item value: ', default=current)

    return self.config_manager.set(address, value)


  def courses(self) -> None:
    courses = self.config_manager.get_courses()

    entries = '\n'.join(courses) if courses else 'No course entries yet.'
    print(f'Canvas course entries:\n{entries}')

    choices = [
      'Add a new course entry',
      'Remove a course entry',
    ]

    index = menu('\nWhat would you like to do?', choices)
    print()

    methods = ['add_course', 'remove_course']

    getattr(self, methods[index])()


  def add_course(self):
    name = text('The name to give the new course entry: ')
    id = number('The Canvas ID for the course: ', type=int)

    self.config_manager.add_course(name, id, None)


  def remove_course(self):
    course = text('The course to remove, as listed above: ')

    self.config_manager.remove_course(course)


  def install(self) -> None:
    console.install()


  def run(self, method: str) -> None:
    courses = self.config_manager.get_courses()

    index = menu('Choose a Canvas course:', courses)

    getattr(console, method)([courses[index]])
