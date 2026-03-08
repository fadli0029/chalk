import sys
import warnings

def _main_deprecated():
    warnings.warn(
        "'chalk-extract' is deprecated. Please use 'chalk extract' instead.",
        DeprecationWarning,
        stacklevel=2
    )
    # Assuming the original _main logic is imported or redefined here
    # In a real scenario, preserve the logic that was previously in _main
    run(*sys.argv[1:])

def run(pdf, output):
    # Core extraction logic here
    pass
