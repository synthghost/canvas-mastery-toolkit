from .coursemanager import CourseManager
from .gradingmanager import GradingManager
from .canvasquizgrader import CanvasQuizGrader
from .canvasquizreviser import CanvasQuizReviser
from .gradescopeexamgrader import GradescopeExamGrader
from .gradescopequizgrader import GradescopeQuizGrader
from .gradescopeexamreviser import GradescopeExamReviser
from .gradescopequizreviser import GradescopeQuizReviser

from . import gradingmanager as _gradingmanager

_gradingmanager.graders = [
  CanvasQuizGrader,
  GradescopeQuizGrader,
  GradescopeExamGrader,
]

_gradingmanager.revisers = [
  CanvasQuizReviser,
  GradescopeQuizReviser,
  GradescopeExamReviser,
]
