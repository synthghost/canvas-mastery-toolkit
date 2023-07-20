classdef FillAnswer < handle

    properties (SetAccess = protected)
        blank_id
        text; weight; comment;
    end

    methods
        function self = FillAnswer(blank_id, text, weight, comment)
            if nargin == 0
                return
            end

            self.blank_id = blank_id;
            self.text = text;
            self.weight = min(max(0, weight), 100);
            self.comment = comment;
        end
    end
end
