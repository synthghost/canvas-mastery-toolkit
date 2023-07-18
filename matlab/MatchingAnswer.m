classdef MatchingAnswer < handle

    properties (SetAccess = protected)
        left; right; comment
    end

    methods
        function self = MatchingAnswer(left, right, comment)
            if nargin == 0
                return
            end

            self.left = left;
            self.right = right;
            self.comment = comment;
        end
    end
end
