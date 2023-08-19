from bullet import utils
from bullet.charDef import *
from bullet.client import myInput
from bullet import Numbers as BulletNumbers

# Adapted from class bullet.Numbers to output a given default value.
class Numbers(BulletNumbers):
  def valid(self, ans):
    try:
      self.type(ans)
      return True
    except:
      default = f'[{self.default}] ' if self.default else ''
      utils.moveCursorUp(1)
      utils.forceWrite(' ' * self.indent + self.prompt + default)
      utils.forceWrite(' ' * len(ans))
      utils.forceWrite('\b' * len(ans))
    return False

  def launch(self, default = None):
    self.default = default
    if self.default is not None:
      try:
        self.type(self.default)
      except:
        raise ValueError('`default` should be a ' + str(self.type))
    my_input = myInput(word_color = self.word_color)
    default = f'[{self.default}] ' if self.default else ''
    utils.forceWrite(' ' * self.indent + self.prompt + default)
    while True:
      ans = my_input.input()
      if ans == '' and self.default is not None:
        return self.default
      if self.valid(ans):
        return self.type(ans)
