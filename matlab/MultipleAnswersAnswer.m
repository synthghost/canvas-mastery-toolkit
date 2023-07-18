classdef MultipleAnswersAnswer < handle

    properties (SetAccess = protected)
        text; weight; comment
    end

    methods
        function self = MultipleAnswersAnswer(text, weight, comment)
            if nargin == 0
                return
            end

            self.text = text;
            self.weight = min(max(0, weight), 100);
            self.comment = comment;
        end
    end
end
