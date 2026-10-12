"""Entry point: `python scripts/ingest --album <slug> --src <path>` (dry run by default)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ingest import main  # noqa: E402

sys.exit(main())
