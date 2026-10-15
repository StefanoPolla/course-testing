"""Check the course material and copy it from staging (course-testing) to release (ntqc).

The two repositories are independent: ntqc gets clean snapshots, never this history.
Some drift between them is allowed; `diff` makes it visible.

    python3 tools/release.py check [TREE] [--release]
    python3 tools/release.py diff RELEASE_DIR [--show PATH]
    python3 tools/release.py copy RELEASE_DIR PATH [PATH ...] [--dry-run]

Run from the root of this repository. Settings are in tools/release.toml.
`copy` only writes files; review and commit in the release repository yourself.
"""
import argparse
import difflib
import fnmatch
import re
import shutil
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = tomllib.loads((ROOT / "tools" / "release.toml").read_text())
REWRITES = [(r["staging"], r["release"]) for r in CONFIG["rewrite"]]
LEFTOVER = CONFIG["leftover"]
EXCLUDE = CONFIG["paths"]["exclude"]
PER_REPO = CONFIG["paths"]["per_repo"]
FORBIDDEN = re.compile(CONFIG["forbidden"]["path_regex"], re.IGNORECASE)
TEXT_SUFFIXES = {".md", ".qmd", ".yml", ".yaml", ".toml", ".ipynb", ".py", ".tex",
                 ".bib", ".lua", ".html", ".txt", ".css", ".json", ".svg"}


class Report:
    def __init__(self):
        self.errors, self.warnings = [], []

    def error(self, msg):
        self.errors.append(msg)

    def warn(self, msg):
        self.warnings.append(msg)

    def finish(self):
        for msg in self.warnings:
            print(f"warning: {msg}")
        for msg in self.errors:
            print(f"ERROR: {msg}")
        print(f"{len(self.errors)} error(s), {len(self.warnings)} warning(s)")
        return 1 if self.errors else 0


def matches(rel, patterns):
    parts = rel.parts
    for pat in patterns:
        if fnmatch.fnmatch(rel.as_posix(), pat):
            return True
        # a pattern without "/" matches any single path component
        if "/" not in pat and any(fnmatch.fnmatch(p, pat) for p in parts):
            return True
        # a directory pattern matches everything below it
        if rel.as_posix().startswith(pat.rstrip("/") + "/"):
            return True
    return False


def files(tree, extra_exclude=()):
    for path in sorted(tree.rglob("*")):
        rel = path.relative_to(tree)
        if path.is_file() and not matches(rel, list(EXCLUDE) + list(extra_exclude)):
            yield rel


def is_text(path):
    return path.suffix.lower() in TEXT_SUFFIXES


def rewrite(text):
    for staging, release in REWRITES:
        text = text.replace(staging, release)
    return text


def released_text(path):
    """Content of a staging file as it would appear in the release."""
    if is_text(path):
        return rewrite(path.read_text())
    return None


# ---------------------------------------------------------------- check

def newcommands(text):
    defs = {}
    for m in re.finditer(r"\\newcommand\{(\\\w+)\}(\[\d\])?\{(.*)\}\s*$", text, re.M):
        defs[m.group(1)] = (m.group(2) or "") + m.group(3)
    return defs


def glossary_entries(text):
    """Minimal reader for notes/glossary.yml: key -> definition."""
    entries, key = {}, None
    for line in text.splitlines():
        m = re.match(r"^  ([\w-]+):\s*$", line)
        if m:
            key = m.group(1)
            continue
        m = re.match(r"^    def:\s*(.*)$", line)
        if m and key:
            entries[key] = m.group(1).strip().strip('"')
    return entries


def chapters(quarto_yml):
    """Chapter and appendix files listed in _quarto.yml (book projects)."""
    return re.findall(r"^\s*-\s+([\w./-]+\.qmd)\s*$", quarto_yml, re.M)


def check(tree, release):
    rep = Report()
    notes = tree / "notes"
    all_files = list(files(tree))

    for rel in all_files:
        if FORBIDDEN.search(rel.as_posix()):
            rep.error(f"{rel}: path looks exam-related; exam material must not be here")

    if release:
        for rel in all_files:
            path = tree / rel
            if is_text(path):
                text = path.read_text(errors="replace")
                for word in LEFTOVER:
                    if word.lower() in text.lower():
                        rep.error(f"{rel}: still contains '{word}'")
            for word in LEFTOVER:
                if word.lower() in rel.as_posix().lower():
                    rep.error(f"{rel}: path contains '{word}'")

    if notes.is_dir():
        tex = newcommands((notes / "macros.tex").read_text())
        web = newcommands((notes / "_macros.qmd").read_text())
        for name in sorted(set(tex) | set(web)):
            if tex.get(name) != web.get(name):
                rep.error(f"macro {name} differs: macros.tex {tex.get(name)!r} "
                          f"vs _macros.qmd {web.get(name)!r}")

        gloss = glossary_entries((notes / "glossary.yml").read_text())
        for key, definition in gloss.items():
            if "$" in definition or "\\" in definition:
                rep.error(f"glossary '{key}': definition contains maths; "
                          "tooltips cannot render it, use plain text")
        used = set()
        for qmd in notes.glob("*.qmd"):
            for key in re.findall(r'\.gloss\s+key="([^"]+)"', qmd.read_text()):
                used.add(key)
                if key not in gloss:
                    rep.error(f"{qmd.name}: unknown glossary key '{key}'")
        for key in sorted(set(gloss) - used):
            rep.warn(f"glossary '{key}' is defined but never used")

        quarto_yml = (notes / "_quarto.yml").read_text()
        for chapter in chapters(quarto_yml):
            path = notes / chapter
            if not path.exists():
                rep.error(f"_quarto.yml lists {chapter}, which does not exist")
                continue
            for n, line in enumerate(path.read_text().splitlines(), 1):
                if "TODO" in line:
                    msg = f"{chapter}:{n}: TODO in a published chapter"
                    rep.error(msg) if release else rep.warn(msg)
    return rep.finish()


# ---------------------------------------------------------------- diff and copy

def diff(target, show):
    staged = {rel for rel in files(ROOT, PER_REPO)}
    released = {rel for rel in files(target, PER_REPO)}
    if show:
        rel = Path(show)
        a = released_text(ROOT / rel) if (ROOT / rel).exists() else ""
        b = (target / rel).read_text() if (target / rel).exists() else ""
        sys.stdout.writelines(difflib.unified_diff(
            b.splitlines(True), (a or "").splitlines(True),
            f"release/{rel}", f"staging/{rel} (rewritten)"))
        return 0
    only_staging = sorted(staged - released)
    only_release = sorted(released - staged)
    changed = []
    for rel in sorted(staged & released):
        new = released_text(ROOT / rel)
        if new is None:
            same = (ROOT / rel).read_bytes() == (target / rel).read_bytes()
        else:
            same = new == (target / rel).read_text(errors="replace")
        if not same:
            changed.append(rel)
    for label, group in (("only in staging", only_staging),
                         ("only in release", only_release),
                         ("differ", changed)):
        print(f"{label} ({len(group)}):")
        for rel in group:
            print(f"  {rel}")
    print("Ignored as per-repo: " + ", ".join(PER_REPO))
    return 0


def copy(target, paths, dry_run):
    selected = []
    for p in paths:
        src = (ROOT / p).resolve()
        if not src.exists():
            sys.exit(f"not found: {p}")
        rel = src.relative_to(ROOT)
        if src.is_dir():
            # per-repo files are copied only when named explicitly
            selected += [rel / r for r in files(src)
                         if not matches(rel / r, list(EXCLUDE) + list(PER_REPO))]
        elif not matches(rel, EXCLUDE):
            selected.append(rel)
    bad = [rel for rel in selected if FORBIDDEN.search(rel.as_posix())]
    if bad:
        sys.exit("refusing to copy exam-related paths:\n  " + "\n  ".join(map(str, bad)))
    for rel in selected:
        dest = target / rel
        new = released_text(ROOT / rel)
        if dest.exists():
            old_same = (new == dest.read_text(errors="replace")) if new is not None \
                else (ROOT / rel).read_bytes() == dest.read_bytes()
            if old_same:
                continue
            status = "update"
        else:
            status = "add"
        print(f"{status:6} {rel}")
        if dry_run:
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        if new is None:
            shutil.copy2(ROOT / rel, dest)
        else:
            dest.write_text(new)
    print("dry run, nothing written" if dry_run else
          "done; now run `check --release` on the release tree, review, and commit there")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check", help="check a tree (default: this repository)")
    c.add_argument("tree", nargs="?", default=str(ROOT))
    c.add_argument("--release", action="store_true",
                   help="release rules: TODOs and staging names are errors")
    d = sub.add_parser("diff", help="compare this repository with a release clone")
    d.add_argument("target")
    d.add_argument("--show", metavar="PATH", help="print the diff of one file")
    p = sub.add_parser("copy", help="copy paths into a release clone, rewritten")
    p.add_argument("target")
    p.add_argument("paths", nargs="+")
    p.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.cmd == "check":
        return check(Path(args.tree).resolve(), args.release)
    target = Path(args.target).resolve()
    if not target.is_dir():
        sys.exit(f"release directory not found: {target}")
    if target == ROOT:
        sys.exit("the release directory must not be this repository")
    if args.cmd == "diff":
        return diff(target, args.show)
    return copy(target, args.paths, args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
