import re
import json
import uuid
import logging
import urllib.parse

from os import path
from canvas import CourseManager
from argparse import ArgumentParser

###########################################################################
# QUIZ GENERATOR
# To be executed from MATLAB.
###########################################################################


# File handling
def validate_path(abs_path):
  if abs_path and not path.exists(abs_path):
    raise FileNotFoundError('No file found at {}'.format(abs_path))

def is_valid_file(parser, abs_path):
  try:
    validate_path(abs_path)
    return abs_path
  except FileNotFoundError as e:
    parser.error(e)

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


# Gather command line arguments from MATLAB.
parser = ArgumentParser(description='Canvas Mastery Toolkit - MATLAB Quiz Generator Sidecar')

parser.add_argument('--dry-run', action='store_true', help='perform data manipulation but do not post to Canvas')
parser.add_argument('--question-limit', nargs=1, help='limit on questions to add')
parser.add_argument('--delete-quiz', action='store_true', help='delete quiz after uploading questions')
parser.add_argument('data_path', nargs=1, help='path to .json data file', type=lambda input: is_valid_file(parser, input))

args = parser.parse_args()

dry = bool(args.dry_run)
limit = int(args.question_limit[0]) if args.question_limit else -1
delete = bool(args.delete_quiz)

if args.data_path:
  data_path = args.data_path[0]

if not data_path:
  print('Specify a data path via command line arguments')
  exit()

print(f'Using file {data_path} with a limit of {limit}')

if dry:
  print('*** DRY RUN ***')

# Connect to Canvas course.
manager = CourseManager()
# manager.set_logging(logging.DEBUG)
course = manager.get_course()

print('Course:', course)


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
if not dry:
  quiz = course.create_quiz({
    'title': data.get('title') or f'Generated Quiz {uuid.uuid4()}',
    'description': data.get('description', ''),
    'quiz_type': 'assignment',
    'shuffle_answers': False,
  })

  print('Quiz:', quiz)


def upload_figure(folder, abs_path):
  if not folder or not abs_path:
    return ''
  if dry:
    return f'<fig="{abs_path}" />'
  is_uploaded, response = folder.upload(abs_path)
  if not is_uploaded:
    raise IOError(f'Upload failed for figure {abs_path}')
  print(f'Figure {response["filename"]} uploaded.')
  url = response['preview_url'].split('?')[0].replace('file_', '')
  return f'<img id="{response["id"]}" src="{url}" alt="" />'


# Keep count for limiting purposes.
count = 0

# Keep running total of the quiz points.
total_points = 0

# Iterate over data to prepare for Canvas API.
for q in data['questions']:
  count += 1

  # Stop adding questions past the given limit.
  if limit > 0 and count >= limit:
    break

  # Don't process questions without answers.
  if not 'answers' in q:
    print('Skipping question without answers.')
    continue

  # Upload file first to get an image tag.
  q_figure = upload_figure(folder, q.get('figure_path'))

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

    a_figure = upload_figure(folder, a.get('figure_path'))

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

  if dry or not quiz:
    print(question)
    continue

  # Post the quiz.
  quiz.create_question(question=question)

if not dry:
  # Update total points for the quiz.
  quiz.edit(quiz={'points_possible': total_points})
  print('Questions uploaded.')


# Delete the quiz, leaving the questions in the "Unfiled" bank.
if not dry and delete:
  quiz.delete()
  print('Quiz deleted.')


# Return to MATLAB.
print('Done!')
