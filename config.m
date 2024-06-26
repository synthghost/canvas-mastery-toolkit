function out = config()
    [base_path] = fileparts(mfilename('fullpath'));

    loadenv(fullfile(base_path, '.env'));

    % Absolute path to the Python command line executable. To
    % find this on Mac, run "which python" or "which python3" in
    % Terminal. MATLAB does not always understand the short-form
    % "python" or "python3" commands. An absolute path is safer.
    out.python_command = getenv('PYTHON_COMMAND');

    % Absolute path to the Python uploader (quiz_generator.py).
    out.python_uploader = fullfile(base_path, 'quiz_generator.py');
end
