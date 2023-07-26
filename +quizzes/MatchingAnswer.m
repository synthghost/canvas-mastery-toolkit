classdef MatchingAnswer < handle

    properties (SetAccess = protected)
        left; right; comment
        figure_path
    end

    methods
        function self = MatchingAnswer(left, right, comment, figure_path)
            if nargin == 0
                return
            end

            self.left = left;
            self.right = right;
            self.comment = comment;
            self.figure_path = figure_path;
        end
    end
end
