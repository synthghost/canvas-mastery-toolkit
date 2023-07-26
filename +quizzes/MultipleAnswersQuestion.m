classdef MultipleAnswersQuestion < quizzes.Question

    methods
        function self = MultipleAnswersQuestion(G, text, varargin)
            self.init(G, 'multiple_answers_question', text, varargin{:});
        end


        function add_correct_answer(self, text, args)
            arguments
                self
                text {mustBeText}
                args.comment {mustBeText} = ''
                args.figure_path {mustBeText} = ''
            end

            self.add_correct_answers({{text, args.comment, args.figure_path}});
        end


        function add_correct_answers(self, array)
            arguments
                self
                array (:,1) cell
            end

            self.add_answers(array, 100);
        end


        function add_incorrect_answer(self, text, args)
            arguments
                self
                text {mustBeText}
                args.comment {mustBeText} = ''
                args.figure_path {mustBeText} = ''
            end

            self.add_incorrect_answers({{text, args.comment, args.figure_path}});
        end


        function add_incorrect_answers(self, array)
            arguments
                self
                array (:,1) cell
            end

            self.add_answers(array, 0);
        end
    end

    methods (Access = protected)
        function add_answers(self, array, weight)
            arguments
                self
                array (:,1) cell
                weight {mustBeNonnegative,mustBeScalarOrEmpty}
            end

            assert(length(array) > 0, 'Answer array cannot be empty.')

            % Iterate backward to force memory pre-allocation
            for i = length(array):-1:1
                data(i,1) = self.make_answer(array{i}, weight);
            end

            self.merge(data);
        end


        function A = make_answer(self, data, weight)
            args = quizzes.pad_char_array(data, 3);

            % Check for figures
            if length(args{3}) > 0
                self.generator.enable_figures();
            end

            A = quizzes.MultipleAnswersAnswer(weight, args{:});
        end
    end
end
