from bullet import utils
from bullet.client import myInput
from bullet import Numbers as BulletNumbers, YesNo as BulletYesNo

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


# Adapted from class bullet.YesNo to add space after default value.
class YesNo(BulletYesNo):

  def valid(self, ans):
    if ans is None:
      return False
    ans = ans.lower()
    if 'yes'.startswith(ans) or 'no'.startswith(ans):
      return True
    utils.moveCursorUp(1)
    utils.forceWrite(' ' * self.indent + self.prompt + self.default + ' ')
    utils.forceWrite(' ' * len(ans))
    utils.forceWrite('\b' * len(ans))
    return False


  def launch(self):
    my_input = myInput(word_color = self.word_color)
    utils.forceWrite(' ' * self.indent + self.prompt + self.default + ' ')
    while True:
      ans = my_input.input()
      if ans == '':
        return self.default.strip('[]') == 'y'
      if self.valid(ans):
        return 'yes'.startswith(ans.lower())
