classdef NumericalQuestion < quizzes.Question

    methods
        function self = NumericalQuestion(G, text, varargin)
            self.init(G, 'numerical_question', text, varargin{:});
        end


        function add_exact_answer(self, exact, error_margin, correct_comment)
            arguments
                self
                exact {mustBeNumeric}
                error_margin {mustBeNumeric}
                correct_comment {mustBeText} = ''
            end

            self.add_answer('exact_answer', exact=exact, error_margin=error_margin, comment=correct_comment);
        end


        function add_precision_answer(self, approximate, precision, correct_comment)
            arguments
                self
                approximate {mustBeNumeric}
                precision {mustBeNumeric}
                correct_comment {mustBeText} = ''
            end

            self.add_answer('precision_answer', approximate=approximate, precision=precision, comment=correct_comment);
        end


        function add_range_answer(self, range_start, range_end, correct_comment)
            arguments
                self
                range_start {mustBeNumeric}
                range_end {mustBeNumeric}
                correct_comment {mustBeText} = ''
            end

            self.add_answer('range_answer', range_start=range_start, range_end=range_end, comment=correct_comment);
        end
    end

    methods (Access = protected)
        function add_answer(self, type, args)
            arguments
                self
                type {mustBeText}
                args.exact = 0
                args.error_margin = 0
                args.approximate = 0
                args.precision = 0
                args.range_start = 0
                args.range_end = 0
                args.comment = ''
            end

            A = quizzes.NumericalAnswer(type, args);

            self.answers = {A};
        end
    end
end
