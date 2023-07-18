classdef NumericalAnswer < handle

    properties (Access = protected)
        supported_types = {
            'exact_answer',
            'precision_answer',
            'range_answer'
        };
    end

    properties (SetAccess = protected)
        type; comment

        % A key-value store conditional on the answer type.
        numerics = struct();
    end

    methods
        function self = NumericalAnswer(type, options)
            if nargin == 0
                return
            end

            assert(ismember(type, self.supported_types), 'Numerical answer type not supported.')

            self.type = type;
            self.comment = options.comment;

            if strcmp(type, 'exact_answer')
                self.numerics.exact = options.exact;
                self.numerics.error_margin = options.error_margin;
            end

            if strcmp(type, 'precision_answer')
                self.numerics.approximate = options.approximate;
                self.numerics.precision = options.precision;
            end

            if strcmp(type, 'range_answer')
                self.numerics.range_start = options.range_start;
                self.numerics.range_end = options.range_end;
            end
        end
    end
end
