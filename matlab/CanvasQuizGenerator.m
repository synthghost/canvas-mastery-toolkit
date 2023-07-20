classdef CanvasQuizGenerator < handle

    properties (SetAccess = protected)
        title; description

        % The collection of generated questions.
        questions
    end

    properties (Access = protected)
        output_path
    end

    methods
        function self = CanvasQuizGenerator(output_path, title, description)
            arguments
                output_path {mustBeText}
                title {mustBeText} = ''
                description {mustBeText} = ''
            end

            self.output_path = output_path;
            self.title = title;
            self.description = description;
        end


        function Q = add_matching_question(self, text, varargin)
            Q = self.add_question(MatchingQuestion(text, varargin{:}));
        end


        function Q = add_multiple_answers_question(self, text, varargin)
            Q = self.add_question(MultipleAnswersQuestion(text, varargin{:}));
        end


        function Q = add_multiple_blanks_question(self, text, varargin)
            Q = self.add_question(BlanksQuestion(text, varargin{:}));
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


        function save(self)
            % Write generator output to file
            fid = fopen(self.output_path, 'wt');
            fprintf(fid, jsonencode(self));
            fclose(fid);
            fprintf('Output saved to %s\n', self.output_path);
        end


        function upload(self, python_flags)
            arguments
                self
                python_flags {mustBeText} = ''
            end

            % Make sure output is saved
            self.save();

            c = config();

            % Run Python script to upload quiz data to Canvas
            system(sprintf('%s "%s" %s "%s"', ...
                c.python_command, c.python_path, python_flags, self.output_path));
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
