"""Grader for MV2's pre-registered count of AI clauses in protective orders
(bar-ai-guidance, analysis/ai-protective-orders-prereg.md and its addendum).

Published before any post in the frame was read. It checks the coded data file against
the order texts (every call's quotation must appear word for word in the order text the
case cites), then grades P1-P4 from the pre-registration and P5-P6 from the addendum.
Standard library only. Apache-2.0. MV2 of Munim, Inc.; made with AI agents working in
his name. Information about public court documents, not legal advice.

Usage: python grade_aipo.py --data ai_protective_orders.json --texts <frame texts dir>
       [--sources <folder of order texts read at the source>] [--out results.json]
"""
import argparse
import difflib
import json
import os
import re
import sys

TESTS = ("BAN", "PUBLIC", "OPENNESS", "DATA", "CONTRACT", "NOTICE", "OTHER")
SETUP_A = ("permitted", "conditional", "forbidden", "unclear")
STATUSES = ("codable", "not_codable", "refusal")
PREDICTIONS = ("P1", "P2", "P3", "P4", "P5", "P6")
MIN_CODABLE = 10
RUN_WORDS = 25

QUOTE_MAP = str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"',
                           " ": " ", "–": "-", "—": "-", "…": "..."})
WORD_RE = re.compile(r"[a-z0-9]+")


def norm(text):
    """Comparable text: block-quote markers dropped, straight quotes, single spaces."""
    lines = []
    for line in text.splitlines():
        while line.startswith("> "):
            line = line[2:]
        lines.append(line)
    return " ".join(" ".join(lines).translate(QUOTE_MAP).split())


def extract(text, start, end):
    """The order text from the start anchor through the end anchor (both normalized).

    The start anchor must occur exactly once, so a span can never silently move."""
    t, s, e = norm(text), norm(start), norm(end)
    if not s or not e:
        raise ValueError("empty anchor")
    i = t.find(s)
    if i < 0:
        raise ValueError("start anchor not found: %r" % s[:80])
    if t.find(s, i + 1) >= 0:
        raise ValueError("start anchor not unique: %r" % s[:80])
    j = t.find(e, i)
    if j < 0:
        raise ValueError("end anchor not found after start: %r" % e[:80])
    return t[i:j + len(e)]


def quote_in(quote, text):
    """True if the quotation appears in text; '...' in a quotation skips words, in order."""
    pos, found = 0, False
    for part in norm(quote).split("..."):
        part = part.strip()
        if not part:
            continue
        k = text.find(part, pos)
        if k < 0:
            return False
        pos, found = k + len(part), True
    return found


def load_docs(texts_dir, sources_dir=""):
    """{'post:<id>': text} from the frame texts and {'src:<name>': text} from sources."""
    docs = {}
    for folder, prefix in ((texts_dir, "post:"), (sources_dir, "src:")):
        if folder and os.path.isdir(folder):
            for name in sorted(os.listdir(folder)):
                if name.endswith(".txt"):
                    with open(os.path.join(folder, name), encoding="utf-8") as f:
                        docs[prefix + name[:-4]] = f.read()
    return docs


def case_text(case, docs):
    parts = []
    for sp in case.get("spans") or []:
        doc = sp.get("doc")
        if doc not in docs:
            raise ValueError("unknown doc %r" % doc)
        parts.append(extract(docs[doc], sp.get("start", ""), sp.get("end", "")))
    return " ".join(parts)


def check_case(case, docs):
    """Problems with one coded case; an empty list means it passes."""
    cid = case.get("case_id", "?")
    status = case.get("status")
    if status not in STATUSES:
        return ["%s: bad status %r" % (cid, status)]
    if status == "not_codable":
        return [] if case.get("reason") else ["%s: not_codable needs a reason" % cid]
    try:
        text = case_text(case, docs)
    except ValueError as e:
        return ["%s: %s" % (cid, e)]
    if not text:
        return ["%s: no spans" % cid]
    if status == "refusal":
        return []
    probs = []
    if not case.get("court"):
        probs.append("%s: no court" % cid)
    tests = case.get("tests")
    if not isinstance(tests, dict) or not tests:
        probs.append("%s: no tests" % cid)
        tests = {}
    for t, q in tests.items():
        if t not in TESTS:
            probs.append("%s: unknown test %r" % (cid, t))
        elif not (q and quote_in(q, text)):
            probs.append("%s: quotation for %s not in the order text" % (cid, t))
    for key in ("self_hosting", "openness"):
        named = case.get(key + "_named")
        if named not in (True, False):
            probs.append("%s: %s_named must be true or false" % (cid, key))
        elif named and not quote_in(case.get(key + "_quote") or "", text):
            probs.append("%s: %s_quote not in the order text" % (cid, key))
    a = case.get("setup_a")
    if a not in SETUP_A:
        probs.append("%s: bad setup_a %r" % (cid, a))
    else:
        if not quote_in(case.get("setup_a_quote") or "", text):
            probs.append("%s: setup_a_quote not in the order text" % cid)
        if a == "unclear" and not case.get("setup_a_reason"):
            probs.append("%s: unclear setup_a needs a reason" % cid)
    return probs


def words(text):
    return WORD_RE.findall(text.lower())


def longest_run(a, b):
    """Length in words of the longest run that two word lists share."""
    return difflib.SequenceMatcher(None, a, b, autojunk=False).find_longest_match(
        0, len(a), 0, len(b)).size


def reuse(cod, texts, run_words=RUN_WORDS):
    """Pairs of codable cases whose AI text shares a run of at least run_words words."""
    ws = {c["case_id"]: words(texts.get(c["case_id"], "")) for c in cod}
    court = {c["case_id"]: c.get("court", "") for c in cod}
    ids = sorted(ws)
    best = {cid: 0 for cid in ids}
    pairs = []
    for i, x in enumerate(ids):
        for y in ids[i + 1:]:
            k = longest_run(ws[x], ws[y])
            best[x], best[y] = max(best[x], k), max(best[y], k)
            if k >= run_words:
                pairs.append({"a": x, "b": y, "words": k, "same_court": court[x] == court[y]})
    shared = sorted({p["a"] for p in pairs} | {p["b"] for p in pairs})
    return {"run_words": run_words, "pairs": pairs,
            "cross_court_pairs": [p for p in pairs if not p["same_court"]],
            "shared_cases": shared, "longest_run_by_case": best}


def pct(k, n):
    return round(100.0 * k / n, 1) if n else None


def held(ok):
    return "held" if ok else "failed"


def grade(cases, texts):
    """Counts and P1-P6 over codable cases; fewer than MIN_CODABLE is too small to grade."""
    cod = [c for c in cases if c["status"] == "codable"]
    n = len(cod)
    tests = {t: sum(1 for c in cod if t in c["tests"]) for t in TESTS}
    setup = {a: sum(1 for c in cod if c["setup_a"] == a) for a in SETUP_A}
    sh = sum(1 for c in cod if c["self_hosting_named"])
    op = sum(1 for c in cod if c["openness_named"])
    rs = reuse(cod, texts)
    out = {"counts": {"cases": len(cases), "codable": n,
                      "not_codable": sum(1 for c in cases if c["status"] == "not_codable"),
                      "refusals": sum(1 for c in cases if c["status"] == "refusal"),
                      "tests": tests, "self_hosting_named": sh, "openness_named": op,
                      "setup_a": setup},
           "percent": {"self_hosting_named": pct(sh, n), "DATA": pct(tests["DATA"], n),
                       "OPENNESS": pct(tests["OPENNESS"], n),
                       "setup_a_permitted": pct(setup["permitted"], n),
                       "setup_a_forbidden": pct(setup["forbidden"], n),
                       "shared_cases": pct(len(rs["shared_cases"]), n)},
           "reuse": rs}
    if n < MIN_CODABLE:
        out["predictions"] = {p: "too small to grade" for p in PREDICTIONS}
        return out
    open_permitted = sorted(c["case_id"] for c in cod
                            if "OPENNESS" in c["tests"] and c["setup_a"] == "permitted")
    out["openness_cases_permitting_a"] = open_permitted
    out["predictions"] = {
        "P1": held(5 * sh <= n),
        "P2": held(2 * tests["DATA"] >= n),
        "P3": held(4 * tests["OPENNESS"] <= n and not open_permitted),
        "P4": held(2 * setup["permitted"] >= n and 5 * setup["forbidden"] <= n),
        "P5": held(bool(rs["cross_court_pairs"])),
        "P6": held(3 * len(rs["shared_cases"]) <= n),
    }
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="Grade the AI protective-order count.")
    ap.add_argument("--data", required=True)
    ap.add_argument("--texts", required=True, help="frame texts folder (<post id>.txt)")
    ap.add_argument("--sources", default="", help="order texts read at the source (<name>.txt)")
    ap.add_argument("--out", default="")
    args = ap.parse_args(argv)
    with open(args.data, encoding="utf-8") as f:
        cases = json.load(f)["cases"]
    docs = load_docs(args.texts, args.sources)
    problems, texts, seen = [], {}, set()
    for c in cases:
        cid = c.get("case_id")
        if not cid or cid in seen:
            problems.append("missing or repeated case_id %r" % cid)
            continue
        seen.add(cid)
        p = check_case(c, docs)
        problems.extend(p)
        if not p and c["status"] == "codable":
            texts[cid] = case_text(c, docs)
    result = {"problems": problems}
    if not problems:
        result.update(grade(cases, texts))
        result["ai_text_by_case"] = texts
    body = json.dumps(result, indent=1, ensure_ascii=False)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(body + "\n")
    print(body)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
