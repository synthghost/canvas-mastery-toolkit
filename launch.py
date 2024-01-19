# -*- coding: utf-8 -*-

from canvas import App

if __name__ == "__main__":
  try:
    app = App()
    app.start()
  except KeyboardInterrupt:
    print('\nOperation stopped.')
