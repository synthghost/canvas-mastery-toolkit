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
# To be executed from MATLAB
###########################################################################


# File handling
def is_valid_file(parser, abs_path):
  if not path.exists(abs_path):
    parser.error('No file found at {}'.format(abs_path))
    return

  return abs_path


# Latex conversion
def latexrepl(match):
  if isinstance(match, re.Match):
    match = match.groups()[0]

  # Double-encode URLs to match Canvas behavior
  encoded = urllib.parse.quote(urllib.parse.quote(match))

  # Generate Canvas equation image HTML
  return f'<img class="equation_image" title="{match}" src="/equation_images/{encoded}?scale=1" alt="LaTeX: {match}" data-equation-content="{match}" data-ignore-a11y-check="" />'

# Parse LaTeX strings enclosed by $
def latex(text):
  p = re.compile('\${1,2}(.*?)\${1,2}')

  return p.sub(latexrepl, text)


# Gather command line arguments from MATLAB
parser = ArgumentParser(description='Canvas Mastery Toolkit - MATLAB Quiz Generator Sidecar')

parser.add_argument('--dry-run', action='store_true', help='perform data manipulation but do not post to Canvas')
parser.add_argument('--question-limit', nargs=1, help='limit on questions to add')
parser.add_argument('--delete-quiz', action='store_true', help='delete quiz after uploading questions')
parser.add_argument('path', nargs=1, help='path to .json data file', type=lambda input: is_valid_file(parser, input))

args = parser.parse_args()

dry = bool(args.dry_run)
limit = int(args.question_limit[0]) if args.question_limit else -1
delete = bool(args.delete_quiz)

if args.path:
  output_path = args.path[0]

if not output_path:
  print('Specify an output path via command line arguments')
  exit()

print(f'Using file {output_path} with a limit of {limit}')

if dry:
  print('*** DRY RUN ***')

# Connect to Canvas course
manager = CourseManager()
# manager.set_logging(logging.DEBUG)
course = manager.get_course()

print('Course:', course)


# Read the generated data as JSON
with open(output_path, 'r') as file:
  data = json.load(file)

if not 'questions' in data:
  print('No questions to process.')
  exit()


# Create a blank quiz
if not dry:
  quiz = course.create_quiz({
    'title': data.get('title') or f'Generated Quiz {uuid.uuid4()}',
    'description': data.get('description', ''),
    'quiz_type': 'assignment',
    'shuffle_answers': False,
  })

  print('Quiz:', quiz)


# Keep count for limiting purposes
count = 0

# Iterate over data to prepare for Canvas API
for q in data['questions']:
  count += 1

  # Stop adding questions past the given limit
  if limit > 0 and count >= limit:
    break

  question = {
    'question_name': q['name'],
    'question_text': latex(q['text']),
    'question_type': q['type'],
    'points_possible': q['points'],
    'answers': [],
  }

  if q.get('distractors'):
    question['matching_answer_incorrect_matches'] = '\n'.join(q['distractors'])

  if not 'answers' in q:
    continue

  for a in q['answers']:
    answer = {}

    # Multiple question types
    if 'text' in a:
      text_types = ['fill_in_multiple_blanks_question', 'multiple_dropdowns_question']
      key = 'answer_text' if q['type'] in text_types else 'answer_html'
      answer[key] = a['text'] if q['type'] in text_types else latex(a['text'])

    if 'weight' in a:
      answer['answer_weight'] = 100 if a['weight'] > 0 else 0

    if a.get('comment'):
      answer['answer_comment_html'] = latex(a['comment'])

    # Matching questions
    if 'left' in a:
      answer['answer_match_left_html'] = latex(a['left'])

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

  # Post the quiz
  quiz.create_question(question=question)

print('Questions uploaded.')


# Delete the quiz, leaving the questions in the "Unfiled" bank
if not dry and delete:
  quiz.delete();
  print('Quiz deleted.')


# Return to MATLAB
print('Done!')
