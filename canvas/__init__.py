from .coursemanager import CourseManager
from .gradingmanager import GradingManager
from .canvasquizgrader import CanvasQuizGrader
from .gradescopeexamgrader import GradescopeExamGrader
from .gradescopequizgrader import GradescopeQuizGrader

from . import gradingmanager as _gradingmanager

_gradingmanager.graders = [
  GradescopeQuizGrader,
  CanvasQuizGrader,
  GradescopeExamGrader,
]
