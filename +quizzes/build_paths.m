function [data_path, figure_dir] = build_paths(fullpath, args)
    arguments
        fullpath {mustBeText}
        args.data {mustBeText} = 'data'
        args.figures {mustBeText} = 'figures'
    end

    % Determine path components;
    [root, file] = fileparts(fullpath);

    % Set paths accordingly.
    data_dir = fullfile(root, args.data);
    data_path = fullfile(data_dir, [file, '.json']);
    figure_dir = fullfile(root, args.figures, file);

    % Create directories as necessary.
    if ~isfolder(data_dir)
        mkdir(data_dir);
    end
    if nargout > 1 && ~isfolder(figure_dir)
        mkdir(figure_dir);
    end
end
