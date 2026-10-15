"""Which order.life people have a coat of arms on Wikidata (P94), and in what format.

Reads the person table of the inochi-no-michikyo repo (read-only) and writes
data_lake/downloads/order-life-arms/person_arms.tsv: order.life qid, label, wikidata qid,
P94 file name, extension. Raster ones (png/jpg/gif) are vectorization candidates.
"""
import csv, json, sys, time, urllib.parse, urllib.request
from pathlib import Path

PERSONS = Path(r"C:\Users\Emma\Documents\GitHub\inochi-no-michikyo\order.life\wikibase\analysis\persons.tsv")
OUT = Path(__file__).resolve().parent.parent / "data_lake/downloads/order-life-arms/person_arms.tsv"
UA = "agentic-vectorization/0.1 (emma@topazcomputing.com)"
SPARQL = "https://query.wikidata.org/sparql"


def query(qids):
    values = " ".join("wd:" + q for q in qids)
    q = f"SELECT ?p ?img WHERE {{ VALUES ?p {{ {values} }} ?p wdt:P94 ?img }}"
    data = urllib.parse.urlencode({"query": q, "format": "json"}).encode()
    for attempt in range(5):
        try:
            req = urllib.request.Request(SPARQL, data=data, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.load(r)["results"]["bindings"]
        except Exception as e:  # rate limit or timeout: back off
            print("retry", attempt, e, file=sys.stderr)
            time.sleep(10 * (attempt + 1))
    raise RuntimeError("SPARQL failed")


def main():
    rows = list(csv.DictReader(PERSONS.open(encoding="utf-8"), delimiter="\t"))
    by_wd = {}
    for r in rows:
        if r["wikidata_qid"]:
            by_wd.setdefault(r["wikidata_qid"], []).append(r)
    wds = sorted(by_wd)
    out = []
    for i in range(0, len(wds), 400):
        for b in query(wds[i:i + 400]):
            wd = b["p"]["value"].rsplit("/", 1)[1]
            name = urllib.parse.unquote(b["img"]["value"].rsplit("/", 1)[1]).replace("_", " ")
            for r in by_wd[wd]:
                out.append((r["qid"], r["label"], wd, name, name.rsplit(".", 1)[-1].lower()))
        print(i, len(out), file=sys.stderr)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["qid", "label", "wikidata_qid", "file", "ext"])
        w.writerows(sorted(out, key=lambda t: int(t[0][1:])))


if __name__ == "__main__":
    main()
