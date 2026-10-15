"""Render an English blazon with Emma's Sodacan-arms-svg-generator, used read-only.

The generator repo is imported from its own folder (never written: bytecode is off) and the SVG
is written here. Usage: python tools/generator_render.py "Or, a lion rampant azure" out.svg
Prints whether the blazon was fully parsed and the generator's commit.
"""
import subprocess, sys
from pathlib import Path

sys.dont_write_bytecode = True
GEN = Path(r"C:\Users\Emma\Documents\GitHub\Sodacan-arms-svg-generator")
sys.path.insert(0, str(GEN))
from arms.blazon import en  # noqa: E402
from arms.render import render  # noqa: E402


def generator_commit():
    return subprocess.run(["git", "-C", str(GEN), "rev-parse", "--short", "HEAD"],
                          capture_output=True, text=True).stdout.strip()


def build(blazon):
    esc = en.parse(blazon)
    return render(esc), en.fully_parsed(esc)


if __name__ == "__main__":
    svg, full = build(sys.argv[1])
    Path(sys.argv[2]).write_text(svg, encoding="utf-8")
    print("fully parsed:", full, "| generator", generator_commit())
