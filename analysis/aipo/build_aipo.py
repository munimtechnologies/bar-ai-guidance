"""Build MV2's AI protective-order coding, check it, and grade it when asked.

For bar-ai-guidance, analysis/ai-protective-orders-prereg.md and its addendum. Without
--grade this job computes no count of codes and no prediction. It:
1. downloads the frozen draft coding 0.9.0 and the published patches (0.9.1, 0.9.2 in
   analysis/aipo/draft/), then applies the local patches in order (whole cases replaced
   by case_id, exactly once each);
2. downloads the free RECAP PDFs in build_manifest.json and checks each sha256 against
   the pinned value (an empty value is recorded, not checked); rebuilds the source texts
   the coding cites (src/<case_id>.txt) with pypdf, or, for PDFs with no usable text
   layer, with tesseract OCR (also written to ocr/<case_id>.txt), and compares each text
   with its pinned text_sha256; adds the hand-pasted passages in srcextra/ and, where the
   manifest says so, reports whether a pasted passage appears in the PDF's pypdf text;
3. downloads the published grader and its tests and runs the tests;
4. re-reads the 29 frame posts from ediscoveryllc.com's public WordPress REST API and
   compares each with the frame's content hash;
5. runs the grader's own per-case check (anchors found once, every quotation word for
   word in the cited text) and reports where any anchor or quotation stops matching;
6. only with --grade, and only if there are no problems, no pending case, no changed post,
   no failing grader test and no pinned hash that stopped matching: runs the grader's
   P1-P6 on the coding and on each pre-declared alternative reading, and writes
   results.json.
Standard library plus pypdf; tesseract and poppler for OCR. Apache-2.0. MV2 of Munim, Inc.;
made with AI agents working in his name. Information about public court documents, not
legal advice.
"""
import argparse
import copy
import hashlib
import html
import importlib.util
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from html.parser import HTMLParser

UA = "Mozilla/5.0 (compatible; MV2-Munim-research/1.0; +mailto:mv2@munimtech.com)"
RAW = "https://raw.githubusercontent.com/munimtechnologies/bar-ai-guidance/main/analysis/aipo/"
API = "https://www.ediscoveryllc.com/wp-json/wp/v2/posts/%d?_fields=id,date,link,title,content"
BLOCKS = {"p", "div", "br", "li", "h1", "h2", "h3", "h4", "h5", "h6", "tr", "blockquote", "ul", "ol"}
PUBLISHED_PATCHES = ("patch-0.9.1.json", "patch-0.9.2.json")

QUOTE_MAP = str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"',
                           " ": " ", "–": "-", "—": "-", "…": "..."})
HEADER_RE = re.compile(r"^\s*Case\s+\d+:\d{2}-[a-z]{2}-\d+\S*\s+Document\s+\d+.*Page\s+\d+\s+of\s+\d+\s*$",
                       re.IGNORECASE)
PAGE_NO_RE = re.compile(r"^\s*(-\s*)?\d{1,3}(\s*-)?\s*$")

# Alternative readings declared in the coding rules (R5, R6, R8, R9, R13): reading_rule -> setup A code.
ALTERNATIVES = {
    "provider_contract": "forbidden",
    "public_model": "permitted",
    "open_use_conditions": "permitted",
    "provisos_not_copied": "permitted",
    "self_hosted_contract_proviso": "permitted",
}
CLOUD_PHRASE = "whether cloud-based or otherwise"

# content_sha256 of each frame post, from frame.json (aipo-frame-v1, 1 Nov 2026).
FRAME_SHA = {
    4703: "5e103d3391dac7899fa65e45b80bdbb98a700e29407de0858f1198219479b2e9",
    4830: "9960f0a80433640b3bc2643ccede57c19742b8fe76b1179c3d9d25c26ef676bd",
    4949: "9cfe63edfd9fca4177dfdd2e0d72c6549bb22a6d25f1f1eb3339093faf052afe",
    5056: "b8ccf083df626806305c42a9e0b877680bebb57b3d76af46fe4bce480d5c0604",
    5067: "0add7512359a36cd333220d319195d6a929f535e8b8ea9621c9da24bef27133c",
    5126: "d087037b91586a92ca27ffef86edabed2010c7579019a0e2b96fc69815086609",
    5136: "0389bd25e41c7ddc3d372af17cde2331d4de0a463d581ec2320a7e852789d4ef",
    5152: "6963e6d92d778116aa178629a571110212e9d82cd0a899045d10caa15274ba7b",
    5228: "217fe732099ce366921f5e87e586b7774f9f10b62ec1f1443d03dd6692e5f343",
    5254: "43c4cfdccc60a400d2cec3cb62c6f04db8ff0f3cde15aa5d7ed7df7e453950e1",
    5266: "5a1e83780532110dd25c215bbdd3e9d715cbd19ece794480ec4b977dab14f0f6",
    5295: "7cab5987901151d493e30cdf56717fd0b734186053e9c2b9dee72f860e7dabc6",
    5324: "6299fa4b4280faf701d1fd71a7581bfdfe1883349a2aaa908b7bd167da3a93c6",
    5386: "4fc350faaf7c34388bf4ec9a489320128d6c9ef9c7df7ac01965e774eb496fe0",
    5432: "15521e428d4e973f5466bfb0af0d56550432f0279f9c6c380a8af3b22e91b151",
    5479: "b0837413867778e91375ecccc77f64d0f9018bab41b24eacc10f022280ce6280",
    5499: "d292eaa5bd86f4c81820ce2a9958fb7ca1f203b2b3b81770edbaf1c5ffe85a8c",
    5519: "b5e18321b42e0889187de8b4549a3bb8f75141434582a4cd54bbf59e47ab6721",
    5529: "d44b6f26486806a0e24d71c1555cf2667d604afb6116db1a059d660c6870515f",
    5535: "8ac678850cd9865735eab0c908db4f1e5114d8c7f6cb2aa182907f44a940356b",
    5549: "9033076ca9e26998326a6da96436cddb5f566b84b543fb0fb4a70828e0f83ea5",
    5571: "1cd81b33f8ab2507526557c323fe06dc66e5f479616759dded0d29240660baa0",
    5617: "889e262ec73286288db942f82bb73ea1eac9ed9ef820898cb12076bfa514ebda",
    5633: "53c00f069a8a22090269463caccbbd5dff575f6d11970378c7fbbba64bc10274",
    5643: "e81fd53ce373e6b776dd53fb055028327ead9c1f152d9781c5fefeeff6284126",
    5656: "4f152a0dcd21b3247c6f7c4bb9c524941a1f5f96b090a4e19345618633b3c277",
    5694: "c87ad6ec88418911966503aa50c4a79c052c1355f37a5af5c10a5f39e91df036",
    5703: "315854dd7441c123a2e26ace97750858f2f6f6fc2e7da596e58a95e12b9945f9",
    5724: "3ea602594bd707c466066273ad3ea7b5e691f02dda82756de6670dfb7ddddebe",
}


# ---------- patch ----------

def apply_patch(base, patch):
    """A new data dict: base with whole cases replaced by case_id (each exactly once)."""
    if base.get("version") != patch["from_version"]:
        raise ValueError("base is %r, patch is for %r" % (base.get("version"), patch["from_version"]))
    out = copy.deepcopy(base)
    index = {}
    for k, c in enumerate(out["cases"]):
        if c["case_id"] in index:
            raise ValueError("repeated case_id in base: %r" % c["case_id"])
        index[c["case_id"]] = k
    seen = set()
    for new in patch["replace"]:
        cid = new["case_id"]
        if cid in seen:
            raise ValueError("case_id twice in patch: %r" % cid)
        if cid not in index:
            raise ValueError("case_id not in base: %r" % cid)
        seen.add(cid)
        out["cases"][index[cid]] = copy.deepcopy(new)
    out["version"] = patch["version"]
    out["status_note"] = patch["status_note"]
    out["coding_rules"] = list(out.get("coding_rules", [])) + list(patch.get("add_rules", []))
    return out


def apply_chain(base, patches):
    data = base
    for p in patches:
        data = apply_patch(data, p)
    return data


def pending(cases):
    """case_ids whose coding is not final yet (reason starts with 'Pending')."""
    return [c["case_id"] for c in cases
            if c.get("status") == "not_codable" and str(c.get("reason", "")).startswith("Pending")]


# ---------- alternative readings (used only with --grade) ----------

def variants(cases, texts, nrm):
    """{name: (cases, changed case_ids)} for each pre-declared alternative reading."""
    out = {}
    for rule, code in ALTERNATIVES.items():
        v = copy.deepcopy(cases)
        changed = []
        for c in v:
            if c.get("status") == "codable" and c.get("reading_rule") == rule:
                c["setup_a"] = code
                changed.append(c["case_id"])
        out["%s->%s" % (rule, code)] = (v, changed)
    v = copy.deepcopy(cases)
    changed = []
    for c in v:
        if c.get("status") == "codable" and c.get("setup_a") == "conditional":
            c["setup_a"] = "forbidden"
            changed.append(c["case_id"])
    out["conditional->forbidden"] = (v, changed)
    v = copy.deepcopy(cases)
    changed = []
    for c in v:
        if (c.get("status") == "codable" and not c.get("self_hosting_named")
                and CLOUD_PHRASE in nrm(texts.get(c["case_id"], "")).lower()):
            c["self_hosting_named"] = True
            changed.append(c["case_id"])
    out["cloud"] = (v, changed)
    v = copy.deepcopy(cases)
    changed = []
    for c in v:
        if c.get("status") == "codable" and c.get("reading_rule") in ALTERNATIVES:
            c["setup_a"] = ALTERNATIVES[c["reading_rule"]]
            changed.append(c["case_id"])
    out["all_reading_rules_reversed"] = (v, changed)
    return out


# ---------- text helpers ----------

def norm(text):
    lines = []
    for line in text.splitlines():
        while line.startswith("> "):
            line = line[2:]
        lines.append(line)
    return " ".join(" ".join(lines).translate(QUOTE_MAP).split())


def strip_page_furniture(text):
    kept, removed = [], 0
    for line in text.splitlines():
        if HEADER_RE.match(line) or PAGE_NO_RE.match(line):
            removed += 1
            continue
        kept.append(line)
    return "\n".join(kept) + "\n", removed


def passage_body(text):
    """A srcextra file's passage: everything after its header paragraph."""
    parts = text.split("\n\n", 1)
    return parts[1] if len(parts) == 2 else ""


def ai_section(text, before=150, after=4500):
    t = norm(text)
    low = t.lower()
    for key in ("restrictions on use of artificial intelligence", "artificial intelligence", "ai tool",
                "generative ai", " ai "):
        i = low.find(key)
        if i >= 0:
            s = max(0, i - before)
            return t[s:i + after]
    return ""


def pypdf_version():
    try:
        import pypdf
        return pypdf.__version__
    except Exception:  # noqa: BLE001
        return "missing"


def source_header(o, sha, when):
    return ("%s, %s, No. %s, ECF %s. Text extracted with pypdf %s from the PDF in the RECAP archive "
            "on CourtListener (%s, sha256 %s), downloaded %s. CM/ECF page-header stamps and bare "
            "page-number lines removed; nothing else changed.\n\n"
            % (o["case_id"], o["court"], o["case_no"], o["ecf"], pypdf_version(), o["url"], sha, when))


def ocr_header(o, sha, tess):
    return ("%s, %s, No. %s, ECF %s. OCR text (%s, 300 dpi grayscale pages from pdftoppm, language eng) "
            "of the PDF in the RECAP archive on CourtListener (%s, sha256 %s), which has no usable text "
            "layer. Not corrected by hand; CM/ECF page-header stamps and bare page-number lines removed.\n\n"
            % (o["case_id"], o["court"], o["case_no"], o["ecf"], tess, o["url"], sha))


# ---------- network ----------

def get(url, tries=4):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=90) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            last = e
            if e.code in (400, 401, 403, 404):
                break
        except Exception as e:  # noqa: BLE001
            last = e
        time.sleep(3 * (i + 1))
    raise RuntimeError("fetch failed %s: %r" % (url, last))


# ---------- frame posts ----------

class TextOut(HTMLParser):
    """HTML to plain text; lines inside <blockquote> start with '> ' (as in frame.py)."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.lines, self.cur, self.quote = [], [], 0

    def _flush(self):
        line = " ".join("".join(self.cur).split())
        if line:
            self.lines.append(("> " if self.quote else "") + line)
        self.cur = []

    def handle_starttag(self, tag, attrs):
        if tag in BLOCKS:
            self._flush()
        if tag == "blockquote":
            self.quote += 1

    def handle_endtag(self, tag):
        if tag in BLOCKS:
            self._flush()
        if tag == "blockquote" and self.quote:
            self.quote -= 1

    def handle_data(self, data):
        self.cur.append(data)

    def text(self):
        self._flush()
        return "\n".join(self.lines) + "\n"


def to_text(fragment):
    p = TextOut()
    p.feed(fragment)
    p.close()
    return p.text()


def post_file_text(post):
    title = html.unescape(to_text(post["title"]["rendered"])).strip()
    return "%s\n%s\n%s\n\n%s" % (title, post["date"], post["link"], to_text(post["content"]["rendered"]))


# ---------- PDFs ----------

def pdf_text_pages(body):
    from pypdf import PdfReader
    return [(p.extract_text() or "") for p in PdfReader(io.BytesIO(body)).pages]


def tesseract_version():
    try:
        r = subprocess.run(["tesseract", "--version"], capture_output=True, text=True)
        first = (r.stdout or r.stderr).splitlines()[0]
        return first.strip()
    except Exception as e:  # noqa: BLE001
        return "tesseract missing (%r)" % e


def ocr_pages(body):
    tmp = tempfile.mkdtemp()
    try:
        pdf = os.path.join(tmp, "in.pdf")
        with open(pdf, "wb") as f:
            f.write(body)
        subprocess.run(["pdftoppm", "-r", "300", "-gray", "-png", pdf, os.path.join(tmp, "p")], check=True)
        pages = []
        for name in sorted(n for n in os.listdir(tmp) if n.endswith(".png")):
            r = subprocess.run(["tesseract", os.path.join(tmp, name), "stdout", "-l", "eng", "--psm", "6"],
                               capture_output=True, text=True, check=True)
            pages.append(r.stdout)
        return pages
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def do_order(o, out, when, tess, extras=None):
    rec = {"case_id": o["case_id"], "use": o["use"]}
    body = get(o["url"])
    sha = hashlib.sha256(body).hexdigest()
    rec["pdf_sha256"] = sha
    if o.get("sha256"):
        rec["sha256_matches_pinned"] = sha == o["sha256"]
        if not rec["sha256_matches_pinned"]:
            return rec, ""
        day = o.get("extracted_on") or when
    else:
        rec["sha256_matches_pinned"] = None  # new: recorded, not checked
        day = time.strftime("%Y-%m-%d", time.gmtime())
    if o["use"] == "text":
        pages = pdf_text_pages(body)
        rec["text_chars_by_page"] = [len(p.strip()) for p in pages]
        clean, removed = strip_page_furniture("\n".join(pages))
        text = source_header(o, sha, day) + clean
    else:
        pages = ocr_pages(body)
        rec["ocr_chars_by_page"] = [len(p.strip()) for p in pages]
        clean, removed = strip_page_furniture("\n".join(pages))
        text = ocr_header(o, sha, tess) + clean
        write(os.path.join(out, "ocr", o["case_id"] + ".txt"), text)
    rec["furniture_lines_removed"] = removed
    rec["text_sha256"] = hashlib.sha256(text.encode("utf-8")).hexdigest()
    if o.get("text_sha256"):
        rec["text_matches_pinned"] = rec["text_sha256"] == o["text_sha256"]
    if o.get("check_passage"):
        passage = passage_body((extras or {}).get(o["check_passage"], ""))
        rec["check_passage"] = o["check_passage"]
        rec["passage_in_pdf_text"] = prefix_diag(norm, clean, passage) if passage else {"error": "no passage"}
    write(os.path.join(out, "src", o["case_id"] + ".txt"), text)
    return rec, ai_section(clean)


def integrity_failures(orders):
    """Pinned hashes that stopped matching, and orders that failed to download."""
    bad = []
    for r in orders:
        if r.get("error"):
            bad.append("%s: %s" % (r["case_id"], r["error"]))
        if r.get("sha256_matches_pinned") is False:
            bad.append("%s: PDF sha256 differs from the pinned value" % r["case_id"])
        if r.get("text_matches_pinned") is False:
            bad.append("%s: text sha256 differs from the pinned value" % r["case_id"])
    return bad


# ---------- check ----------

def load_module(path):
    spec = importlib.util.spec_from_file_location("grade_aipo", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def prefix_diag(nrm, text, target):
    t, s = nrm(text), nrm(target)
    n = t.count(s) if s else 0
    if n:
        return {"occurrences": n}
    words = s.split(" ")
    lo, hi = 0, len(words)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if " ".join(words[:mid]) in t:
            lo = mid
        else:
            hi = mid - 1
    pre = " ".join(words[:lo])
    k = t.find(pre) if pre else -1
    return {"occurrences": 0, "prefix_words_found": lo, "target_continues": " ".join(words[lo:lo + 15]),
            "text_continues": t[k + len(pre):k + len(pre) + 150] if k >= 0 else ""}


def diagnose(case, docs, g):
    out = {"spans": [], "quotes": {}}
    texts = []
    for sp in case.get("spans") or []:
        doc = docs.get(sp.get("doc"), "")
        d = {"doc": sp.get("doc"), "doc_found": sp.get("doc") in docs,
             "start": prefix_diag(g.norm, doc, sp.get("start", ""))}
        t, s = g.norm(doc), g.norm(sp.get("start", ""))
        i = t.find(s) if s else -1
        if i >= 0:
            d["end_after_start"] = prefix_diag(g.norm, t[i:], sp.get("end", ""))
        out["spans"].append(d)
        try:
            texts.append(g.extract(doc, sp.get("start", ""), sp.get("end", "")))
        except ValueError:
            pass
    text = " ".join(texts)
    quotes = dict(case.get("tests") or {})
    for key in ("self_hosting_quote", "openness_quote", "setup_a_quote"):
        if case.get(key):
            quotes[key] = case[key]
    for k, q in quotes.items():
        if not g.quote_in(q, text):
            out["quotes"][k] = prefix_diag(g.norm, text, q.split("...")[0])
    return out


def check_cases(cases, docs, g):
    problems, diags, seen, statuses = [], {}, set(), {}
    for c in cases:
        cid = c.get("case_id")
        statuses[c.get("status")] = statuses.get(c.get("status"), 0) + 1
        if not cid or cid in seen:
            problems.append("missing or repeated case_id %r" % cid)
            continue
        seen.add(cid)
        p = g.check_case(c, docs)
        if p:
            problems.extend(p)
            diags[cid] = diagnose(c, docs, g)
    return problems, diags, statuses


def grade_all(cases, docs, g):
    """P1-P6 on the coding and on each alternative reading (call only with 0 problems)."""
    texts = {c["case_id"]: g.case_text(c, docs) for c in cases if c["status"] == "codable"}
    res = {"main": g.grade(cases, texts), "alternatives": {}}
    for name, (v, changed) in variants(cases, texts, g.norm).items():
        r = g.grade(v, texts)
        res["alternatives"][name] = {"changed": changed, "counts": r["counts"],
                                     "percent": r["percent"], "predictions": r.get("predictions")}
    res["coding"] = {c["case_id"]: {k: c.get(k) for k in ("court", "status", "setup_a", "reading_rule",
                                                          "self_hosting_named", "openness_named")}
                     for c in cases}
    res["ai_text_by_case"] = texts
    return res


def load_extras(folder):
    """{name: text} for each srcextra/<name>.txt (hand-pasted passages cited as src:<name>)."""
    out = {}
    if folder and os.path.isdir(folder):
        for name in sorted(os.listdir(folder)):
            if name.endswith(".txt"):
                with open(os.path.join(folder, name), encoding="utf-8") as f:
                    out[name[:-4]] = f.read()
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--patches", nargs="+", default=["patch-1.0.0.json"],
                    help="local patches applied in order after the published patches")
    ap.add_argument("--published", nargs="*", default=list(PUBLISHED_PATCHES),
                    help="patches in analysis/aipo/draft/ applied first, in order")
    ap.add_argument("--manifest", default="build_manifest.json")
    ap.add_argument("--extra-src", default="srcextra", help="folder of hand-pasted passages (<name>.txt)")
    ap.add_argument("--out", default="/out")
    ap.add_argument("--grade", action="store_true", help="grade P1-P6 (only if nothing blocks it)")
    args = ap.parse_args(argv)
    out = args.out
    report = {"pypdf": pypdf_version(), "tesseract": tesseract_version()}

    local = []
    for name in args.patches:
        with open(name, encoding="utf-8") as f:
            local.append(json.load(f))
    with open(args.manifest, encoding="utf-8") as f:
        man = json.load(f)

    base_body = get(RAW + "draft/ai_protective_orders-0.9.0.json")
    report["base_sha256"] = hashlib.sha256(base_body).hexdigest()
    published = []
    report["published_patches_sha256"] = {}
    for name in args.published:
        body = get(RAW + "draft/" + name)
        report["published_patches_sha256"][name] = hashlib.sha256(body).hexdigest()
        published.append(json.loads(body.decode("utf-8")))
    data = apply_chain(json.loads(base_body.decode("utf-8")), published + local)
    write(os.path.join(out, "ai_protective_orders-%s.json" % data["version"]),
          json.dumps(data, indent=1, ensure_ascii=False) + "\n")

    src_dir = os.path.join(out, "src")
    velez = get(RAW + "draft/src/velez-oneplus.txt")
    write(os.path.join(src_dir, "velez-oneplus.txt"), velez.decode("utf-8"))
    extras = load_extras(args.extra_src)
    report["extra_src_sha256"] = {}
    for name, text in extras.items():
        write(os.path.join(src_dir, name + ".txt"), text)
        report["extra_src_sha256"][name] = hashlib.sha256(text.encode("utf-8")).hexdigest()

    orders, sections = [], []
    for o in man["orders"]:
        try:
            rec, sec = do_order(o, out, man["extracted_on"], report["tesseract"], extras)
        except Exception as e:  # noqa: BLE001
            rec, sec = {"case_id": o["case_id"], "use": o["use"], "error": repr(e)}, ""
        orders.append(rec)
        sections.append((o["case_id"], o["use"], sec))
        time.sleep(2)
    report["orders"] = orders
    report["integrity_failures"] = integrity_failures(orders)
    write(os.path.join(out, "ai_sections.txt"),
          "".join("=== %s (%s) ===\n%s\n\n" % (cid, use, sec or "(no AI passage found)")
                  for cid, use, sec in sections))

    gdir = os.path.join(out, "grader")
    os.makedirs(gdir, exist_ok=True)
    for name in ("grade_aipo.py", "test_grade_aipo.py"):
        body = get(RAW + name)
        with open(os.path.join(gdir, name), "wb") as f:
            f.write(body)
        report[name + "_sha256"] = hashlib.sha256(body).hexdigest()
    tests = subprocess.run([sys.executable, "-I", "-B", "-m", "unittest", "discover", "-s", gdir, "-v"],
                           capture_output=True, text=True)
    report["grader_tests_exit"] = tests.returncode
    report["grader_tests_tail"] = tests.stderr[-300:]

    tdir = os.path.join(out, "texts")
    os.makedirs(tdir, exist_ok=True)
    changed = []
    for pid in sorted(FRAME_SHA):
        try:
            post = json.loads(get(API % pid))
        except RuntimeError as e:
            changed.append({"id": pid, "error": str(e)})
            continue
        sha = hashlib.sha256(post["content"]["rendered"].encode("utf-8")).hexdigest()
        write(os.path.join(tdir, "%d.txt" % pid), post_file_text(post))
        if sha != FRAME_SHA[pid]:
            changed.append({"id": pid, "sha256": sha})
        time.sleep(1)
    report["posts_checked"] = len(FRAME_SHA)
    report["posts_changed_or_missing"] = changed

    g = load_module(os.path.join(gdir, "grade_aipo.py"))
    docs = g.load_docs(tdir, src_dir)
    problems, diags, statuses = check_cases(data["cases"], docs, g)
    still = pending(data["cases"])
    report.update({"version": data["version"], "cases": len(data["cases"]), "statuses": statuses,
                   "pending": still, "problems": problems, "diagnostics": diags})
    if args.grade:
        if (problems or still or changed or report["integrity_failures"]
                or report["grader_tests_exit"] != 0):
            report["graded"] = ("refused: problems, pending cases, changed posts, integrity failures "
                                "or failing grader tests")
        else:
            res = grade_all(data["cases"], docs, g)
            res["version"] = data["version"]
            write(os.path.join(out, "results.json"), json.dumps(res, indent=1, ensure_ascii=False) + "\n")
            report["graded"] = "results.json"
    write(os.path.join(out, "check.json"), json.dumps(report, indent=1, ensure_ascii=False) + "\n")
    print(json.dumps({k: report[k] for k in ("version", "pypdf", "tesseract", "grader_tests_exit",
                                               "posts_changed_or_missing", "cases", "statuses", "pending",
                                               "integrity_failures")},
                     indent=1))
    for r in orders:
        print(" ", r["case_id"], r["use"], r.get("sha256_matches_pinned"), r.get("text_matches_pinned", ""),
              r.get("passage_in_pdf_text", ""), r.get("error", ""))
    print("PROBLEMS: %d" % len(problems))
    for p in problems:
        print(" - " + p)
    if args.grade:
        print("GRADED: %s" % report.get("graded"))
        if report.get("graded") == "results.json":
            res_main = json.load(open(os.path.join(out, "results.json"), encoding="utf-8"))["main"]
            print(json.dumps({"counts": res_main["counts"], "percent": res_main["percent"],
                              "predictions": res_main.get("predictions")}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
