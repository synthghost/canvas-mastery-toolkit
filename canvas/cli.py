import click

from sys import platform
from canvas import styles


def is_unix_like() -> bool:
  return platform == 'darwin' or platform.startswith('linux')


def is_windows() -> bool:
  return platform == 'win32'


def menu(prompt: str, choices: list[str]) -> int:
  if is_unix_like():
    from bullet import Bullet

    _, index = Bullet(prompt, choices, **styles.bullets).launch()
    return index

  if is_windows():
    from consolemenu import SelectionMenu

    return SelectionMenu.get_selection(
      choices,
      title=prompt,
      show_exit_option=False,
    )

  raise EnvironmentError('OS or client not supported. Cannot display options.')


def confirm(prompt: str, default: str = 'y') -> bool:
  if is_unix_like():
    from canvas.bullet import YesNo

    return YesNo(prompt, default=default, **styles.inputs).launch()

  if is_windows():
    answer = text_input(f'[y/n] {prompt}', default=default, strip=True)

    return 'yes'.startswith(answer.lower())

  return False


def text(prompt: str, default = '', strip = False) -> str:
  if is_unix_like():
    from bullet import Input

    return Input(prompt, default=default, strip=strip, **styles.inputs).launch()

  return text_input(prompt, default, strip)


def text_input(prompt: str, default = '', strip = False) -> str:
  paren = f'[{default}] ' if default else ''
  while True:
    value = input(prompt + paren)
    if value == '' and default != '':
      return default
    if value == '':
      print('Input must not be blank. Please try again.\n')
      continue
    return value.strip() if strip else value


def number(prompt: str, default = None, type = float):
  if is_unix_like():
    from canvas.bullet import Numbers

    return Numbers(prompt, type=type, **styles.inputs).launch(default=default)

  return number_input(prompt, default, type)


def number_input(prompt: str, default = None, type = float):
  if default is not None:
    # Check default.
    try:
      type(default)
    except:
      raise ValueError('`default` should be a ' + str(type))
  paren = f'[{default}] ' if default is not None else ''
  while True:
    try:
      value = input(prompt + paren)
      if value == '' and default is not None:
        return default
      return type(value)
    except ValueError:
      kind = 'an integer' if type == int else 'a float'
      print(f'Input must be {kind}. Please try again.\n')
      continue


def error(message: str) -> None:
  click.secho(message, **styles.error)


def info(message: str) -> None:
  click.echo(message)


def warn(message: str) -> None:
  click.secho(message, **styles.warn)
