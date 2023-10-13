from canvas.configmanager import ConfigManager

# Dependent on canvas.configmanager.
from canvas.coursemanager import CourseManager
from canvas.gradingmanager import GradingManager

from canvas.canvasquizgrader import CanvasQuizGrader
from canvas.canvasquizreviser import CanvasQuizReviser
from canvas.gradescopeexamgrader import GradescopeExamGrader
from canvas.gradescopequizgrader import GradescopeQuizGrader
from canvas.gradescopeexamreviser import GradescopeExamReviser
from canvas.gradescopequizreviser import GradescopeQuizReviser

from canvas import gradingmanager as _gradingmanager

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
