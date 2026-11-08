#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# court_ai_rules.py 0.1.0: look up what US bars, courts and legislatures have told lawyers
# about generative AI, in MV2's bar-ai-guidance index (data/guidance.json, CC BY 4.0).
# Made with AI agents working in MV2's (Munim, Inc.) name. Standard library only, read-only.
# It reports what public documents say and where to read them. It is not legal advice.
"""Look up entries of the bar-ai-guidance index by state, binding force, kind, id or text.

Data source, in this order: --file PATH; the repository's own data/guidance.json when the
script runs inside a checkout of munimtechnologies/bar-ai-guidance; otherwise one HTTPS GET
of --url (default: the file on the repository's main branch).

Exit codes: 0 = at least one entry matched (with --state: at least one entry of a requested
state itself, not only national ones); 1 = no match; 2 = the index could not be read.
"""
import argparse
import json
import os
import re
import sys
import urllib.request

__version__ = "0.1.0"

DEFAULT_URL = ("https://raw.githubusercontent.com/munimtechnologies/bar-ai-guidance/"
               "main/data/guidance.json")
REPO_URL = "https://github.com/munimtechnologies/bar-ai-guidance"

BINDING_LABELS = {
    "court_rule": "court rule",
    "statute": "state statute",
    "advisory": "advisory guidance",
}
VERIFICATION_LABELS = {
    "fetched": "issuer's own page or file, retrieved and title matched",
    "cited": "issuer's own address, cited but not retrieved",
    "archived": "archived copy of the issuer's own file (Internet Archive)",
}
FOOTER = ("Information about public documents, not legal advice. Read the linked document "
          "itself, and check the court's local rules and the assigned judge's standing "
          "orders, before relying on it.")
CODE_RE = re.compile(r"^[A-Z]{2}$")


def local_data_path():
    """data/guidance.json of the checkout this script sits in, if any.

    In the repository the script is skills/court-ai-rules/scripts/court_ai_rules.py, so the
    repository root is three folders above the script's own folder.
    """
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(os.path.dirname(os.path.dirname(here)))
    path = os.path.join(root, "data", "guidance.json")
    return path if os.path.isfile(path) else None


def load_index(file_path=None, url=None, timeout=30):
    """Return (data, source). Raises ValueError or OSError when the index cannot be read."""
    if file_path:
        with open(file_path, encoding="utf-8") as fh:
            data = json.load(fh)
        source = file_path
    elif url is None and local_data_path():
        path = local_data_path()
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        source = path
    else:
        url = url or DEFAULT_URL
        if not url.startswith("https://"):
            raise ValueError("only https:// URLs are read")
        req = urllib.request.Request(url, headers={"User-Agent": "court-ai-rules/" + __version__})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        source = url
    if not isinstance(data, dict) or not isinstance(data.get("entries"), list):
        raise ValueError("not a bar-ai-guidance index (no 'entries' list)")
    return data, source


def split_codes(values):
    codes = []
    for value in values or []:
        for part in value.split(","):
            part = part.strip().upper()
            if part:
                if not CODE_RE.match(part):
                    raise ValueError("not a two-letter code: %r" % part)
                if part not in codes:
                    codes.append(part)
    return codes


def entry_text(entry):
    return " ".join(str(v) for v in entry.values() if isinstance(v, str)).lower()


def select(entries, states=None, national=True, ids=None, binding=None, kind=None, grep=None):
    """Filter entries. With states, national (US) entries are added unless national=False."""
    wanted = list(states or [])
    if wanted and national and "US" not in wanted:
        wanted.append("US")
    out = []
    for entry in entries:
        if wanted and entry.get("jurisdiction") not in wanted:
            continue
        if ids and entry.get("id") not in ids:
            continue
        if binding and entry.get("binding") != binding:
            continue
        if kind and entry.get("kind") != kind:
            continue
        if grep and grep.lower() not in entry_text(entry):
            continue
        out.append(entry)
    return out


def labelled(entry):
    item = dict(entry)
    item["binding_label"] = BINDING_LABELS.get(entry.get("binding"), str(entry.get("binding")))
    item["link_label"] = VERIFICATION_LABELS.get(entry.get("verification"),
                                                 str(entry.get("verification")))
    return item


def missing_message(code, data, filtered=False):
    what = "matching entry" if filtered else "entry"
    return ("No %s for %s in bar-ai-guidance %s (updated %s). That does not mean %s has no "
            "rule, order or opinion on AI: the index lists only documents read from primary "
            "sources. See the README's 'Known gaps' (%s), the state bar's and courts' own "
            "sites, the court's local rules and the judge's standing orders."
            % (what, code, data.get("version", "?"), data.get("updated", "?"), code, REPO_URL))


def format_entry(entry, show_notes=False):
    item = labelled(entry)
    number = (" (%s)" % entry["number"]) if entry.get("number") else ""
    lines = [
        "[%s] %s | %s | %s | %s" % (entry.get("id"), entry.get("jurisdiction"),
                                    item["binding_label"], entry.get("kind"), entry.get("date")),
        "  %s%s" % (entry.get("title"), number),
        "  Issuer: %s" % entry.get("issuer"),
        "  Link: %s" % entry.get("url"),
        "    (%s; checked %s)" % (item["link_label"], entry.get("url_verified")),
        "  Confidentiality: %s" % entry.get("confidentiality_note"),
    ]
    if entry.get("in_house_tools_note"):
        lines.append("  In-house tools: %s" % entry["in_house_tools_note"])
    if show_notes and entry.get("notes"):
        lines.append("  Notes: %s" % entry["notes"])
    return "\n".join(lines)


def summary_lines(data):
    entries = data["entries"]
    lines = ["%d entries, version %s (updated %s)"
             % (len(entries), data.get("version", "?"), data.get("updated", "?"))]
    by_binding = {}
    by_code = {}
    for entry in entries:
        by_binding[entry.get("binding")] = by_binding.get(entry.get("binding"), 0) + 1
        code = entry.get("jurisdiction")
        by_code[code] = by_code.get(code, 0) + 1
    lines.append("by binding: " + ", ".join("%s %d" % (k, by_binding[k])
                                            for k in sorted(by_binding)))
    lines.append("jurisdictions (%d): " % len(by_code)
                 + ", ".join("%s %d" % (k, v) for k, v in by_code.items()))
    return lines


def build_parser():
    p = argparse.ArgumentParser(
        prog="court_ai_rules.py",
        description="Look up US bar, court and legislative guidance on lawyers' use of "
                    "generative AI (bar-ai-guidance index). Not legal advice.")
    p.add_argument("--state", action="append", metavar="XX",
                   help="two-letter state code, DC or US; repeat or comma-separate")
    p.add_argument("--no-national", action="store_true",
                   help="with --state, leave out the national (US, ABA) entries")
    p.add_argument("--id", action="append", dest="ids", metavar="ID", help="exact entry id")
    p.add_argument("--binding", choices=sorted(BINDING_LABELS), help="binding force")
    p.add_argument("--kind", help="kind, e.g. rule_amendment, formal_opinion, court_policy")
    p.add_argument("--grep", metavar="TEXT", help="case-insensitive text in any field")
    p.add_argument("--notes", action="store_true", help="also print each entry's notes")
    p.add_argument("--json", action="store_true", help="print JSON instead of text")
    p.add_argument("--summary", action="store_true", help="print counts and stop")
    p.add_argument("--file", metavar="PATH", help="read this guidance.json instead")
    p.add_argument("--url", metavar="URL", help="read the index from this https URL")
    p.add_argument("--version", action="version", version="%(prog)s " + __version__)
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        states = split_codes(args.state)
    except ValueError as exc:
        print("court_ai_rules: %s" % exc, file=sys.stderr)
        return 2
    try:
        data, source = load_index(args.file, args.url)
    except (OSError, ValueError) as exc:
        print("court_ai_rules: could not read the index: %s" % exc, file=sys.stderr)
        return 2

    if args.summary:
        print("\n".join(summary_lines(data)))
        print("source: %s" % source)
        return 0

    entries = data["entries"]
    found = select(entries, states=states, national=not args.no_national, ids=args.ids,
                   binding=args.binding, kind=args.kind, grep=args.grep)
    present = set(e.get("jurisdiction") for e in found)
    missing = [code for code in states if code not in present]
    if states:
        hit = any(e.get("jurisdiction") in states for e in found)
    else:
        hit = bool(found)

    if args.json:
        print(json.dumps({
            "version": data.get("version"),
            "updated": data.get("updated"),
            "source": source,
            "license": data.get("license"),
            "matched": len(found),
            "missing": missing,
            "entries": [labelled(e) for e in found],
            "not_legal_advice": FOOTER,
        }, indent=2, ensure_ascii=False))
        return 0 if hit else 1

    print("bar-ai-guidance %s (updated %s): %d of %d entries matched; source %s"
          % (data.get("version", "?"), data.get("updated", "?"), len(found), len(entries),
             source))
    filtered = bool(args.ids or args.binding or args.kind or args.grep)
    for code in missing:
        print("")
        print(missing_message(code, data, filtered))
    for entry in found:
        print("")
        print(format_entry(entry, show_notes=args.notes))
    print("")
    print(FOOTER)
    return 0 if hit else 1


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(errors="replace")
        except (ValueError, OSError):
            pass
    sys.exit(main())
