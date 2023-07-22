# Canvas Mastery Toolkit

This repository contains tools to support implementations of the learning mastery gradebook on Canvas.

## Requirements

- **MATLAB:** 2022b or later
- **Python:** 3.8 or later

**Python dependencies**
- [canvasapi](https://pypi.org/project/canvasapi/)
- [keyring](https://pypi.org/project/keyring/)
- [python-dotenv](https://pypi.org/project/python-dotenv/)

## Installation

To install the necessary Python requirements, run:

```bash
pip install -r requirements.txt
```

## Python Environment

To set a Canvas API access token and course ID, copy `.env.example` to `.env` and set `CANVAS_API_TOKEN` and `CANVAS_COURSE_ID` respectively.

## MATLAB Configuration

Automating the MATLAB-to-Python process is optional, but doing so requires configuring MATLAB to call Python via system commands. To configure this, open `config.m` and set `python_command` and `python_script`.

## Usage

The MATLAB script `quiz_generator.m` demonstrates how to generate quiz questions and upload them to Canvas. New generators can be created in much the same way, but require at least the following boilerplate.

```matlab
% Add the quiz generator toolkit to the MATLAB path.
addpath('matlab');

% The absolute path where the data output file will be saved. This is
% passed to Python, which will complain if it can't access the file, so
% an absolute path is recommended. Optionally, it may be useful to change
% this value for each quiz should you wish to keep a record of the output.
output_path = '/path/to/output.json';

G = CanvasQuizGenerator(config(), output_path);

% Q = G.add...

G.upload();
```

The quiz's title and description can optionally be set as part of the boilerplate.

```matlab
G = CanvasQuizGenerator(config(), output_path, 'Quiz Title', 'Description text');
```

Details about question generation can be found in `docs.md`.
