classdef MultipleChoiceQuestion < quizzes.MultipleAnswersQuestion

    properties (Hidden, SetAccess = protected)
        hasCorrectAnswer = false;
    end

    methods
        function self = MultipleChoiceQuestion(G, text, varargin)
            self@quizzes.MultipleAnswersQuestion(G, text, varargin{:});
            self.type = 'multiple_choice_question';
        end
    end

    methods (Hidden)
        function add_correct_answers(self, array)
            assert(length(array) == 1 & ~self.hasCorrectAnswer, ...
                'Multiple choice questions can only have one correct answer')

            add_correct_answers@quizzes.MultipleAnswersQuestion(self, array);
            self.hasCorrectAnswer = true;
        end
    end
end
