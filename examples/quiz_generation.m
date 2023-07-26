%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% CANVAS QUIZ GENERATION
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

clear all; clc

addpath('/path/to/canvas-mastery-toolkit');

data_path = '/path/to/data.json';
quiz_title = 'MATLAB-Generated Quiz';

G = quizzes.Generator(data_path, quiz_title);



%% Matching

% Add a question with a figure, which is inserted in place of "{figure}".
Q1 = G.add_matching_question('<p>Match the parts of the horse.</p><p>{figure}</p>', ...
    points=4, figure_path='/path/to/figure_1.png');

Q1.add_answer_pair('Torso {figure}', 'Barrel', figure_path='/path/to/figure_2.png');
Q1.add_answer_pair('Front half', 'Forehand', comment_when_incorrect='Don''t feel bad! This is a hard one.');

% Add more pairs.
Q1.add_answer_pairs({
    {'Back half', 'Haunches'},
    {'Foot {figure}', 'Hoof', '', '/path/to/figure_3.png'},
    {'Nose', 'Muzzle', 'Horses make all kinds of funny faces!'},
});

Q1.add_distractors({'Stifle', 'Forelock'});
Q1.add_distractors({'Pastern'; 'Croup'});



%% Multiple Answers

Q2 = G.add_multiple_answers_question('<p>Which kinds of horses are real?</p>', points=3);

Q2.add_correct_answers({'Warmblood', 'Draft', 'Iberian', 'Arabian', 'Icelandic'});

Q2.add_incorrect_answers({
    'Pegasus',
    {'Unicorn {figure}', '', '/path/to/figure_4.png'},
    'Centaur',
});

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

Q4 = G.add_multiple_choice_question('<p>Are horses bigger than rabbits?</p>');

Q4.add_correct_answer('Usually, but not always {figure}', comment='Incredibly, this is true!', figure_path='/path/to/figure_5.png');

% Trying to add more correct answers throws an error.
% Q4.add_correct_answer('There can''t be two right answers!');

Q4.add_incorrect_answers({
    {'Always! Why even ask?!', 'An understandable instinct, but it''s not always the case'},
    'Never! Have you seen rabbits? They''re huge!',
});

% How best to do this?
% Q4.subset_answers()

Q4.shuffle_answers();

Q4.add_incorrect_answer('I don''t know! {figure}', figure_path='/path/to/figure_6.png');



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

Q6 = G.add_numerical_question('<p>At what age (in years) is a horse considered a yearling? {figure}</p>', figure_path='/path/to/figure_7.png');

% Q6.add_exact_answer(1, 0.5);
% Q6.add_precision_answer(1.000, 3);
Q6.add_range_answer(0.8, 1.2, 'Nice job!');



%% Output

% G.shuffle_questions();

% Save to file only.
% G.save();

% Save and upload to Canvas.
G.upload('--dry-run');
