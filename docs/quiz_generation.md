# Canvas Quiz Generation

The MATLAB script `examples/quiz_generation.m` demonstrates how to generate quiz questions and upload them to Canvas. New generators can be created in much the same way, but require at least the following boilerplate.

```matlab
% Add the toolkit to the MATLAB path.
addpath('/path/to/canvas-mastery-toolkit');

% The absolute path where the data output file will be saved. This is
% passed to Python, which will complain if it can't access the file, so
% an absolute path is recommended. Optionally, it may be useful to change
% this value for each quiz should you wish to keep a record of the output.
data_path = '/path/to/data.json';

% Create a quiz generator.
G = quizzes.Generator(data_path);

% Add questions and answers.
% Q = G.add...

% Upload to Canvas.
G.upload();
```

In some cases, it may be convenient to use dynamic paths and quiz names that match the filename and/or folder of the specific generator script.

```matlab
% Matching filename in an unrelated folder.
data_path = ['/path/to/', mfilename, '.json'];

% Matching filename in the current folder.
[this_folder, this_file] = fileparts(mfilename('fullpath'));
data_path = [this_folder, '/', this_file, '.json'];
```

The quiz's title and rich-text description can optionally be set as part of the boilerplate.

```matlab
G = quizzes.Generator(data_path, 'Quiz Title', 'Description text');
```

Note that if `--delete-quiz` is given as a Python flag during upload, the title and description are effectively meaningless since the quiz will be removed once the questions are fully uploaded.

## Creating and using a generator

Generating Canvas quizzes in MATLAB revolves around the `Generator` class of the `quizzes` package. A generator object must be instantiated with a data output path to begin adding questions.

```matlab
G = quizzes.Generator('path/to/data.json');
```

The data output path determines where MATLAB will save a JSON representation of the assembled quiz. This data is passed to Python to upload to Canvas.

Once instantiated, the generator provides methods to add quiz questions of several types. These methods all require one argument (the rich question text) and optionally take two others (the question name and number of points possible).

```matlab
Q = G.add_matching_question(text, name='', points=1);
Q = G.add_multiple_answers_question(text, name='', points=1);
Q = G.add_multiple_blanks_question(text, name='', points=1);
Q = G.add_multiple_choice_question(text, name='', points=1);
Q = G.add_multiple_dropdowns_question(text, name='', points=1);
Q = G.add_numerical_question(text, name='', points=1);
```

Each method is described in more detail below.

Answers within a particular question can be shuffled. The order of questions added to the generator can also be shuffled, though this has no affect on their answers. Shuffling can be done at any point, leaving subsequent additions unshuffled.

```matlab
% Shuffle answers in question Q.
Q.shuffle_answers();

% Shuffle questions in generator G.
G.shuffle_questions();
```

When all questions and answers have been added, the quiz can be uploaded to Canvas.

```matlab
G.upload();
G.upload(python_flags);
```

The argument `python_flags` can take any number of three possible flags which are passed to Python to alter the uploading behavior.

- `'--dry-run'` performs a dry run without actually modifying data on Canvas. This is useful to test the process and ensure correct configuration.
- `'--question-limit [num]'` takes a numeric value in place of `[num]` and limits the number of questions to process should the generator have an excessive amount. This is useful in combination with question shuffling.
- `'--delete-quiz'` deletes the quiz from Canvas immediately after uploading it. This allows creating a temporary quiz as a vessel to add the questions to an "Unfiled" question bank on Canvas, then removing that vessel afterwards.

The quiz can also be saved without uploading.

```matlab
% Save to file only.
G.save();
```

### Matching Questions

Matching questions take correct answer pairs. The left side is the prompt and can contain rich text. The right side is the correct answer in plain text, which is added as a choice to each of the question's dropdowns. Optionally, a rich-text comment can be added in the case of an incorrect choice for that prompt. Answer pairs can be also be added in bulk.

```matlab
Q.add_answer_pair(left, right);
Q.add_answer_pair(left, right, incorrect_comment);

Q.add_answer_pairs({
    {left, right},
    {left, right, incorrect_comment},
});
```

Incorrect answers, called distractors, can be added as additional plain-text choices to each of the question's dropdowns.

```matlab
Q.add_distractors({text, text, ...});
```

### Multiple Answers Questions

Multiple answers questions take multiple correct and multiple incorrect answers, both of which can contain rich text. Optionally, a rich-text comment can be added to each in the case of that choice, whether correct or incorrect.

```matlab
Q.add_correct_answers({
    text,
    {text, comment},
});

Q.add_incorrect_answers({
    text,
    {text, comment},
});
```

### Multiple Blanks Questions

Multiple blanks questions take only correct answers in plain text, either singularly or in bulk. Optionally, a rich-text comment can be added to each in the case of that entry.

```matlab
Q.add_correct_answer(blank_id, text);
Q.add_correct_answer(blank_id, text, comment);

Q.add_correct_answers(blank_id, {
    text,
    {text, comment}
});
```

The first argument, `blank_id`, can be any string but must match square-bracketed keywords defined in the question text.

```matlab
Q = G.add_multiple_blanks_question('The first letter in the English alphabet is [letter].');

Q.add_correct_answer('letter', 'A');
```

### Multiple Choice Questions

Multiple choice questions are identical to multiple answers questions above, except they take only one correct answer.

```matlab
Q.add_correct_answer(text);
Q.add_correct_answer(text, comment);

Q.add_incorrect_answers({
    text,
    {text, comment},
});
```

### Multiple Dropdowns Questions

Multiple dropdowns questions take one correct and multiple incorrect answers in plain text. Optionally, a rich-text comment can be added to each in the case of that choice, whether correct or incorrect.

```matlab
Q.add_correct_answer(blank_id, text);
Q.add_correct_answer(blank_id, text, comment);

Q.add_incorrect_answers(blank_id, {
    text,
    {text, comment},
});
```

The first argument, `blank_id`, can be any string but must match square-bracketed keywords defined in the question text.

```matlab
Q = G.add_multiple_dropdowns_question('The last letter in the English alphabet is [letter].');

Q.add_correct_answer('letter', 'Z');
Q.add_incorrect_answers('letter', {'X', 'Y'});
```

### Numerical Questions

Numerical questions take only one correct answer. There are three types of numerical answers: exact, precision, and range. Optionally, a rich-text comment can be added in the case of a correct entry.

```matlab
Q.add_exact_answer(exact, error_margin);
Q.add_exact_answer(exact, error_margin, comment);

Q.add_precision_answer(approximate, precision);
Q.add_precision_answer(approximate, precision, comment);

Q.add_range_answer(range_start, range_end);
Q.add_range_answer(range_start, range_end, comment);
```

The exact answer type takes an exact numeric value as a baseline and an absolute numeric margin within which other answers are considered correct. For example, `(100, 0.1)` would accept answers from 99.9 to 100.1.

The precision answer type takes an approximate numeric value as a baseline and a number of decimals of precision to expect for correct answers. For example, `(3.14, 2)` would accept answers of 3.14, 3.142, 3.1416 and so on.

The range answer type takes numeric values for the start and end of a range of correct answers. For example, `(40, 60)` would accept answers from 40 to 60.
