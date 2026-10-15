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
import arms.render as R  # noqa: E402
from arms.render import render  # noqa: E402

_sources = []
_orig_pick = R._pick


def _pick(comp, exclude_source):  # same choice as the generator's; also records the source file
    got = _orig_pick(comp, exclude_source)
    if got is not None and got.get("source"):
        _sources.append(got["source"])
    return got


R._pick = _pick


class _Layers(dict):  # a charge drawing looked up by its source file: record that file
    def __getitem__(self, key):
        _sources.append(key)
        return dict.__getitem__(self, key)


def _recording(loader, per_house=False):
    cache = {}

    def wrapped():
        if "v" not in cache:
            data = loader()
            for d in (data.values() if per_house else [data]):
                if isinstance(d, dict) and "layers" in d:
                    d["layers"] = _Layers(d["layers"])
            cache["v"] = data
        return cache["v"]
    return wrapped


R.charge_instances = _recording(R.charge_instances)
R.house_charges = _recording(R.house_charges, per_house=True)


def generator_commit():
    return subprocess.run(["git", "-C", str(GEN), "rev-parse", "--short", "HEAD"],
                          capture_output=True, text=True).stdout.strip()


def build(blazon, detail=False):
    """SVG and whether the blazon parsed fully; with detail, also the Commons files whose
    drawings were reused and the generator's notes on what it could not draw."""
    _sources.clear()
    R.NOTES.clear()
    esc = en.parse(blazon)
    svg = render(esc)
    if detail:
        return svg, en.fully_parsed(esc), sorted(set(_sources)), list(R.NOTES)
    return svg, en.fully_parsed(esc)


if __name__ == "__main__":
    svg, full = build(sys.argv[1])
    Path(sys.argv[2]).write_text(svg, encoding="utf-8")
    print("fully parsed:", full, "| generator", generator_commit())
