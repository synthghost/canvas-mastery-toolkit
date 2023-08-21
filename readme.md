# Canvas Mastery Toolkit

This repository contains a toolkit to support implementations of the learning mastery gradebook on Canvas.

## Requirements

- **MATLAB:** 2023a or later[^1]
- **Python:** 3.8 or later[^2]

**Python dependencies**
- [bullet](https://github.com/bchao1/bullet)
- [canvasapi](https://pypi.org/project/canvasapi/)
- [keyring](https://pypi.org/project/keyring/)
- [pandas](https://pypi.org/project/pandas/)
- [python-dateutil](https://pypi.org/project/python-dateutil/)
- [python-dotenv](https://pypi.org/project/python-dotenv/)

## Installation

To install the necessary Python requirements, run:

```bash
pip install -r requirements.txt
```

## Environment

The toolkit uses environmental variables to configure behavior. To get started, copy `.env.example` to `.env` and open in a text or code editor of choice.

To connect to the Canvas API, set `CANVAS_API_TOKEN` and `CANVAS_COURSE_ID`. To upload generated quiz questions to Canvas, set `PYTHON_COMMAND` to the system's Python executable. To additionally upload figures as part of quiz generation, set `CANVAS_FOLDER_ID`.

## Documentation

For details on usage and syntax, see the information provided in `docs/`.


[^1]: MATLAB 2023a introduced support for environmental variables, which the toolkit leverages in order to decouple sensitive configuration values from version-controlled code.
[^2]: Python 3.8 is the minimum version supported by the [pandas](https://pypi.org/project/pandas/) package, which is central to several features in the toolkit. Additionally, Python 3.8 introduced support for [assignment expressions](https://peps.python.org/pep-0572/), which help write clearer, well-intentioned list and dictionary comprehensions and are used throughout the toolkit.
