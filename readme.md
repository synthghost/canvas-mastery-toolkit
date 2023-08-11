# Canvas Mastery Toolkit

This repository contains tools to support implementations of the learning mastery gradebook on Canvas.

## Requirements

- **MATLAB:** 2023a or later (required to use environmental variables)
- **Python:** 3.8 or later (required by pandas)

**Python dependencies**
- [bullet](https://github.com/bchao1/bullet)
- [canvasapi](https://pypi.org/project/canvasapi/)
- [keyring](https://pypi.org/project/keyring/)
- [pandas](https://pypi.org/project/pandas/)
- [python-dotenv](https://pypi.org/project/python-dotenv/)

## Installation

To install the necessary Python requirements, run:

```bash
pip install -r requirements.txt
```

## Environment

This toolkit uses environmental variables to configure behavior. To get started, copy `.env.example` to `.env` and open in a text or code editor of choice.

To connect to the Canvas API, set `CANVAS_API_TOKEN` and `CANVAS_COURSE_ID`. To upload generated quiz questions to Canvas, set `PYTHON_COMMAND` to the system's Python executable. To additionally upload figures as part of quiz generation, set `CANVAS_FOLDER_ID`.

## Documentation

For details on usage and syntax, see the information provided in `docs/`.
