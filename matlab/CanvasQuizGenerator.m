classdef CanvasQuizGenerator < handle

    properties (SetAccess = protected)
        title; description

        % The collection of generated questions.
        questions
    end

    properties (Access = protected)
        python_command = '';
        python_script = '';
        output_path
    end

    methods
        function self = CanvasQuizGenerator(config, output_path, title, description)
            arguments
                config struct
                output_path {mustBeText}
                title {mustBeText} = ''
                description {mustBeText} = ''
            end

            self.output_path = output_path;
            self.title = title;
            self.description = description;

            if isfield(config, 'python_command') && ~isempty(config.python_command)
                self.python_command = config.python_command;
            end

            if isfield(config, 'python_script') && ~isempty(config.python_script)
                self.python_script = config.python_script;
            end
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

            assert(strlength(self.python_command), 'Python command must be defined in config.m.')
            assert(strlength(self.python_script), 'Python script must be defined in config.m.')

            % Make sure output is saved
            self.save();

            % Run Python script to upload quiz data to Canvas
            system(sprintf('%s "%s" %s "%s"', ...
                self.python_command, self.python_script, python_flags, self.output_path));
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
