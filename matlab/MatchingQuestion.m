classdef MatchingQuestion < Question

    properties (SetAccess = protected)
        % The list of incorrect values to show amonst the correct ones.
        distractors
    end

    methods
        function self = MatchingQuestion(text, varargin)
            self.init('matching_question', text, varargin{:});
        end


        function add_answer_pair(self, left, right, incorrect_comment)
            arguments
                self
                left {mustBeText}
                right {mustBeText}
                incorrect_comment {mustBeText} = ''
            end

            self.add_answer_pairs({{left, right, incorrect_comment}});
        end


        function add_answer_pairs(self, array)
            arguments
                self
                array (:,1) cell
            end

            % Iterate backward to force memory pre-allocation
            for i = length(array):-1:1
                list(i,1) = self.make_answer(array{i});
            end

            self.answers = [self.answers; list];
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
            if length(data) < 3
                data{3} = '';
            end

            A = MatchingAnswer(char(data(1)), char(data(2)), char(data(3)));
        end
    end
end
