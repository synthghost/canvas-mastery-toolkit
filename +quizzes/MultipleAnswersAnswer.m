classdef MultipleAnswersAnswer < handle

    properties (SetAccess = protected)
        weight; text; comment
        figure_path
    end

    methods
        function self = MultipleAnswersAnswer(weight, text, comment, figure_path)
            if nargin == 0
                return
            end

            self.weight = min(max(0, weight), 100);
            self.text = text;
            self.comment = comment;
            self.figure_path = figure_path;
        end
    end
end
