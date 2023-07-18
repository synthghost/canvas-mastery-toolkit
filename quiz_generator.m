%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% QUIZ GENERATOR
% Demo
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

close all; clear all; clc

addpath('matlab')

G = CanvasQuizGenerator();



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



%% Multiple Choice

Q3 = G.add_multiple_choice_question('<p>Are horses bigger than rabbits?</p>', points=1);

Q3.add_correct_answer('Usually, but not always', 'Incredibly, this is true!');

% This one throws an error. Intentional!
% Q1.add_correct_answer('There can''t be two right answers!');

Q3.add_incorrect_answers({
    {'Always! Why even ask?!', 'An understandable instinct, but it''s not always the case'};
    'Never! Have you seen rabbits? They''re huge!'
});

% Add more
Q3.add_incorrect_answers({'The jury''s still out on this one'});

% How best to do this?
% Q2.subset_answers()

Q3.shuffle_answers();

Q3.add_catchall_answer('I don''t know!');



%% Multiple Dropdowns

Q4 = G.add_multiple_dropdowns_question('<p>An adult female horse is a [opt1] and a young male is a [opt2].</p>', points=2);

Q4.add_correct_answer('opt1', 'Mare');
Q4.add_incorrect_answer('opt1', 'Stallion');

% Should this also allow bulk additions?
Q4.add_correct_answer('opt2', 'Colt', 'This one can be tricky.');
Q4.add_incorrect_answer('opt2', 'Filly');

Q4.shuffle_answers();



%% Numerical

Q5 = G.add_numerical_question('<p>At what age (in years) is a horse considered a yearling?</p>', points=1);

% Q5.add_exact_answer(1, 0.5);
% Q5.add_precision_answer(1.000, 3);
Q5.add_range_answer(0.8, 1.2, 'Nice job!');



%% Output

% G.shuffle_questions();

encoded = jsonencode(G);

filename = 'demo.json';
fid = fopen(['output/', filename], 'wt');
fprintf(fid, encoded);
fclose(fid);

status = system(['/usr/bin/env /usr/local/bin/python3 /Users/orion/Code/canvas-mastery-toolkit/quiz_generator.py  --dry-run --limit 10 ', filename]);
