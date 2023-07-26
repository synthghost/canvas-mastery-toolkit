classdef DropdownsQuestion < quizzes.Question

    methods
        function self = DropdownsQuestion(G, text, varargin)
            self.init(G, 'multiple_dropdowns_question', text, varargin{:});
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

            assert(length(array) > 0, 'Answer array cannot be empty.')

            % Iterate backward to force memory pre-allocation
            for i = length(array):-1:1
                list(i,1) = self.make_answer(blank_id, array{i}, weight);
            end

            self.merge(list);
        end


        function A = make_answer(self, blank_id, data, weight)
            args = quizzes.pad_char_array(data, 2);
            A = quizzes.FillAnswer(blank_id, weight, args{:});
        end
    end
end
