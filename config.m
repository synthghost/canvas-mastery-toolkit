function out = config()
    % Absolute path to Python command line executable. To find this on Mac,
    % run "which python" or "which python3" in Terminal, then copy the full
    % path shown and paste it here. MATLAB does not always understand the
    % short-form "python" or "python3" commands, so this way is safer.
    out.python_command = '/usr/local/bin/python3';

    % Absolute path to the Python script (quiz_generator.py).
    out.python_script = '/path/to/quiz_generator.py';
end
