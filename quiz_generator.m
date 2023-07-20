%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% QUIZ GENERATOR
% Demo
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

close all; clear all; clc

addpath('matlab');

% The absolute path where the data output file will be saved. This is
% passed to Python, which will complain if it can't access the file, so
% an absolute path is recommended. Optionally, it may be useful to change
% this value for each quiz should you wish to keep a record of the output.
output_path = '/path/to/output.json';

% The title to give the quiz when uploading to Canvas. If --delete-quiz
% is given as a Python flag later, this title is effectively meaningless
% since the quiz will be removed once the questions are fully uploaded.
quiz_title = 'MATLAB-Generated Quiz';

G = CanvasQuizGenerator(output_path, quiz_title);



%% Matching

Q1 = G.add_matching_question('<p>Match the parts of the horse.</p>', points=4);

Q1.add_answer_pair('Torso', 'Barrel');
Q1.add_answer_pair('Ankle', 'Fetlock', 'Don''t feel bad! This is a hard one.');

% Add more
Q1.add_answer_pairs({
    {'Front half', 'Forehand'},
    {'Back half', 'Haunches'},
    {'Foot', 'Hoof'},
    {'Nose', 'Muzzle', 'Horses make all kinds of funny faces!'},
});

Q1.add_distractors({'Stifle', 'Forelock'});
Q1.add_distractors({'Pastern'; 'Croup'});



%% Multiple Answers

Q2 = G.add_multiple_answers_question('<p>Which kinds of horses are real?</p>', points=3);

Q2.add_correct_answers({'Warmblood', 'Draft', 'Iberian', 'Arabian', 'Icelandic'});

Q2.add_incorrect_answers({'Pegasus', 'Unicorn', 'Centaur'});

Q2.shuffle_answers();



%% Multiple Blanks

Q3 = G.add_multiple_blanks_question('<p>A horse''s height is measured at the [blank1], typically in units of [blank2].</p>', points=2);

Q3.add_correct_answer('blank1', 'withers', 'Very good!');
Q3.add_correct_answers('blank2', {
    {'hands', 'Yup! A \"hand\" is 4 inches long.'},
    'centimeters',
    'cm',
});



%% Multiple Choice

Q4 = G.add_multiple_choice_question('<p>Are horses bigger than rabbits?</p>', points=1);

Q4.add_correct_answer('Usually, but not always', 'Incredibly, this is true!');

% This one throws an error. Intentional!
% Q1.add_correct_answer('There can''t be two right answers!');

Q4.add_incorrect_answers({
    {'Always! Why even ask?!', 'An understandable instinct, but it''s not always the case'},
    'Never! Have you seen rabbits? They''re huge!',
});

% Add more
Q4.add_incorrect_answers({'The jury''s still out on this one'});

% How best to do this?
% Q2.subset_answers()

Q4.shuffle_answers();

Q4.add_catchall_answer('I don''t know!');



%% Multiple Dropdowns

Q5 = G.add_multiple_dropdowns_question('<p>An adult female horse is a [drop1] and a young male is a [drop2].</p>', points=2);

Q5.add_correct_answer('drop1', 'Mare');
Q5.add_incorrect_answers('drop1', {
    'Stallion',
    'Colt',
    'Filly',
    {'Foal', 'This is a general term for a young horse.'},
});

Q5.add_correct_answer('drop2', 'Colt');
Q5.add_incorrect_answers('drop2', {
    'Mare',
    'Stallion',
    'Filly',
    {'Foal', 'This is a general term for a young horse.'},
});

Q5.shuffle_answers();



%% Numerical

Q6 = G.add_numerical_question('<p>At what age (in years) is a horse considered a yearling?</p>', points=1);

% Q5.add_exact_answer(1, 0.5);
% Q5.add_precision_answer(1.000, 3);
Q6.add_range_answer(0.8, 1.2, 'Nice job!');



%% Output

% G.shuffle_questions();

% Save to file only.
% G.save();

% Save and upload to Canvas.
% Possible Python flags: --dry-run, --question-limit [num], --delete-quiz
G.upload('--dry-run');
