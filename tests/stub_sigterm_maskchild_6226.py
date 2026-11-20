#!/usr/bin/env python3
"""sys-nseyz4 review fixture: announce our pid + inherited SigIgn mask, then
hang. The test SIGTERMs us plain; dying on default disposition proves the
runner's spawn preexec un-blocked the captured SIGTERM across exec. Stdlib-
only; run by test_gateway_sigterm_detach_6226.py section E."""
import json
import os
import sys
import time
from pathlib import Path

Path(sys.argv[1]).write_text(json.dumps({"pid": os.getpid()}))
time.sleep(120)
