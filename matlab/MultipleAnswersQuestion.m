classdef MultipleAnswersQuestion < Question

    methods
        function self = MultipleAnswersQuestion(text, varargin)
            self.init('multiple_answers_question', text, varargin{:});
        end


        function add_correct_answers(self, array)
            self.add_answers(array, 100);
        end


        function add_incorrect_answers(self, array)
            self.add_answers(array, 0);
        end


        % Should these be correct sometimes?
        function add_catchall_answer(self, text, comment)
            arguments
                self
                text {mustBeText}
                comment {mustBeText} = ''
            end

            self.add_answers({{text, comment}}, 0);
        end
    end

    methods (Access = protected)
        function add_answers(self, array, weight)
            arguments
                self
                array (:,1) cell
                weight {mustBeNonnegative,mustBeScalarOrEmpty}
            end

            % Iterate backward to force memory pre-allocation
            for i = length(array):-1:1
                list(i,1) = self.make_answer(array{i}, weight);
            end

            self.answers = [self.answers; list];
        end


        function A = make_answer(self, data, weight)
            if ischar(data) || (iscell(data) && length(data) < 2)
                A = MultipleAnswersAnswer(data, weight, '');
                return
            end

            A = MultipleAnswersAnswer(char(data(1)), weight, char(data(2)));
        end
    end
end
