from .coursemanager import CourseManager
from .gradingmanager import GradingManager
from .canvasquizgrader import CanvasQuizGrader
from .gradescopeexamgrader import GradescopeExamGrader
from .gradescopequizgrader import GradescopeQuizGrader
from .gradescopeexamreviser import GradescopeExamReviser
from .gradescopequizreviser import GradescopeQuizReviser

from . import gradingmanager as _gradingmanager

_gradingmanager.graders = [
  GradescopeQuizGrader,
  CanvasQuizGrader,
  GradescopeExamGrader,
]

_gradingmanager.revisers = [
  GradescopeQuizReviser,
  GradescopeExamReviser,
]
