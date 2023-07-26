classdef Generator < handle

    properties (SetAccess = protected)
        title; description

        has_figures = false;

        % The collection of generated questions.
        questions = {};
    end

    properties (Access = protected)
        data_path
    end

    methods
        function self = Generator(data_path, title, description)
            arguments
                data_path {mustBeText}
                title {mustBeText} = ''
                description {mustBeText} = ''
            end

            self.data_path = data_path;
            self.title = title;
            self.description = description;
        end


        function Q = add_matching_question(self, text, varargin)
            Q = self.add_question(quizzes.MatchingQuestion(self, text, varargin{:}));
        end


        function Q = add_multiple_answers_question(self, text, varargin)
            Q = self.add_question(quizzes.MultipleAnswersQuestion(self, text, varargin{:}));
        end


        function Q = add_multiple_blanks_question(self, text, varargin)
            Q = self.add_question(quizzes.BlanksQuestion(self, text, varargin{:}));
        end


        function Q = add_multiple_choice_question(self, text, varargin)
            Q = self.add_question(quizzes.MultipleChoiceQuestion(self, text, varargin{:}));
        end


        function Q = add_multiple_dropdowns_question(self, text, varargin)
            Q = self.add_question(quizzes.DropdownsQuestion(self, text, varargin{:}));
        end


        function Q = add_numerical_question(self, text, varargin)
            Q = self.add_question(quizzes.NumericalQuestion(self, text, varargin{:}));
        end


        function shuffle_questions(self)
            self.questions = self.questions(randperm(length(self.questions)));
        end


        function enable_figures(self)
            self.has_figures = true;
        end


        function save(self)
            % Write generator data to file.
            fid = fopen(self.data_path, 'wt');
            fprintf(fid, jsonencode(self));
            fclose(fid);
            fprintf('Data saved to %s\n', self.data_path);
        end


        function upload(self, python_flags)
            arguments
                self
                python_flags {mustBeText} = ''
            end

            % Load configuration struct from config.m.
            cfg = config();

            assert(isfield(config, 'python_command') && strlength(cfg.python_command), ...
                'Missing Python command (PYTHON_COMMAND).')

            % Make sure data is saved.
            self.save();

            % Run Python to upload quiz data to Canvas.
            system(sprintf('%s "%s" %s "%s"', ...
                cfg.python_command, cfg.python_uploader, python_flags, self.data_path));
        end
    end

    methods (Access = private)
        function Q = add_question(self, Q)
            assert(endsWith(class(Q), 'Question'), 'Data must be a Question type.')

            % Add new question to end of collection.
            self.questions{end+1,1} = Q;
        end
    end
end
