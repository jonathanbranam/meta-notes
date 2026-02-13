#!/usr/bin/env bash
# run_tests.sh - Run vader.vim tests for meta-notes plugin

# Default values
VADER_PATH="${VADER_PATH:-$HOME/.vim/pack/testing/start/vader.vim}"
PLUGIN_PATH="${PLUGIN_PATH:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)}"
TEST_PATH="${TEST_PATH:-test/*.vader}"
VIM_CMD="${VIM_CMD:-vim}"

# Usage information
usage() {
    cat << EOF
Usage: $0 [OPTIONS] [TEST_FILES]

Run vader.vim tests for the meta-notes plugin.

OPTIONS:
    -h, --help              Show this help message
    -v, --vader PATH        Path to vader.vim (default: ~/.vim/pack/testing/start/vader.vim)
    -p, --plugin PATH       Path to plugin root (default: current directory)
    -i, --interactive       Run in interactive mode (without !)
    -q, --quiet             Show only summary

EXAMPLES:
    # Run all tests
    $0

    # Run specific test file
    $0 test/open_note.vader

    # Run with custom vader path
    $0 --vader ~/vim-plugins/vader.vim

    # Run in interactive mode
    $0 --interactive

ENVIRONMENT VARIABLES:
    VADER_PATH     Path to vader.vim installation
    PLUGIN_PATH    Path to meta-notes plugin root
    TEST_PATH      Test files to run (default: test/*.vader)
    VIM_CMD        Vim command to use (default: vim)
EOF
    exit 0
}

# Parse arguments
INTERACTIVE=false
QUIET=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            ;;
        -v|--vader)
            VADER_PATH="$2"
            shift 2
            ;;
        -p|--plugin)
            PLUGIN_PATH="$2"
            shift 2
            ;;
        -i|--interactive)
            INTERACTIVE=true
            shift
            ;;
        -q|--quiet)
            QUIET=true
            shift
            ;;
        -*)
            echo "Unknown option: $1"
            usage
            ;;
        *)
            TEST_PATH="$1"
            shift
            ;;
    esac
done

# Verify vader.vim exists
if [[ ! -d "$VADER_PATH" ]]; then
    echo "Error: vader.vim not found at: $VADER_PATH"
    echo "Install it with:"
    echo "  mkdir -p ~/.vim/pack/testing/start"
    echo "  git clone https://github.com/junegunn/vader.vim.git ~/.vim/pack/testing/start/vader.vim"
    exit 1
fi

# Verify plugin path exists
if [[ ! -d "$PLUGIN_PATH" ]]; then
    echo "Error: Plugin path not found: $PLUGIN_PATH"
    exit 1
fi

# Build the vim command
if [[ "$INTERACTIVE" == "true" ]]; then
    VADER_CMD="Vader"
else
    VADER_CMD="Vader!"
fi

# Run the tests
if [[ "$QUIET" == "true" ]]; then
    "$VIM_CMD" -es -Nu <(cat << EOF
filetype off
set rtp+=$VADER_PATH
set rtp+=$PLUGIN_PATH
filetype plugin indent on
syntax enable
EOF
) +${VADER_CMD} "$TEST_PATH" 2>&1 | grep -E "(Starting Vader|Success|Elapsed)"
else
    "$VIM_CMD" -es -Nu <(cat << EOF
filetype off
set rtp+=$VADER_PATH
set rtp+=$PLUGIN_PATH
filetype plugin indent on
syntax enable
EOF
) +${VADER_CMD} "$TEST_PATH" 2>&1
fi

# Capture exit code
EXIT_CODE=${PIPESTATUS[0]}

exit $EXIT_CODE
