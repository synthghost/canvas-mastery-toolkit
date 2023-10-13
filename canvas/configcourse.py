from __future__ import annotations

import canvas.configmanager

class ConfigCourse:

  def __init__(self, manager: canvas.configmanager.ConfigManager, section: str) -> None:
    self.manager = manager
    self.config = self.manager.config
    self.section = section


  def get(self, key: str = None) -> str:
    return self.config.get(self.section, key)


  def set(self, key: str, value: str) -> None:
    self.config.set(self.section, key, value)
    self.manager.save()


  def get_revision_questions(self) -> list[dict]:
    return [dict(self.config.items(section))
      for section in self.config.sections()
        if str(section).startswith(self.revision_section())]


  def add_revision_questions(self) -> None:
    self.config[self.revision_section(1)] = {
      'question_name': 'Assignment URL',
      'question_text': (
        'Go to your submission for "$assignment", '
        'copy the URL, and paste it here as a link.'
      ),
      'question_type': 'essay_question',
      'points_possible': 1,
    }

    self.config[self.revision_section(2)] = {
      'question_name': 'Revised Work',
      'question_text': (
        'Upload your revised work. Be sure to follow the revision rules.'
      ),
      'question_type': 'file_upload_question',
      'points_possible': 1,
    }

    self.manager.save()


  def remove_revision_questions(self) -> None:
    for section in self.config.sections():
      if str(section).startswith(self.revision_section()):
        self.config.remove_section(section)

    self.manager.save()


  def revision_section(self, id: int = None) -> None:
    sub = f'.{id}' if id is not None else ''
    return f'{self.section}.revision_question{sub}'
