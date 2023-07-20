classdef DropdownsQuestion < Question

    methods
        function self = DropdownsQuestion(text, varargin)
            self.init('multiple_dropdowns_question', text, varargin{:});
        end


        function add_correct_answer(self, blank_id, text, comment)
            arguments
                self
                blank_id {mustBeText}
                text {mustBeText}
                comment {mustBeText} = ''
            end

            self.add_answers(blank_id, {{text, comment}}, 100);
        end


        function add_incorrect_answers(self, blank_id, array)
            self.add_answers(blank_id, array, 0);
        end
    end

    methods (Access = protected)
        function add_answers(self, blank_id, array, weight)
            arguments
                self
                blank_id {mustBeText}
                array (:,1) cell
                weight {mustBeNonnegative,mustBeScalarOrEmpty}
            end

            % Iterate backward to force memory pre-allocation
            for i = length(array):-1:1
                list(i,1) = self.make_answer(blank_id, array{i}, weight);
            end

            self.answers = [self.answers; list];
        end


        function A = make_answer(self, blank_id, data, weight)
            if ischar(data) || (iscell(data) && length(data) < 2)
                A = FillAnswer(blank_id, data, weight, '');
                return
            end

            A = FillAnswer(blank_id, char(data(1)), weight, char(data(2)));
        end
    end
end
