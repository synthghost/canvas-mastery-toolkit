classdef CanvasQuizGenerator < handle

    properties (SetAccess = protected)
        % The collection of generated questions.
        questions
    end

    methods
        function Q = add_matching_question(self, text, varargin)
            Q = self.add_question(MatchingQuestion(text, varargin{:}));
        end


        function Q = add_multiple_answers_question(self, text, varargin)
            Q = self.add_question(MultipleAnswersQuestion(text, varargin{:}));
        end


        function Q = add_multiple_choice_question(self, text, varargin)
            Q = self.add_question(MultipleChoiceQuestion(text, varargin{:}));
        end


        function Q = add_multiple_dropdowns_question(self, text, varargin)
            Q = self.add_question(DropdownsQuestion(text, varargin{:}));
        end


        function Q = add_numerical_question(self, text, varargin)
            Q = self.add_question(NumericalQuestion(text, varargin{:}));
        end


        function shuffle_questions(self)
            self.questions = self.questions(randperm(length(self.questions)));
        end
    end

    methods (Access = private)
        function Q = add_question(self, Q)
            assert(endsWith(class(Q), 'Question'), 'Data must be a Question type.')

            % Add new question to end of collection
            self.questions = [self.questions; Q];
        end
    end
end
