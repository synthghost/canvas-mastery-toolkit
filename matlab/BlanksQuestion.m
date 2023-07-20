classdef BlanksQuestion < Question

    methods
        function self = BlanksQuestion(text, varargin)
            self.init('fill_in_multiple_blanks_question', text, varargin{:});
        end


        function add_correct_answer(self, blank_id, text, comment)
            arguments
                self
                blank_id {mustBeText}
                text {mustBeText}
                comment {mustBeText} = ''
            end

            self.add_correct_answers(blank_id, {{text, comment}});
        end


        function add_correct_answers(self, blank_id, array)
            arguments
                self
                blank_id {mustBeText}
                array (:,1) cell
            end

            % Iterate backward to force memory pre-allocation
            for i = length(array):-1:1
                list(i,1) = self.make_answer(blank_id, array{i});
            end

            self.answers = [self.answers; list];
        end
    end

    methods (Access = protected)
        function A = make_answer(self, blank_id, data)
            % Answers specified for blanks questions are always correct
            weight = 100;

            if ischar(data) || (iscell(data) && length(data) < 2)
                A = FillAnswer(blank_id, data, weight, '');
                return
            end

            A = FillAnswer(blank_id, char(data(1)), weight, char(data(2)));
        end
    end
end
