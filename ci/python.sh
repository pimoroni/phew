SCRIPT_PATH=${BASH_SOURCE-$0}
SCRIPT_PATH=$(dirname "$SCRIPT_PATH")
SCRIPT_PATH=$(realpath "$SCRIPT_PATH")

function qa_prepare_all {
    pip install ruff codespell
}

function qa_check {
    ruff check --config "$SCRIPT_PATH/ruff.toml" "$@"
}

function qa_fix {
    ruff check --config "$SCRIPT_PATH/ruff.toml" --fix "$@"
}

function qa_phew_check {
    qa_check __init__.py phew/
}

function qa_phew_fix {
    qa_fix __init__.py phew/
}

function qa_examples_check {
    qa_check examples/
}

function qa_examples_fix {
    qa_fix examples/
}

function qa_tests_check {
    qa_check tests/
}

function qa_tests_fix {
    qa_fix tests/
}

function qa_spelling_check {
    codespell
}

function qa_test {
    python3 -m unittest discover -s tests -p "*_test.py" -v
}
