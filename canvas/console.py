import click
import functools

from canvas.cli import error, info
from canvas import ConfigManager, GradingManager

config_manager = ConfigManager()
grading_manager = GradingManager()


###########################################################################
# General commands
###########################################################################

@click.group
@click.version_option(package_name='canvas-mastery-toolkit')
def cli():
  """Canvas Mastery Toolkit CLI."""
  pass


@cli.command
@click.argument('address')
@click.argument('value', required=False)
def config(address, value = None):
  """Retrieve or store configuration values.

  \b
  ADDRESS is the configuration item address as "section.key".
  VALUE is the configuration item value (optional).
  """
  if value is not None:
    return config_manager.set(address, value)
  try:
    info(config_manager.get(address))
  except Exception:
    error(f'No entry found for "{address}".')


@cli.command
def install():
  """Perform initial package installation."""
  config_manager.install()


###########################################################################
# Course commands
###########################################################################

@cli.group
def courses():
  """Manage Canvas course entries."""
  pass


@courses.command
@click.argument('course_name')
@click.argument('course_id', type=int)
@click.argument('folder_id', type=int, required=False)
def add(course_name, course_id, folder_id):
  """Add a Canvas course entry.

  \b
  COURSE_NAME is the name to give the course entry.
  COURSE_ID is the Canvas ID for the course.
  FOLDER_ID is the Canvas ID for a file upload folder (optional).
  """
  config_manager.add_course(course_name, course_id, folder_id)


@courses.command
def list():
  """List Canvas course entries."""
  info(', '.join(config_manager.get_courses()))


@courses.command
@click.argument('course_name')
def remove(course_name):
  """Remove a Canvas course entry.

  COURSE_NAME is the name of a Canvas course entry."""
  config_manager.remove_course(course_name)


###########################################################################
# Mastery commands
###########################################################################

def course_name_argument(func):
  func.__doc__ += '\n\nCOURSE_NAME is the name of a Canvas course entry.'
  @click.argument('course_name')
  @functools.wraps(func)
  def wrapper(*args, **kwargs):
    course_name = kwargs.pop('course_name', None)
    if course_name:
      grading_manager.use(config_manager.get_course(course_name))
    return func(*args, **kwargs)
  return wrapper


@cli.command
@course_name_argument
def assign():
  """Assign checkpoint opportunities for given Canvas course."""
  grading_manager.start_opportunities()


@cli.command
@course_name_argument
def export():
  """Export mastery gradebook for given Canvas course."""
  grading_manager.export_learning_mastery_gradebook()


@cli.command
@course_name_argument
def grade():
  """Perform grading for given Canvas course."""
  grading_manager.start_grading()


@cli.command
@course_name_argument
def revise():
  """Assign revisions for given Canvas course."""
  grading_manager.start_revisions()


@cli.command
@course_name_argument
def rubrics():
  """Generate mastery rubrics for given Canvas course."""
  grading_manager.generate_single_outcome_rubrics()


@cli.command
@course_name_argument
def sds():
  """Set accommodations for given Canvas course."""
  grading_manager.start_accommodations()
