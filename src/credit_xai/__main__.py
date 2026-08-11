"""Allow `python -m credit_xai` as an alias for `python -m credit_xai.cli`."""

import sys

from credit_xai.cli import main

if __name__ == "__main__":
    sys.exit(main())
