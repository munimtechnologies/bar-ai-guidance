#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 MV2, Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name.
"""MSPB fabricated-citation census 1.0.0 (pre-registered; see PLAN.md next to this file).

Pure functions only: manifest parsing, frame building, text classification, the database
check and grading. Fetching lives in run_job.py. Standard library only. Information about
public decisions of a federal agency, not legal advice.
"""
from __future__ import annotations

import csv
import datetime as dt
import hashlib
import io
import json
import re
import urllib.parse

VERSION = "1.0.0"
UA = "MV2-Munim-research/1.0 (mv2@munimtech.com)"
START = "2024-01-01"          # first issued date in the frame
END = "2026-11-09"            # last issued date in the frame
SPLIT = "2025-07-01"          # P3: early period is START..SPLIT-1, late period is SPLIT..END
BASE = "https://www.mspb.gov/decisions/"
# The two listing manifests the job must read, then four that may be stale or missing.
MAIN_MANIFESTS = (
    "nonprecedential/NonPrecedentialDecisions_Manifest.json",
    "precedential/PrecedentialDecisions_Manifest.json",
)
EXTRA_MANIFESTS = (
    "nonprecedential/NonPrecedentialDecisions_Manifest_Table.json",
    "nonprecedential/NonPrecedentialDecisions_Manifest-updmar2025.json",
    "precedential/PrecedentialDecisions_Manifest_Table.json",
    "precedential/PrecedentialDecisions_Manifest_updMar2025.json",
)
MIN_FRAME = 500               # fewer decisions in the frame: stop before any PDF is fetched
MAX_FRAME = 4500              # more decisions in the frame: stop before any PDF is fetched
READABLE_CHARS = 300
HEAD_CHARS = 4000             # caption, representation block and heading
PROXIMITY = 2000              # characters between an AI term and a fabricated-citation phrase


def now():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# --- manifests -----------------------------------------------------------------------------
def parse_date(value):
    """ISO date from a manifest ISSUED_DATE ('2026/11/09', '2025/3/14', '2025-03-14',
    '03/14/2025'); None if it cannot be read."""
    s = (value or "").strip()
    m = re.match(r"^(\d{4})[/-](\d{1,2})[/-](\d{1,2})(?!\d)", s)
    if m:
        y, mo, d = m.groups()
    else:
        m = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{4})(?!\d)", s)
        if not m:
            return None
        mo, d, y = m.groups()
    try:
        return dt.date(int(y), int(mo), int(d)).isoformat()
    except ValueError:
        return None


def collection_of(manifest_path):
    return manifest_path.split("/", 1)[0]


def pdf_url(collection, file_name):
    return BASE + collection + "/" + urllib.parse.quote(file_name, safe="")


def row_id(collection, file_name):
    """Stable public id: anyone can recompute it from the manifest."""
    key = "%s/%s" % (collection, (file_name or "").strip().lower())
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:12]


def parse_manifest(body, manifest_path):
    """(rows, stats) for one manifest. body: bytes or str of {"DOCUMENT_TYPE": ..., "data": [...]}."""
    if isinstance(body, bytes):
        try:
            body = body.decode("utf-8-sig")
        except UnicodeDecodeError:
            body = body.decode("latin-1")
    data = json.loads(body)
    coll = collection_of(manifest_path)
    rows, no_file, bad_date = [], 0, 0
    for x in (data.get("data") or []) if isinstance(data, dict) else []:
        if not isinstance(x, dict):
            continue
        fname = (x.get("FILE_NAME") or "").strip()
        if not fname:
            no_file += 1
            continue
        date = parse_date(x.get("ISSUED_DATE"))
        if date is None:
            bad_date += 1
        rows.append({
            "row_id": row_id(coll, fname),
            "file_name": fname,
            "collection": coll,
            "date": date,
            "docket": re.sub(r"\s+", " ", x.get("DOCKET_NBR") or "").strip()[:200],
            "agency": re.sub(r"\s+", " ", x.get("AGENCY") or "").strip()[:120],
            "doctitle": (x.get("DOCTITLE") or "").strip()[:80],
        })
    dates = sorted(r["date"] for r in rows if r["date"])
    stats = {"manifest": manifest_path, "document_type": data.get("DOCUMENT_TYPE") if isinstance(data, dict) else None,
             "rows": len(rows), "no_file_name": no_file, "bad_date": bad_date,
             "earliest": dates[0] if dates else None, "latest": dates[-1] if dates else None}
    return rows, stats


def in_window(date):
    return bool(date) and START <= date <= END


def merge(frame, rows, manifest_path):
    """Adds in-window rows to frame (dict keyed by row_id; first manifest read wins).
    Returns the number of in-window rows in this manifest."""
    n = 0
    for r in rows:
        if not in_window(r["date"]):
            continue
        n += 1
        d = frame.get(r["row_id"])
        if d is None:
            d = dict(r, manifests=[])
            frame[r["row_id"]] = d
        if manifest_path not in d["manifests"]:
            d["manifests"].append(manifest_path)
    return n


# --- text classification (frozen) ---------------------------------------------------------
AI_TERMS = re.compile(
    r"\bartificial[- ]intelligence\b"
    r"|\bgenerative\s+(?-i:A[Il])\b"
    r"|(?-i:\bA[Il])[- ](?:generated|drafted|drafting|tools?|assisted|platforms?)\b"
    r"|(?-i:\(\s*[\"\u201c]?A[Il][\"\u201d]?\s*\))"
    r"|\bChatGPT\b|\blarge language models?\b|\bLLMs?\b", re.I)

_AUTH = r"(?:cases?|citations?|cites|authorit(?:y|ies)|quotations?|quotes|opinions?|decisions?|case\s+law|caselaw|precedents?)"
_SKIP = r"(?:in|of|for|this|that|the|and|to|by|on|at|from|with|its|his|her|their|a|an)"
FAKE_CITE = re.compile(
    # an adjective of falsity, up to two words (not function words or possessives), then a kind of authority
    r"\b(?:fictitious|non-?existent|fabricated|fake|hallucinated|made-up|bogus|phantom|invented)\s+"
    r"(?:(?!" + _SKIP + r"\b)\w+\s+){0,2}?" + _AUTH + r"\b"
    # "... cited (by the appellant) do not exist" / "do not appear to exist"
    r"|\b(?:cited|quoted|referenced)\s+(?:\w+\s+){0,3}?(?:do(?:es)?|did)\s+not\s+(?:appear\s+to\s+)?exist\b"
    # "the cases do not exist" (plural nouns only)
    r"|\b(?:cases|citations|authorities|decisions)\s+(?:(?:that|which)\s+)?(?:do|did)\s+not\s+(?:appear\s+to\s+)?exist\b"
    # "unable to locate the cases cited"
    r"|\blocate\s+(?:(?:the|any|these|such|this|that)\s+)?" + _AUTH +
    r"\s+(?:\w+\s+){0,2}?(?:cited|relied|referenced|quoted)\b", re.I)

PRO_SE = re.compile(r"\bpro\s+se\b", re.I)
ACTION = re.compile(r"\bsanction(?:s|ed)?\b|\b1201\.43\b", re.I)
KINDS = (("remand", re.compile(r"\bREMAND\s+ORDER\b")),
         ("opinion", re.compile(r"\bOPINION\s+AND\s+ORDER\b")),
         ("final", re.compile(r"\bFINAL\s+ORDER\b")),
         ("other_order", re.compile(r"\bORDER\b")))

FLAG_KEYS = ("fake_cite", "ai_mention", "ai_citation", "pro_se", "action")


def normalize(text):
    text = re.sub(r"\s+", " ", text or "")
    return re.sub(r"(\w)- (\w)", r"\1-\2", text)  # words split across PDF lines


def _excerpt(text, pos, width=350):
    a, b = max(0, pos - width), min(len(text), pos + width)
    return text[a:b]


def doc_kind(head):
    for name, rx in KINDS:
        if rx.search(head):
            return name
    return "unknown"


def classify(raw_text):
    """Flags for one decision text (frozen)."""
    text = normalize(raw_text)
    head = text[:HEAD_CHARS]
    r = {"chars": len(text), "excerpts": {}, "kind": doc_kind(head), "pro_se": bool(PRO_SE.search(head))}
    ai = [m.start() for m in AI_TERMS.finditer(text)]
    fake = [m.start() for m in FAKE_CITE.finditer(text)]
    r["ai_mention"] = bool(ai)
    r["fake_cite"] = bool(fake)
    pair = next(((a, p) for a in ai for p in fake if abs(a - p) <= PROXIMITY), None)
    r["ai_citation"] = pair is not None
    if ai:
        r["excerpts"]["ai_mention"] = _excerpt(text, ai[0])
    if fake:
        r["excerpts"]["fake_cite"] = _excerpt(text, fake[0])
    if pair:
        r["excerpts"]["ai_citation"] = _excerpt(text, pair[0])
    m = ACTION.search(text) if r["fake_cite"] else None
    r["action"] = bool(m)
    if m:
        r["excerpts"]["action"] = _excerpt(text, m.start())
    return r


# --- the AI Hallucination Cases Database (P8 and a descriptive list) ------------------------
MSPB_NAME = re.compile(r"Merit\s+Systems\s+Protection|\bMSPB\b", re.I)


def db_check(csv_text):
    """Rows whose Court names the MSPB, and rows whose case name names it (court reviews)."""
    court_rows, review_rows = [], []
    for row in csv.DictReader(io.StringIO(csv_text)):
        court = (row.get("Court") or "").strip()
        name = (row.get("Case Name") or "").strip()
        item = {"case_id": (row.get("case_id") or "").strip(), "date": (row.get("Date") or "").strip()[:10],
                "court": court[:80]}
        if MSPB_NAME.search(court):
            court_rows.append(item)
        elif MSPB_NAME.search(name):
            review_rows.append(item)
    return {"court_rows": court_rows, "review_rows": review_rows}


# --- grading (frozen) -----------------------------------------------------------------------
def _share(rows, key):
    n = len(rows)
    k = sum(1 for r in rows if r.get(key))
    return {"n": n, "k": k, "share": round(k / n, 3) if n else None}


def _min3(s, test):
    return "not testable" if s["n"] < 3 else ("held" if test(s["share"]) else "failed")


def grade(docs, db=None, manifests=None):
    readable = [d for d in docs if d.get("readable")]
    fake = [d for d in readable if d.get("fake_cite")]
    for d in readable:
        d["is_final"] = d.get("kind") == "final"
    P = {}
    P["P1"] = {"text": "the frame holds at least 5 readable decisions with a fabricated-citation phrase",
               "detail": {"n": len(fake)}, "verdict": "held" if len(fake) >= 5 else "failed"}
    s = _share(fake, "ai_mention")
    P["P2"] = {"text": "fewer than half of the fabricated-citation decisions mention an AI term",
               "detail": s, "verdict": _min3(s, lambda x: x < 0.5)}
    early = [d for d in readable if d.get("date") and d["date"] < SPLIT]
    late = [d for d in readable if d.get("date") and d["date"] >= SPLIT]
    se, sl = _share(early, "fake_cite"), _share(late, "fake_cite")
    if len(fake) < 3 or se["n"] < 100 or sl["n"] < 100:
        v = "not testable"
    else:
        v = "held" if sl["share"] > se["share"] else "failed"
    P["P3"] = {"text": "the share of readable decisions with a fabricated-citation phrase is higher from %s on than before" % SPLIT,
               "detail": {"early": se, "late": sl}, "verdict": v}
    s = _share(fake, "pro_se")
    P["P4"] = {"text": "at least two thirds of the fabricated-citation decisions have a pro se appellant",
               "detail": s, "verdict": _min3(s, lambda x: x >= 2 / 3)}
    base = _share(readable, "pro_se")
    P["P5"] = {"text": "the pro se share among fabricated-citation decisions is higher than among all readable decisions",
               "detail": {"fake_cite": s, "readable": base},
               "verdict": "not testable" if s["n"] < 3 or not base["n"] else ("held" if s["share"] > base["share"] else "failed")}
    s = _share(fake, "action")
    P["P6"] = {"text": "fewer than half of the fabricated-citation decisions mention sanctions or 5 C.F.R. 1201.43",
               "detail": s, "verdict": _min3(s, lambda x: x < 0.5)}
    s = _share(fake, "is_final")
    P["P7"] = {"text": "at least half of the fabricated-citation decisions are final orders",
               "detail": s, "verdict": _min3(s, lambda x: x >= 0.5)}
    if db is None:
        P["P8"] = {"text": "the AI Hallucination Cases Database has no row whose court is the MSPB",
                   "detail": None, "verdict": "not testable"}
    else:
        P["P8"] = {"text": "the AI Hallucination Cases Database has no row whose court is the MSPB",
                   "detail": {"court_rows": len(db["court_rows"]), "review_rows": len(db["review_rows"])},
                   "verdict": "held" if not db["court_rows"] else "failed"}
    by_year, by_kind, status = {}, {}, {}
    for d in docs:
        status[d.get("doc_status") or "not_fetched"] = status.get(d.get("doc_status") or "not_fetched", 0) + 1
    for d in readable:
        y = (d.get("date") or "????")[:4]
        b = by_year.setdefault(y, {"readable": 0, "fake_cite": 0, "ai_mention": 0, "ai_citation": 0})
        b["readable"] += 1
        b["fake_cite"] += bool(d.get("fake_cite"))
        b["ai_mention"] += bool(d.get("ai_mention"))
        b["ai_citation"] += bool(d.get("ai_citation"))
        by_kind[d.get("kind") or "unknown"] = by_kind.get(d.get("kind") or "unknown", 0) + 1
    counts = {"in_frame": len(docs), "readable": len(readable), "fake_cite": len(fake),
              "ai_mention": sum(1 for d in readable if d.get("ai_mention")),
              "ai_citation": sum(1 for d in readable if d.get("ai_citation")),
              "pro_se_readable": base["k"],
              "precedential_readable": sum(1 for d in readable if d.get("collection") == "precedential"),
              "fetch_status": dict(sorted(status.items())), "by_kind": dict(sorted(by_kind.items())),
              "by_year": dict(sorted(by_year.items()))}
    return {"census_version": VERSION, "window": [START, END], "counts": counts,
            "manifests": manifests or [], "database": db,
            "fake_cite_decisions": [public_row(d) for d in fake],
            "ai_mention_decisions": [public_row(d) for d in readable if d.get("ai_mention")],
            "predictions": P}


ROW_COLS = ["row_id", "collection", "docket", "date", "agency", "kind", "doc_status", "chars", "readable",
            "pdf_sha256", "manifests"] + list(FLAG_KEYS)


def public_row(d):
    """One decision as published: id, docket number and metadata, never the appellant's name or
    the file name (which carries it)."""
    out = {c: d.get(c, "") for c in ROW_COLS}
    out["manifests"] = "|".join(d.get("manifests") or [])
    return out


def results_md(res, sources):
    L = ["# MSPB fabricated-citation census %s: results" % res["census_version"], "",
         "Frame: every Board decision issued %s to %s in the MSPB's public decision listings. Information about "
         "public decisions of a federal agency, not legal advice. Made with AI agents working in MV2's name."
         % tuple(res["window"]), "",
         "Sources: `%s`" % json.dumps(sources), "", "Counts: `%s`" % json.dumps(res["counts"]), "",
         "| prediction | text | verdict | detail |", "|---|---|---|---|"]
    for k, v in res["predictions"].items():
        L.append("| %s | %s | %s | `%s` |" % (k, v["text"], v["verdict"], json.dumps(v["detail"])))
    L += ["", "## Manifests", "", "| manifest | rows | in window | earliest | latest | error |", "|---|---|---|---|---|---|"]
    for m in res["manifests"]:
        L.append("| %s | %s | %s | %s | %s | %s |" % (m.get("manifest"), m.get("rows"), m.get("in_window"),
                                                       m.get("earliest"), m.get("latest"), m.get("error", "")))
    L += ["", "## Decisions with a fabricated-citation phrase", "",
          "| id | docket | date | kind | agency | flags |", "|---|---|---|---|---|---|"]
    for r in res["fake_cite_decisions"]:
        L.append("| %s | %s | %s | %s | %s | %s |" % (r["row_id"], r["docket"], r["date"], r["kind"], r["agency"],
                                                      ", ".join(k for k in FLAG_KEYS if r.get(k))))
    return "\n".join(L) + "\n"


def rows_csv(docs):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=ROW_COLS, extrasaction="ignore", lineterminator="\n")
    w.writeheader()
    for d in sorted(docs, key=lambda x: (x.get("date") or "", x.get("row_id") or "")):
        w.writerow(public_row(d))
    return buf.getvalue()
