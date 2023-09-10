import re
import canvas.grader

from os import path
from tkinter import Tk
from bullet import Bullet
from canvas import styles
from canvasapi.assignment import Assignment
from tkinter.filedialog import asksaveasfilename

class CanvasQuizReviser(canvas.grader.Grader):

  def do(self) -> None:
    print('Now handling revisions for Canvas quiz')

    quiz = None
    submissions = None

    # Repeat quiz or submissions selection until we have submissions.
    while not submissions:
      quiz = self.get_quiz()
      submissions = self.get_submissions(quiz)

    # Set file name.
    name = re.sub(r'(?u)[^-\w.]', '', quiz.name.strip().replace(' ', '_'))

    box = Tk()
    # Show only file window, not full GUI.
    box.withdraw()
    box.attributes('-topmost', True)
    save_path = path.abspath(asksaveasfilename(initialfile=f'submissions_for_{name}', defaultextension='.html'))
    box.destroy()

    # Build links to submission comments.
    links = map(self.make_anchor, submissions)

    # Save links to the selected path.
    with open(save_path, 'w') as file:
      file.write('<br>'.join(links))

    print('\nSaved submission links to:', save_path)

    print('\nDone.')


  def get_quiz(self) -> Assignment:
    # Select an existing assignment.
    quizzes = [a for a in self.get_assignments()
      if a.published and a.is_quiz_assignment and a.grading_type == 'points']

    _, index = Bullet(f'\nSelect quiz:', **styles.bullets, choices=list(map(str, quizzes))).launch()
    print('\nQuiz:', quizzes[index])
    print()

    return quizzes[index]


  def get_submissions(self, quiz: Assignment):
    submissions = [s for s in quiz.get_submissions(include=['submission_comments'])
      if getattr(s, 'score', None) is not None and s.graded_at and s.submission_comments]

    # Validate submissions.
    if not submissions:
      print('That quiz has no submissions with comments! Please select another.')
      return

    print(f'Found {len(submissions)} submissions with comments.')

    return submissions


  def make_anchor(self, submission):
    name = f'Submission {submission.id}'
    url = submission.preview_url.split('?')[0]
    return f'<a href="{url}" target="_blank">{name}</a>'
