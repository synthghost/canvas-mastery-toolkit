classdef MatchingQuestion < quizzes.Question

    properties (SetAccess = protected)
        % The list of incorrect values to show amonst the correct ones.
        distractors
    end

    methods
        function self = MatchingQuestion(G, text, varargin)
            self.init(G, 'matching_question', text, varargin{:});
        end


        function add_answer_pair(self, left, right, args)
            arguments
                self
                left {mustBeText}
                right {mustBeText}
                args.comment_when_incorrect {mustBeText} = ''
                args.figure_path {mustBeText} = ''
            end

            self.add_answer_pairs({{left, right, args.comment_when_incorrect, args.figure_path}});
        end


        function add_answer_pairs(self, array)
            arguments
                self
                array (:,1) cell
            end

            assert(length(array) > 0, 'Answer array cannot be empty.')

            % Iterate backward to force memory pre-allocation
            for i = length(array):-1:1
                data(i,1) = self.make_answer(array{i});
            end

            self.merge(data);
        end


        function add_distractors(self, array)
            arguments
                self
                array (:,1) cell
            end

            self.distractors = [self.distractors; array];
        end
    end

    methods (Access = protected)
        function A = make_answer(self, data)
            assert(length(data) >= 2, 'Answer pairs must have at least two arguments.')

            args = quizzes.pad_char_array(data, 4);

            % Check for figures
            if length(args{4}) > 0
                self.generator.enable_figures();
            end

            A = quizzes.MatchingAnswer(args{:});
        end
    end
end
