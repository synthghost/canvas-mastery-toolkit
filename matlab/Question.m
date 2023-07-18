classdef Question < handle & matlab.mixin.Heterogeneous

    properties (SetAccess = protected)
        type; text
        name; points

        % The collection of answers to this question.
        answers
    end

    properties (Access = protected)
        supported_types = {
            'matching_question',
            'multiple_answers_question',
            'multiple_choice_question',
            'multiple_dropdowns_question',
            'numerical_question'
        };
    end

    methods
        function shuffle_answers(self)
            self.answers = self.answers(randperm(length(self.answers)));
        end
    end

    % Sealed methods cannot be redeclared by subclasses
    methods (Sealed, Access = protected)
        function init(self, type, text, options)
            arguments
                self
                type {mustBeText}
                text {mustBeText}
                options.name {mustBeText} = ''
                options.points {mustBePositive,mustBeScalarOrEmpty} = 1
            end

            assert(ismember(type, self.supported_types), 'Question type not supported.')

            self.type = type;
            self.text = text;
            self.name = options.name;
            self.points = options.points;
        end
    end

    methods (Static, Sealed, Access = protected)
        function defaultObject = getDefaultScalarElement
            defaultObject = MultipleAnswersQuestion('Placeholder');
        end
    end
end
