import re
import json
import uuid
import click
import urllib.parse

from os import path
from canvas import ConfigManager, CourseManager

###########################################################################
# QUIZ GENERATOR
# To be executed from MATLAB.
###########################################################################


# File handling
def validate_path(abs_path):
  if abs_path and not path.exists(abs_path):
    raise FileNotFoundError('No file found at {}'.format(abs_path))


def validate_figure_paths(questions):
  for q in questions:
    validate_path(q.get('figure_path'))
    if 'answers' in q:
      [validate_path(a.get('figure_path')) for a in q['answers']]


# Latex conversion
def latexrepl(match):
  if isinstance(match, re.Match):
    match = match.groups()[0]

  # Double-encode URLs to match Canvas behavior.
  encoded = urllib.parse.quote(urllib.parse.quote(match))

  # Generate Canvas equation image HTML.
  return f'<img class="equation_image" title="{match}" src="/equation_images/{encoded}?scale=1" alt="LaTeX: {match}" data-equation-content="{match}" data-ignore-a11y-check="" />'


# Parse LaTeX strings enclosed by $.
def latex(text):
  p = re.compile('\${1,2}(.*?)\${1,2}')

  return p.sub(latexrepl, text)


def upload_figure(folder, abs_path, dry_run = False):
    if not folder or not abs_path:
      return ''
    if dry_run:
      return f'<fig="{abs_path}" />'
    is_uploaded, response = folder.upload(abs_path)
    if not is_uploaded:
      raise IOError(f'Upload failed for figure {abs_path}')
    print(f'Figure {response["filename"]} uploaded.')
    url = response['preview_url'].split('?')[0].replace('file_', '')
    return f'<img id="{response["id"]}" src="{url}" alt="" />'


# Gather command line arguments from MATLAB.
@click.command
@click.argument('course_name')
@click.argument('data_path', type=click.Path(exists=True, dir_okay=False))
@click.option('--delete-quiz', is_flag=True, help='Delete the quiz after uploading questions.')
@click.option('--dry-run', is_flag=True, help='Test process but do not upload to Canvas.')
@click.option('--question-limit', type=int, default=-1, help='Limit on how many questions to add.')
def cli(course_name, data_path, delete_quiz, dry_run, question_limit):
  """Canvas Mastery Toolkit CLI.

  MATLAB Quiz Generator Sidecar.

  \b
  COURSE_NAME is the name of a Canvas course entry.
  DATA_PATH is the absolute path to a .json data file."""
  config = ConfigManager()

  # Connect to Canvas course.
  manager = CourseManager(config.get_course(course_name))
  course = manager.get_course()

  limit = f'a limit of {question_limit}' if question_limit > 0 else 'no limit'
  print(f'Using file {data_path} with {limit}')
  print('Course:', course)
  if dry_run:
    print('*** DRY RUN ***')

  # Read the generated data as JSON.
  with open(data_path, 'r') as file:
    data = json.load(file)

  if not 'questions' in data:
    print('No questions to process.')
    exit()

  has_figures = data.get('has_figures') == True or data.get('has_figures') == 'true'

  print('Figures:', has_figures)

  folder = manager.get_folder() if has_figures else None

  print('Folder:', folder)

  # Validate that all figures are valid files.
  if has_figures:
    validate_figure_paths(data['questions'])

  # Create a blank quiz.
  if not dry_run:
    quiz = course.create_quiz({
      'title': data.get('title') or f'Generated Quiz {uuid.uuid4()}',
      'description': data.get('description', ''),
      'quiz_type': 'assignment',
      'shuffle_answers': False,
    })

    print('Quiz:', quiz)

  # Keep running total of the quiz points.
  total_points = 0

  # Iterate over data to prepare for Canvas API.
  for count, q in enumerate(data['questions']):
    # Stop adding questions past the given limit.
    if question_limit > 0 and count >= question_limit:
      break

    # Don't process questions without answers.
    if not 'answers' in q:
      print('Skipping question without answers.')
      continue

    # Upload file first to get an image tag.
    q_figure = upload_figure(folder, q.get('figure_path'), dry_run)

    question = {
      'question_name': q['name'],
      'question_text': latex(q['text']).replace('{figure}', q_figure),
      'question_type': q['type'],
      'points_possible': q['points'],
      'answers': [],
    }

    total_points += q['points']

    if q.get('distractors'):
      question['matching_answer_incorrect_matches'] = '\n'.join(q['distractors'])

    for a in q['answers']:
      answer = {}

      a_figure = upload_figure(folder, a.get('figure_path'), dry_run)

      # Multiple question types
      if 'text' in a:
        text_types = ['fill_in_multiple_blanks_question', 'multiple_dropdowns_question']
        key = 'answer_text' if q['type'] in text_types else 'answer_html'
        answer[key] = a['text'] if q['type'] in text_types else latex(a['text']).replace('{figure}', a_figure)

      if 'weight' in a:
        answer['answer_weight'] = 100 if a['weight'] > 0 else 0

      if a.get('comment'):
        answer['answer_comment_html'] = latex(a['comment'])

      # Matching questions
      if 'left' in a:
        answer['answer_match_left_html'] = latex(a['left']).replace('{figure}', a_figure)

      if 'right' in a:
        answer['answer_match_right'] = a['right']

      # Dropdown questions
      if 'blank_id' in a:
        answer['blank_id'] = a['blank_id']

      # Numerical questions
      if 'type' in a:
        answer['numerical_answer_type'] = a['type']

      if 'numerics' not in a:
        question['answers'].append(answer)
        continue

      n = a['numerics']

      if 'exact' in n:
        answer['answer_exact'] = n['exact']

      if 'error_margin' in n:
        answer['answer_error_margin'] = n['error_margin']

      if 'approximate' in n:
        answer['answer_approximate'] = n['approximate']

      if 'precision' in n:
        answer['answer_precision'] = n['precision']

      if 'range_start' in n:
        answer['answer_range_start'] = n['range_start']

      if 'range_end' in n:
        answer['answer_range_end'] = n['range_end']

      question['answers'].append(answer)

    if dry_run or not quiz:
      print(question)
      continue

    # Post the quiz.
    quiz.create_question(question=question)

  if not dry_run:
    # Update total points for the quiz.
    quiz.edit(quiz={'points_possible': total_points})
    print('Questions uploaded.')


  # Delete the quiz, leaving the questions in the "Unfiled" bank.
  if not dry_run and delete_quiz:
    quiz.delete()
    print('Quiz deleted.')


  # Return to MATLAB.
  print('Done!')


if __name__ == '__main__':
  cli()
