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
        function self = NumericalAnswer(type, args)
            if nargin == 0
                return
            end

            assert(ismember(type, self.supported_types), 'Numerical answer type not supported.')

            self.type = type;
            self.comment = args.comment;

            if strcmp(type, 'exact_answer')
                self.numerics.exact = args.exact;
                self.numerics.error_margin = args.error_margin;
            end

            if strcmp(type, 'precision_answer')
                self.numerics.approximate = args.approximate;
                self.numerics.precision = args.precision;
            end

            if strcmp(type, 'range_answer')
                self.numerics.range_start = args.range_start;
                self.numerics.range_end = args.range_end;
            end
        end
    end
end
