function out = pad_char_array(array, len)
    if ischar(array)
        array = {array};
    end
    pad = cell(1, len);
    [pad{1:length(array)}] = deal(array{:});
    out = cellfun(@(x) char(x), pad, UniformOutput=false);
end
