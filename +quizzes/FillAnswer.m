classdef FillAnswer < handle

    properties (SetAccess = protected)
        blank_id
        weight; text; comment;
    end

    methods
        function self = FillAnswer(blank_id, weight, text, comment)
            if nargin == 0
                return
            end

            self.blank_id = blank_id;
            self.weight = min(max(0, weight), 100);
            self.text = text;
            self.comment = comment;
        end
    end
end
