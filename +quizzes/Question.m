classdef Question < handle & matlab.mixin.Heterogeneous

    properties (SetAccess = protected)
        type; text
        name; points
        figure_path

        % The collection of answers to this question.
        answers = {};
    end

    properties (Access = protected)
        generator

        supported_types = {
            'fill_in_multiple_blanks_question',
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

    % Sealed methods cannot be redeclared by subclasses.
    methods (Sealed, Access = protected)
        function init(self, G, type, text, args)
            arguments
                self
                G quizzes.Generator
                type {mustBeText}
                text {mustBeText}
                args.name {mustBeText} = ''
                args.points {mustBePositive,mustBeScalarOrEmpty} = 1
                args.figure_path {mustBeText} = ''
            end

            assert(ismember(type, self.supported_types), 'Question type not supported.')

            self.generator = G;
            self.type = type;
            self.text = text;
            self.name = args.name;
            self.points = args.points;
            self.figure_path = args.figure_path;

            if length(self.figure_path) > 0
                self.generator.enable_figures();
            end
        end


        function merge(self, list)
            if length(self.answers) == 0 && length(list) == 1
                self.answers = {list};
                return
            end

            if length(self.answers) == 1
                self.answers = [self.answers{1}; list];
                return
            end

            self.answers = [self.answers; list];
        end
    end

    methods (Static, Sealed, Access = protected)
        function defaultObject = getDefaultScalarElement
            defaultObject = quizzes.MultipleAnswersQuestion('Placeholder');
        end
    end
end
