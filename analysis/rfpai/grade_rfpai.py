#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Grade the pre-registered study "How 2026 legal-aid RFPs treat a vendor's own use of AI".

MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents working in his name.
Code: Apache-2.0. Information about public procurement documents, not legal advice.

What it does, in order:
1. Loads the frozen coding (coding.json) and frame decisions (frame_decisions.json).
2. Re-fetches every source file named in the coding (live from lsntap.org, else the Wayback copy),
   checks its SHA-256 against the frozen value, and extracts text with pypdf (the collector's method).
3. Checks every quotation is in its file's text (after Unicode NFKC and whitespace folding only),
   that every code has a supporting quotation, and that each record has at least 1,000 characters.
4. Grades P1-P4 on the full frame and on the sensitivity frame (amendment 1), then, as an
   exploratory robustness check, re-grades the full frame with each borderline call flipped.
5. Writes results.json and results.md to --out.

Predictions (pre-registration, commit 17f6f85):
  P1 at most 30% of codable postings have a VENDOR_AI clause.
  P2 VENDOR_AI share for postings dated 1 Jul - 4 Nov 2026 is strictly higher than for 1 Jan - 30 Jun 2026;
     each half needs at least 5 codable postings, else "not testable".
  P3 no codable posting has a `ban` sub-code.
  P4 at least 25% of codable TECH postings have AI_IN_SCOPE; at least 5 TECH postings needed.
"""
import argparse
import copy
import hashlib
import io
import json
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.request
from pathlib import Path

UA = "MV2-Munim-research/1.0 (+mv2@munimtech.com)"
SUBCODES = ("disclose", "human_review", "data", "restrict", "ban")
MIN_CHARS = 1000


# ---------- text ----------
def norm(s: str) -> str:
    """NFKC (folds ligatures such as U+FB01) and collapse every run of whitespace to one space."""
    s = unicodedata.normalize("NFKC", s).replace("­", "")
    return re.sub(r"\s+", " ", s).strip()


def quote_in(quote: str, text: str) -> bool:
    q = norm(quote)
    return bool(q) and q in norm(text)


def pdf_text(data: bytes) -> str:
    from pypdf import PdfReader
    reader = PdfReader(io.BytesIO(data))
    return "".join(f"\n===== PAGE {i} =====\n{(p.extract_text() or '')}" for i, p in enumerate(reader.pages, 1))


# ---------- fetch ----------
def get(url: str, tries: int = 3, pause: float = 2.0):
    last = None
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.read(), None
        except urllib.error.HTTPError as e:
            last = f"HTTP {e.code}"
            if e.code in (403, 404, 410):
                break
        except Exception as e:  # recorded, not fatal
            last = f"{type(e).__name__}: {e}"
        time.sleep(pause * (k + 1))
    return None, last


def fetch_file(url: str):
    data, err = get(url)
    if data:
        return data, "live", None
    data2, err2 = get(f"https://web.archive.org/web/2026id_/{url}", tries=5, pause=5.0)
    if data2:
        return data2, "wayback", err
    return None, None, f"live: {err}; wayback: {err2}"


# ---------- dates ----------
def in_window(posted: str) -> bool:
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", posted):
        return "2026-01-01" <= posted <= "2026-11-04"
    if re.fullmatch(r"\d{4}-\d{2}", posted):
        return "2026-01" <= posted <= "2026-11"
    return False


def half(posted: str) -> str:
    """H1 = 1 Jan-30 Jun 2026, H2 = 1 Jul-4 Nov 2026. A month-only date uses its month."""
    return "H1" if int(posted[5:7]) <= 6 else "H2"


# ---------- grading ----------
def share(k: int, n: int):
    return None if n == 0 else k / n


def grade(records: list) -> dict:
    n = len(records)
    v = [r for r in records if r["vendor_ai"]]
    p1_share = share(len(v), n)
    res = {"n_codable": n, "n_vendor_ai": len(v)}
    res["P1"] = {"k": len(v), "n": n, "share": p1_share,
                 "result": "not testable" if n == 0 else ("held" if len(v) * 10 <= 3 * n else "failed")}
    h = {}
    for name in ("H1", "H2"):
        rs = [r for r in records if half(r["posted"]) == name]
        h[name] = {"n": len(rs), "k": sum(1 for r in rs if r["vendor_ai"])}
        h[name]["share"] = share(h[name]["k"], h[name]["n"])
    if h["H1"]["n"] < 5 or h["H2"]["n"] < 5:
        p2 = "not testable"
    else:
        # strictly higher, compared exactly: k2/n2 > k1/n1  <=>  k2*n1 > k1*n2
        p2 = "held" if h["H2"]["k"] * h["H1"]["n"] > h["H1"]["k"] * h["H2"]["n"] else "failed"
    res["P2"] = {"H1": h["H1"], "H2": h["H2"], "result": p2}
    bans = [r["id"] for r in records if "ban" in r.get("vendor_ai_subcodes", [])]
    res["P3"] = {"ban_records": bans, "result": "not testable" if n == 0 else ("held" if not bans else "failed")}
    tech = [r for r in records if r["tech"] == "TECH"]
    ais = [r for r in tech if r["ai_in_scope"]]
    if len(tech) < 5:
        p4 = "not testable"
    else:
        p4 = "held" if len(ais) * 4 >= len(tech) else "failed"
    res["P4"] = {"k": len(ais), "n": len(tech), "share": share(len(ais), len(tech)), "result": p4}
    sub = {s: sum(1 for r in v if s in r.get("vendor_ai_subcodes", [])) for s in SUBCODES}
    res["subcode_counts"] = sub
    res["vendor_ai_ids"] = [r["id"] for r in v]
    res["ai_in_scope_ids"] = [r["id"] for r in records if r["ai_in_scope"]]
    return res


def flipped(records: list, rid: str, b: dict) -> list:
    out = copy.deepcopy(records)
    for r in out:
        if r["id"] == rid:
            r[b["field"]] = b["alt"]
            if b["field"] == "vendor_ai":
                r["vendor_ai_subcodes"] = list(b.get("alt_subcodes", []))
    return out


def robustness(records: list) -> list:
    base = grade(records)
    rows = []
    for r in records:
        for b in r.get("borderline", []):
            g = grade(flipped(records, r["id"], b))
            changed = {p: (base[p]["result"], g[p]["result"]) for p in ("P1", "P2", "P3", "P4")
                       if base[p]["result"] != g[p]["result"]}
            rows.append({"record": r["id"], "field": b["field"], "alt": b["alt"], "changes": changed})
    return rows


# ---------- verification ----------
def check_structure(coding: dict) -> list:
    """Problems that do not need the source texts."""
    probs = []
    ids = [r["id"] for r in coding["records"]]
    if len(ids) != len(set(ids)):
        probs.append("duplicate record ids")
    for r in coding["records"]:
        rid = r["id"]
        if not in_window(r["posted"]):
            probs.append(f"{rid}: posted {r['posted']} outside the window")
        if r["tech"] not in ("TECH", "NON_TECH"):
            probs.append(f"{rid}: bad tech value")
        codes = {c for q in r["quotes"] for c in q["codes"]}
        if r["vendor_ai"]:
            if not r["vendor_ai_subcodes"]:
                probs.append(f"{rid}: VENDOR_AI without sub-code")
            for s in r["vendor_ai_subcodes"]:
                if s not in SUBCODES:
                    probs.append(f"{rid}: unknown sub-code {s}")
                if f"VENDOR_AI:{s}" not in codes:
                    probs.append(f"{rid}: sub-code {s} has no quotation")
        elif r["vendor_ai_subcodes"] or any(c.startswith("VENDOR_AI:") for c in codes):
            probs.append(f"{rid}: VENDOR_AI quotes or sub-codes on a record coded without VENDOR_AI")
        if r["ai_in_scope"] and "AI_IN_SCOPE" not in codes:
            probs.append(f"{rid}: AI_IN_SCOPE has no quotation")
        if not r["ai_in_scope"] and "AI_IN_SCOPE" in codes:
            probs.append(f"{rid}: AI_IN_SCOPE quotation on a record coded without it")
        if r["seed_only"] and r["sensitivity_codable"]:
            probs.append(f"{rid}: seed-only record marked codable in the sensitivity frame")
        for f in r["files"]:
            if not re.fullmatch(r"[0-9a-f]{64}", f["sha256"]):
                probs.append(f"{rid}: bad sha256")
        for q in r["quotes"]:
            if not (0 <= q["file"] < len(r["files"])):
                probs.append(f"{rid}: quote points to a missing file")
        for b in r.get("borderline", []):
            if b["field"] not in ("vendor_ai", "tech", "ai_in_scope"):
                probs.append(f"{rid}: bad borderline field")
    return probs


def check_texts(coding: dict, texts: dict) -> list:
    """texts: {url: text}. Returns per-quote and per-record checks."""
    rows = []
    for r in coding["records"]:
        chars = sum(len(texts.get(f["url"], "").strip()) for f in r["files"])
        rows.append({"record": r["id"], "check": "codable_chars", "value": chars, "ok": chars >= MIN_CHARS})
        for i, q in enumerate(r["quotes"]):
            t = texts.get(r["files"][q["file"]]["url"], "")
            rows.append({"record": r["id"], "check": f"quote_{i}", "codes": q["codes"], "ok": quote_in(q["text"], t)})
    return rows


def fmt(x):
    return "n/a" if x is None else f"{100 * x:.1f}%"


def write_md(path: Path, res: dict):
    L = ["# Results: how 2026 legal-aid RFPs treat a vendor's own use of AI", "",
         "Machine-written by grade_rfpai.py (Apache-2.0). MV2 of Munim, Inc.; made with AI agents working in his name. Not legal advice.", "",
         f"- Coding file sha256: `{res['coding_sha256']}`",
         f"- Files fetched: {res['files_ok']} of {res['files_total']} with matching SHA-256; quotations found: {res['quotes_ok']} of {res['quotes_total']}; structure problems: {len(res['structure_problems'])}",
         f"- Verified: **{res['verified']}**", ""]
    for frame in ("full", "sensitivity"):
        g = res[frame]
        L += [f"## {frame.capitalize()} frame ({g['n_codable']} codable postings)", "",
              "| | Result | Numbers |", "|---|---|---|",
              f"| P1 VENDOR_AI share <= 30% | {g['P1']['result']} | {g['P1']['k']}/{g['P1']['n']} = {fmt(g['P1']['share'])} |",
              f"| P2 H2 share > H1 share | {g['P2']['result']} | H1 {g['P2']['H1']['k']}/{g['P2']['H1']['n']} = {fmt(g['P2']['H1']['share'])}; H2 {g['P2']['H2']['k']}/{g['P2']['H2']['n']} = {fmt(g['P2']['H2']['share'])} |",
              f"| P3 no `ban` | {g['P3']['result']} | ban records: {', '.join(g['P3']['ban_records']) or 'none'} |",
              f"| P4 AI_IN_SCOPE among TECH >= 25% | {g['P4']['result']} | {g['P4']['k']}/{g['P4']['n']} = {fmt(g['P4']['share'])} |",
              "", f"VENDOR_AI records: {', '.join(g['vendor_ai_ids']) or 'none'}; sub-codes: {g['subcode_counts']}", ""]
    L += ["## Exploratory: each borderline call flipped (full frame)", "", "| Record | Field -> alt | Predictions that change |", "|---|---|---|"]
    for row in res["robustness"]:
        ch = "; ".join(f"{p}: {a} -> {b}" for p, (a, b) in row["changes"].items()) or "none"
        L.append(f"| {row['record']} | {row['field']} -> {row['alt']} | {ch} |")
    bad = [c for c in res["text_checks"] if not c["ok"]]
    L += ["", "## Failed checks", ""] + ([f"- {c}" for c in bad] or ["- none"])
    path.write_text("\n".join(L) + "\n", encoding="utf-8")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--coding", default="coding.json")
    ap.add_argument("--out", default="out")
    args = ap.parse_args(argv)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    raw = Path(args.coding).read_bytes()
    coding = json.loads(raw.decode("utf-8"))
    res = {"coding_sha256": hashlib.sha256(raw).hexdigest(), "graded_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    res["structure_problems"] = check_structure(coding)

    texts, fetch_rows = {}, []
    for r in coding["records"]:
        for f in r["files"]:
            if f["url"] in texts:
                continue
            data, src, err = fetch_file(f["url"])
            row = {"url": f["url"], "source": src, "error": err}
            if data:
                row["sha256"] = hashlib.sha256(data).hexdigest()
                row["sha_ok"] = row["sha256"] == f["sha256"]
                try:
                    texts[f["url"]] = pdf_text(data)
                except Exception as ex:
                    row["text_error"] = f"{type(ex).__name__}: {ex}"
                    texts[f["url"]] = ""
            else:
                row["sha_ok"] = False
                texts[f["url"]] = ""
            fetch_rows.append(row)
    res["fetch"] = fetch_rows
    res["files_total"] = len(fetch_rows)
    res["files_ok"] = sum(1 for x in fetch_rows if x["sha_ok"])
    res["text_checks"] = check_texts(coding, texts)
    q = [c for c in res["text_checks"] if c["check"].startswith("quote_")]
    res["quotes_total"], res["quotes_ok"] = len(q), sum(1 for c in q if c["ok"])
    res["verified"] = (not res["structure_problems"] and res["files_ok"] == res["files_total"]
                       and all(c["ok"] for c in res["text_checks"]))

    full = list(coding["records"])
    sens = [r for r in full if r["sensitivity_codable"]]
    res["full"] = grade(full)
    res["sensitivity"] = grade(sens)
    res["differs"] = {p: [res["full"][p]["result"], res["sensitivity"][p]["result"]] for p in ("P1", "P2", "P3", "P4")
                      if res["full"][p]["result"] != res["sensitivity"][p]["result"]}
    res["robustness"] = robustness(full)
    (out / "results.json").write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    write_md(out / "results.md", res)
    print(json.dumps({"verified": res["verified"], "files_ok": f"{res['files_ok']}/{res['files_total']}",
                      "quotes_ok": f"{res['quotes_ok']}/{res['quotes_total']}",
                      "full": {p: res["full"][p]["result"] for p in ("P1", "P2", "P3", "P4")},
                      "sensitivity": {p: res["sensitivity"][p]["result"] for p in ("P1", "P2", "P3", "P4")},
                      "differs": res["differs"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
