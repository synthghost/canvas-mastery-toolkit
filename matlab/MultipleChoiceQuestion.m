classdef MultipleChoiceQuestion < MultipleAnswersQuestion

    properties (Hidden, SetAccess = protected)
        hasCorrectAnswer = false;
    end

    methods
        function self = MultipleChoiceQuestion(text, varargin)
            self@MultipleAnswersQuestion(text, varargin{:});
            self.type = 'multiple_choice_question';
        end


        function add_correct_answer(self, text, comment)
            arguments
                self
                text {mustBeText}
                comment {mustBeText} = ''
            end

            self.add_correct_answers({{text, comment}});
        end


        function add_correct_answers(self, array)
            assert(length(array) == 1 & ~self.hasCorrectAnswer, ...
                'Multiple choice questions can only have one correct answer')

            add_correct_answers@MultipleAnswersQuestion(self, array);
            self.hasCorrectAnswer = true;
        end
    end
end
