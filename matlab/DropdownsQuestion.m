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

            self.add_answer(blank_id, text, 100, comment);
        end


        function add_incorrect_answer(self, blank_id, text, comment)
            arguments
                self
                blank_id {mustBeText}
                text {mustBeText}
                comment {mustBeText} = ''
            end

            self.add_answer(blank_id, text, 0, comment);
        end
    end

    methods (Access = protected)
        function add_answer(self, blank_id, text, weight, comment)
            A = DropdownsAnswer(blank_id, text, weight, comment);

            self.answers = [self.answers; A];
        end
    end
end
