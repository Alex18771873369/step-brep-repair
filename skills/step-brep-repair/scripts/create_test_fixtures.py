#!/usr/bin/env python3
"""Optional smoke-test fixtures, created in a new empty directory only."""
import argparse
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('output_directory')
a = p.parse_args()
out = Path(a.output_directory).resolve()
out.mkdir(parents=False, exist_ok=False)
import FreeCAD
import Part
Part.makeBox(10, 20, 30).exportStep(str(out / 'box.step'))
Part.makePlane(10, 20).exportStep(str(out / 'open_face.step'))
print('Created STEP test fixtures in', out)
