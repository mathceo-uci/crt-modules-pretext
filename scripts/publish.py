#!/usr/bin/env python3
"""Publish one (or a few) target(s) into the separate site repository.

Replaces `pretext deploy`, one target at a time.

For each web target it:
  1. builds it from scratch with `pretext build --clean` (skip with
     --no-build), so no page dropped from the book lingers, and leaves out
     the TODO notes (keep them with --with-todos; see without_todos below).
     Once every target is published, it rebuilds these web targets again,
     with the TODO notes, so the local copies in output/ keep them,
  2. strips its unused external assets (scripts/strip_external.py), so the
     published folder carries only the images that target references,
  3. replaces that target's folder in the site repository with the stripped
     build, leaving every other module's folder untouched.

For each Student Workbook print target it:
  1. asks whether to rebuild it with `pretext build`, which rewrites the LaTeX
     and so loses any hand edits to it. The answer defaults to no; --no-build
     skips the question and does not rebuild,
  2. adds the cover external/{module}-cover.pdf to the start of that LaTeX
     (a module with no cover file is published without one, with a warning),
  3. compiles the PDF with pdflatex, running it as many times as needed,
  4. copies the PDF to the site root as {module}-sw.pdf.

Before any of this, it refuses to publish a target whose source still has a
\\restrictedimage placeholder (see restricted_uses below).

The script does no git: it only writes files into a local checkout of the site
repository. Committing and pushing that checkout to publish is done by hand.

The output of pretext and pdflatex goes to log files in output/publish-logs/.
If a step fails, the script stops and shows why: the LaTeX error lines for a
failed PDF compile, otherwise the end of the log.

The published name is derived from the target name, not from a deploy-dir
attribute in project.ptx, so project.ptx carries no deploy configuration for a
stray `pretext deploy` to act on:
    {module}-tg-web   -> {module}/            (Teaching Guide)
    {module}-sw-web   -> {module}-workbook/   (Student Workbook)
    {module}-sw-print -> {module}-sw.pdf      (Student Workbook PDF)

Site folder: defaults to ../mathceo-uci.github.io (a sibling of this repository);
override with the MATHCEO_SITE_DIR environment variable. It must already exist —
the script never creates or clones it.

Usage:
    python3 scripts/publish.py hawaii-tg-web              # build, strip, replace
    python3 scripts/publish.py hawaii-tg-web hawaii-sw-web
    python3 scripts/publish.py --no-build hawaii-tg-web   # use existing output/
    python3 scripts/publish.py --with-todos hawaii-tg-web # keep the TODO notes
    python3 scripts/publish.py hawaii-sw-print            # ask to rebuild, add cover, compile, copy PDF
    python3 scripts/publish.py --list                     # list publishable targets
    python3 scripts/publish.py --dry-run hawaii-tg-web    # show the plan, change nothing
"""
import os, sys, re, shutil, subprocess, contextlib
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from strip_external import strip

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Name of the separate repository that hosts the published site.
SITE_REPO = "mathceo-uci.github.io"

# Local checkout of that repository. Defaults to a sibling of this repository;
# override with MATHCEO_SITE_DIR. The script copies into this folder but never
# creates, clones, commits, or pushes it — publishing from here is done by hand.
SITE_DIR = os.environ.get("MATHCEO_SITE_DIR") or os.path.join(os.path.dirname(ROOT), SITE_REPO)


# The full output of pretext and pdflatex goes here, one file per target and
# tool. It sits outside output/<target>/ because a web target's folder is
# copied to the site as a whole.
LOG_DIR = os.path.join(ROOT, "output", "publish-logs")


class StepFailed(Exception):
    """A step failed. Its message has already been shown."""


def read_lines(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read().splitlines()


def find_tool(name):
    """Return the command that starts a tool, as a list.

    On Windows a bare name such as "pretext" is found only if the tool's folder
    is on PATH and the tool is an .exe, so look up its full path first. pip
    often installs pretext into a Scripts folder that is not on PATH; in that
    case run it through this Python instead, as `python -m pretext`.
    Return None if the tool cannot be found.
    """
    path = shutil.which(name)
    if path:
        return [path]
    if name == "pretext":
        try:
            import pretext  # noqa: F401  (only checks that it is installed)
            return [sys.executable, "-m", "pretext"]
        except ImportError:
            pass
    return None


def run_logged(cmd, log_name, cwd=ROOT, error_log=None):
    """Run a command with its output going to a log file.

    If the command fails, show why and raise StepFailed. By default that is the
    end of the command's log. For LaTeX, pass the .log it writes as error_log:
    the real error lines are there, not at the end of what pdflatex prints.
    """
    tool = find_tool(cmd[0])
    if tool is None:
        done_working()
        fail(f"{cmd[0]} not found",
             f"install it, or add its folder to PATH, then check that `{cmd[0]} --version` "
             "works in this terminal")
        raise StepFailed
    os.makedirs(LOG_DIR, exist_ok=True)
    log = os.path.join(LOG_DIR, log_name)
    with open(log, "w", encoding="utf-8") as f:
        code = subprocess.run(tool + cmd[1:], cwd=cwd, stdout=f, stderr=subprocess.STDOUT).returncode
    if code != 0:
        done_working()
        fail(f"{cmd[0]} failed", f"exit code {code}")
        shown = latex_errors(error_log) if error_log and os.path.isfile(error_log) else []
        if not shown:
            error_log = log
            shown = read_lines(log)[-15:]
        for line in shown:
            print(f"      {dim(line)}")
        print(f"    Full log: {show(error_log)}")
        raise StepFailed
    return log


def latex_errors(log, limit=3):
    """The first few errors in a LaTeX .log. Each starts with a line beginning
    with "!" and ends at the "l.<number>" line that says where in the .tex it
    happened."""
    lines = read_lines(log)
    out = []
    for i, line in enumerate(lines):
        if line.startswith("!") and len(out) < limit * 4:
            block = [line]
            for nxt in lines[i + 1:i + 8]:
                block.append(nxt)
                if nxt.startswith("l."):
                    break
            out += block
    return out


# ── Output ──────────────────────────────────────────────────────────────────
# Each target gets a heading, then one line per step: a mark, a label, and a
# dimmed detail. Colour is used only on a terminal, and never when NO_COLOR is
# set (https://no-color.org).

COLOR = sys.stdout.isatty() and not os.environ.get("NO_COLOR")
WARNINGS = []    # (target, message), repeated in the closing summary


def _style(code, text):
    return f"\033[{code}m{text}\033[0m" if COLOR else text


def bold(t):   return _style("1", t)
def dim(t):    return _style("2", t)
def green(t):  return _style("32", t)
def yellow(t): return _style("33", t)
def red(t):    return _style("31", t)


def show(path):
    """A path as short as possible for display: relative to the current folder
    when it is close by, otherwise with the home folder written as ~."""
    rel = os.path.relpath(path)
    if not rel.startswith(os.path.join("..", "..")):
        return rel
    home = os.path.expanduser("~")
    return "~" + path[len(home):] if path.startswith(home) else path


def heading(name, dest):
    print(f"\n{bold(name)} {dim('→')} {dest}")


def _line(mark, label, detail, colour=lambda t: t):
    # Pad before colouring: the colour codes are invisible but would count
    # towards the width and throw off the column.
    print(f"  {mark} {colour(f'{label:<24}')}{dim(detail) if detail else ''}")


def ok(label, detail=""):
    _line(green("✓"), label, detail)


def warn(target, label, detail=""):
    _line(yellow("!"), label, detail, yellow)
    WARNINGS.append((target, f"{label}: {detail}" if detail else label))


def fail(label, detail=""):
    _line(red("✗"), label, detail, red)


def working(label):
    """Show that a slow step is running. The ok/fail line that follows writes
    over it on a terminal."""
    if sys.stdout.isatty():
        print(f"  {dim('…')} {dim(label)}", end="\r", flush=True)


def done_working():
    if sys.stdout.isatty():
        print("\033[2K", end="")    # clear the "working" line


NAME_RE = re.compile(r"^(?P<module>.+)-(?P<kind>tg|sw)-(?P<fmt>web|print)$")


def deploy_name(name):
    """Published name for a target, from the naming convention.

    {module}-tg-web -> {module};  {module}-sw-web -> {module}-workbook;
    {module}-sw-print -> {module}-sw.pdf.
    Returns None for a name that does not fit the convention. Teaching Guide
    print targets are not published.
    """
    m = NAME_RE.match(name)
    if not m:
        return None
    module, kind, fmt = m.group("module", "kind", "fmt")
    if fmt == "print":
        return f"{module}-sw.pdf" if kind == "sw" else None
    return module if kind == "tg" else f"{module}-workbook"


def is_print(name):
    return name.endswith("-print")


def publish_targets():
    """{name: published name} for every target in project.ptx whose name fits
    the convention: html targets named {module}-{tg|sw}-web and latex targets
    named {module}-sw-print. The published name is derived from the target name,
    so project.ptx carries no deploy configuration for a stray deploy to act on."""
    tree = ET.parse(os.path.join(ROOT, "project.ptx"))
    out = {}
    for t in tree.iter("target"):
        if t.get("format") in ("html", "latex"):
            dest = deploy_name(t.get("name", ""))
            if dest:
                out[t.get("name")] = dest
    return out


# An image whose license does not allow sharing is replaced in the source by a
# gray \restrictedimage box (see DOCUMENTATION/conventions.md). A module that
# still has one is not ready to publish. The command is written directly in the
# .ptx files; its definition in source/tikz/tikzPreamble.tex is not a use, so
# only .ptx files are searched, and uses inside XML comments are ignored.
RESTRICTED_RE = re.compile(r"\\restrictedimage\b")


def restricted_uses(name, modules):
    """[(file, count)] of \\restrictedimage uses in the source files a target
    builds from: its own module's .ptx files and the shared ones, meaning every
    .ptx file whose name does not start with another module's name."""
    module = NAME_RE.match(name).group("module")
    others = tuple(f"{m}-" for m in modules if m != module)
    found = []
    for folder, _dirs, files in os.walk(os.path.join(ROOT, "source")):
        for fn in sorted(files):
            if not fn.endswith(".ptx") or fn.startswith(others):
                continue
            path = os.path.join(folder, fn)
            with open(path, encoding="utf-8") as f:
                count = len(uncommented(RESTRICTED_RE, f.read()))
            if count:
                found.append((path, count))
    return found


def mb(nbytes):
    return f"{nbytes / 1e6:.1f} MB"


def dir_size(path):
    """Total size in bytes of every file under path (0 if it does not exist)."""
    total = 0
    for root, _dirs, files in os.walk(path):
        for f in files:
            try:
                total += os.path.getsize(os.path.join(root, f))
            except OSError:
                pass
    return total


def strip_source_maps(build_dir):
    """Delete JS/CSS source maps (*.map, *.map.gz) from the build; return
    (files removed, bytes freed).

    PreTeXt ships its prebuilt _static bundle with source maps included. They are
    referenced only by the sourceMappingURL comment at the tail of each minified
    bundle, which a browser fetches only when DevTools is open — the deployed site
    never loads them. Removing them is safe on any host (about 23 MB per target).
    """
    removed = freed = 0
    for root, _dirs, files in os.walk(build_dir):
        for fn in files:
            if fn.endswith(".map") or fn.endswith(".map.gz"):
                path = os.path.join(root, fn)
                try:
                    freed += os.path.getsize(path)
                    os.remove(path)
                    removed += 1
                except OSError:
                    pass
    return removed, freed


def copy_into_site(name, folder):
    """Replace <SITE_DIR>/<folder> with this target's stripped build, and return
    the destination path.

    The destination is removed first so a page dropped from the build does not
    linger from a previous publish.
    """
    src = os.path.join(ROOT, "output", name)
    dest = os.path.join(SITE_DIR, folder)
    if os.path.isdir(dest):
        shutil.rmtree(dest)
    shutil.copytree(src, dest)
    return dest


# The cover goes first, before the frontmatter. PreTeXt's cover support is not
# designed for multi-book projects, so the script adds it to the built LaTeX
# instead. The page counter is reset so the cover and its blank back page are
# not numbered.
COVER_MARK = "%% Cover image, not numbered (added by scripts/publish.py)"
COVER_TEX = r"""{mark}
\setcounter{{page}}{{0}}%
\includepdf[noautoscale=false]{{external/{cover}}}%
%% Blank obverse for 2-sided version
\thispagestyle{{empty}}\hbox{{}}\setcounter{{page}}{{0}}\cleardoublepage%
"""


def add_cover(tex_path, module):
    """Add external/{module}-cover.pdf to the start of the LaTeX file.

    Returns "added", "present" (already added on an earlier run, as happens with
    --no-build), or "missing" (the module has no cover file). The cover goes
    just before \\frontmatter, and pdfpages, which provides \\includepdf, is
    loaded just before \\begin{document}.
    """
    cover = f"{module}-cover.pdf"
    if not os.path.isfile(os.path.join(ROOT, "external", cover)):
        return "missing"
    with open(tex_path, encoding="utf-8") as f:
        tex = f.read()
    if COVER_MARK in tex:
        return "present"
    for anchor in ("\\begin{document}\n", "\n\\frontmatter\n"):
        if tex.count(anchor) != 1:
            raise RuntimeError(f"expected one {anchor.strip()!r} in {tex_path}")
    tex = tex.replace("\\begin{document}\n", "\\usepackage{pdfpages}\n\\begin{document}\n")
    tex = tex.replace("\n\\frontmatter\n",
                      "\n" + COVER_TEX.format(mark=COVER_MARK, cover=cover) + "\\frontmatter\n")
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(tex)
    return "added"


# A LaTeX log line asking for another pass, e.g. "Rerun to get
# cross-references right" or "Label(s) may have changed".
RERUN_RE = re.compile(r"Rerun to get|may have changed\. Rerun")

# Each pass can move page numbers and workspace boxes, which the next pass
# reads back. A fresh build needs 3 passes; stop at this many all the same.
MAX_PASSES = 5


def compile_pdf(build_dir, module):
    """Compile {module}-sw.tex to PDF with pdflatex and return the PDF's path.

    pdflatex is run directly, not through latexmk: latexmk is a Perl script,
    and MiKTeX on Windows does not include Perl. Like latexmk, it runs pdflatex
    again as long as the last pass asked for a rerun or changed the .aux file,
    where the page references and workspace-box positions are saved. The
    workspace boxes are not covered by LaTeX's rerun warning, hence the .aux
    check.
    """
    log = os.path.join(build_dir, f"{module}-sw.log")
    aux = os.path.join(build_dir, f"{module}-sw.aux")

    def read_aux():
        if not os.path.isfile(aux):
            return None
        with open(aux, "rb") as f:
            return f.read()

    for n in range(1, MAX_PASSES + 1):
        before = read_aux()
        run_logged(["pdflatex", "-interaction=nonstopmode", f"{module}-sw.tex"],
                   f"{module}-sw-print-pdflatex.log", cwd=build_dir, error_log=log)
        rerun = any(RERUN_RE.search(line) for line in read_lines(log))
        if not rerun and read_aux() == before:
            break
    else:
        warn(module + "-sw-print", "LaTeX still asks for another pass",
             f"stopped after {MAX_PASSES}; page numbers may be off")
    return os.path.join(build_dir, f"{module}-sw.pdf")


def ask_rebuild(name, tex):
    """Ask whether to rebuild a print target, and return the answer.

    The built LaTeX may carry hand edits, and a rebuild overwrites them, so the
    answer defaults to no. Without a terminal to ask in, the script does not
    rebuild.
    """
    if not sys.stdin.isatty():
        print(f"  {dim('·')} {dim('Not asking whether to rebuild: no terminal to ask in')}")
        return False
    try:
        reply = input(f"  {yellow('?')} Rebuild with pretext? This replaces "
                      f"{os.path.basename(tex)} and any hand edits to it. {dim('[y/N]')} ")
    except EOFError:    # Ctrl-D: take it as no
        print()
        return False
    return reply.strip().lower() in ("y", "yes")


# TODO notes are <assemblage component="TODO"> elements. PreTeXt's versions
# feature drops an element whose component is not in the publication file's
# <version include="..."/> list, but keeps every component when there is no
# <version> element at all. So to leave out only the TODOs, the list for the
# build has to name every other component: the publication file's own list
# without TODO, or, when it has none, every component the source uses except
# TODO. Today TODO is the only component, so the list comes out empty.
TODO_COMPONENT = "TODO"
COMMENT_RE = re.compile(r"<!--.*?-->", re.S)
VERSION_RE = re.compile(r"<version\b[^>]*?/>")
SOURCE_OPEN_RE = re.compile(r"<source\b[^>]*>")


def publication_file(name):
    """Path of the publication file a target in project.ptx uses."""
    root = ET.parse(os.path.join(ROOT, "project.ptx")).getroot()
    folder = root.get("publication", "publication")
    for t in root.iter("target"):
        if t.get("name") == name:
            return os.path.join(ROOT, folder, t.get("publication"))
    raise RuntimeError(f"target {name} not found in project.ptx")


def source_components():
    """Every component="..." name used anywhere in source/."""
    names = set()
    for folder, _dirs, files in os.walk(os.path.join(ROOT, "source")):
        for fn in files:
            if fn.endswith(".ptx"):
                with open(os.path.join(folder, fn), encoding="utf-8") as f:
                    names.update(re.findall(r'component="([^"]*)"', f.read()))
    return names


def uncommented(pattern, text):
    """Matches of pattern that are not inside an XML comment."""
    spans = [m.span() for m in COMMENT_RE.finditer(text)]
    return [m for m in pattern.finditer(text)
            if not any(a <= m.start() < b for a, b in spans)]


@contextlib.contextmanager
def without_todos(pub_path):
    """While the block runs, set the publication file's version list so the
    build leaves out the TODO notes and keeps every other component. The file
    is put back exactly as it was afterwards, even if the build fails.
    Yields the list of components kept."""
    with open(pub_path, encoding="utf-8") as f:
        original = f.read()
    versions = uncommented(VERSION_RE, original)
    if len(versions) > 1:
        raise RuntimeError(f"more than one <version> in {show(pub_path)}")
    include = re.search(r'include="([^"]*)"', versions[0].group()) if versions else None
    if include:
        kept = [c for c in include.group(1).split() if c != TODO_COMPONENT]
    else:
        kept = sorted(source_components() - {TODO_COMPONENT})
    element = f'<version include="{" ".join(kept)}"/>'
    if versions:
        start, end = versions[0].span()
        changed = original[:start] + element + original[end:]
    else:
        opens = uncommented(SOURCE_OPEN_RE, original)
        if not opens:
            raise RuntimeError(f"no <source> element in {show(pub_path)}")
        at = opens[0].end()
        changed = original[:at] + "\n    " + element + original[at:]
    try:
        with open(pub_path, "w", encoding="utf-8") as f:
            f.write(changed)
        yield kept
    finally:
        with open(pub_path, "w", encoding="utf-8") as f:
            f.write(original)


def pretext_build(name, clean=False):
    """Build a target. With clean, the target's output folder is emptied
    first. A plain build never deletes pages, so a page dropped from the book
    stays behind in output/ and would be published with the rest."""
    working("Building with pretext")
    run_logged(["pretext", "build"] + (["--clean"] if clean else []) + [name],
               f"{name}-pretext.log")
    done_working()
    ok("Built with pretext")


def publish_pdf(name, dest_name, build):
    """Build a Student Workbook print target, add its cover, compile it, and
    copy the PDF to the site root."""
    module = NAME_RE.match(name).group("module")
    od = os.path.join(ROOT, "output", name)
    tex = os.path.join(od, f"{module}-sw.tex")

    if build and ask_rebuild(name, tex):
        pretext_build(name)
    elif os.path.isfile(tex):
        ok("Kept existing LaTeX", show(tex))
    if not os.path.isfile(tex):
        fail("No LaTeX to compile", f"{show(tex)} not found")
        print(f"    Answer y to rebuild, or run: pretext build {name}")
        raise StepFailed

    cover = os.path.join(ROOT, "external", f"{module}-cover.pdf")
    try:
        status = add_cover(tex, module)
    except RuntimeError as e:
        fail("Could not add the cover", str(e))
        raise StepFailed
    if status == "missing":
        warn(name, "No cover", f"{show(cover)} not found; published without one")
    else:
        ok("Cover added" if status == "added" else "Cover already added", show(cover))

    working("Compiling the PDF (pdflatex)")
    pdf = compile_pdf(od, module)
    done_working()
    ok("Compiled the PDF", mb(os.path.getsize(pdf)))

    dest = os.path.join(SITE_DIR, dest_name)
    shutil.copy2(pdf, dest)
    ok("Copied to the site", show(dest))


def publish_web(name, dest_name, build, todos):
    """Build a web target (without its TODO notes unless todos is true), strip
    what it does not use, and replace its folder in the site."""
    od = os.path.join(ROOT, "output", name)
    if build and todos:
        pretext_build(name, clean=True)
        ok("Kept the TODO notes", "--with-todos")
    elif build:
        pub = publication_file(name)
        try:
            with without_todos(pub) as kept:
                pretext_build(name, clean=True)
        except RuntimeError as e:
            fail("Could not leave out the TODOs", str(e))
            raise StepFailed
        ok("Left out the TODO notes",
           f'{os.path.basename(pub)} set to include="{" ".join(kept)}" '
           "for this build, then restored")
    else:
        print(f"  {dim('·')} {dim('Not rebuilding: the existing build may still show TODO notes')}")
    if not os.path.isdir(od):
        fail("No build to publish", f"{show(od)} not found")
        print("    Run it without --no-build.")
        raise StepFailed

    before = dir_size(os.path.join(od, "external"))
    removed, freed = strip(od, apply=True, verbose=False)
    ok("Removed unused media", f"{mb(before)} → {mb(before - freed)}, {removed} files")
    mremoved, mfreed = strip_source_maps(od)
    ok("Removed source maps", f"{mb(mfreed)}, {mremoved} files")

    dest = copy_into_site(name, dest_name)
    ok("Replaced on the site", show(dest) + os.sep)


def main(argv):
    targets = publish_targets()
    if "--list" in argv:
        width = max(map(len, targets))
        print(f"{bold('Target'.ljust(width))}   {bold('Published as')}")
        for n, d in targets.items():
            print(f"{n.ljust(width)}   {d}{'' if is_print(n) else '/'}")
        return 0

    build = "--no-build" not in argv
    todos = "--with-todos" in argv
    dry = "--dry-run" in argv
    names = [a for a in argv if not a.startswith("--")]

    if not names:
        print(__doc__)
        print("Give at least one target name. Available:", ", ".join(targets))
        return 1
    unknown = [n for n in names if n not in targets]
    if unknown:
        print(f"{red('✗')} Not a publishable target: {', '.join(unknown)}")
        print(f"  Run {bold('python3 scripts/publish.py --list')} to see them.")
        return 1

    # Refuse before anything is built or copied, so no target is published
    # with a restricted-image placeholder in it.
    modules = {NAME_RE.match(n).group("module") for n in targets}
    blocked = {n: restricted_uses(n, modules) for n in names}
    blocked = {n: uses for n, uses in blocked.items() if uses}
    if blocked:
        command = "\\restrictedimage"
        print(f"{red('✗')} Not published: the source still has restricted-image placeholders "
              f"({bold(command)})")
        for n, uses in blocked.items():
            print(f"  {n}")
            for path, count in uses:
                print(f"    {show(path)} {dim(f'({count})')}")
        print("  Replace each one with an openly licensed image first "
              "(see DOCUMENTATION/conventions.md, Restricted images).")
        return 1

    site_missing = not os.path.isdir(SITE_DIR)

    if dry:
        print(f"{bold('Dry run')} — nothing changes. Site folder: {show(SITE_DIR)}"
              f"{red(' (not found)') if site_missing else ''}")
        for n in names:
            heading(n, targets[n] + ("" if is_print(n) else "/"))
            od = os.path.join(ROOT, "output", n)
            if is_print(n):
                module = NAME_RE.match(n).group("module")
                cover = os.path.join(ROOT, "external", f"{module}-cover.pdf")
                ask = "ask whether to rebuild, then " if build else ""
                print(f"  {dim('·')} {ask}add the cover, compile, copy the PDF")
                if not os.path.isfile(cover):
                    _line(yellow("!"), "No cover", f"{show(cover)} not found", yellow)
            else:
                what = ("build with the TODO notes, " if todos else "build without the TODO notes, ") if build else ""
                print(f"  {dim('·')} {what}remove unused files, replace the folder")
            if not build and not os.path.isdir(od):
                _line(red("✗"), "No build", f"{show(od)} not found", red)
        return 0

    if site_missing:
        print(f"{red('✗')} Site folder not found: {show(SITE_DIR)}")
        print("  Clone the site repository there, or set MATHCEO_SITE_DIR to its path.")
        return 1

    # Web targets published without their TODO notes. Their local builds in
    # output/ lose the TODOs too, so they are rebuilt with them at the end.
    stripped = [n for n in names if not is_print(n)] if build and not todos else []
    if stripped:
        print(f"{yellow('!')} Rebuilding without the TODO notes, to publish: "
              f"output/ for {', '.join(stripped)}")

    # Publish each target in turn, stopping at the first failure.
    published = []
    for n in names:
        heading(n, targets[n] + ("" if is_print(n) else "/"))
        try:
            if is_print(n):
                publish_pdf(n, targets[n], build)
            else:
                publish_web(n, targets[n], build, todos)
            published.append(n)
        except StepFailed:
            print(f"\n{red('Stopped.')} {n} was not published; targets after it were not tried.")
            done = [t for t in published if t in stripped]
            if done:
                print(f"  Local builds of {', '.join(done)} have no TODO notes. "
                      "To get them back, run: pretext build <target>")
            return 1

    if stripped:
        print(f"\n{bold('Local builds')} {dim('— putting the TODO notes back in output/')}")
        for n in stripped:
            working(f"Rebuilding {n}")
            try:
                run_logged(["pretext", "build", n], f"{n}-pretext-local.log")
                done_working()
                ok(n, "rebuilt with the TODO notes")
            except StepFailed:
                warn(n, "Local rebuild failed", f"run: pretext build {n}")

    count = f"{len(names)} target{'s' if len(names) != 1 else ''}"
    print(f"\n{green('Published')} {count} to {show(SITE_DIR)}")
    for target, message in WARNINGS:
        print(f"  {yellow('!')} {target}: {message}")
    print(f"  {dim('Next: commit and push the site folder.')}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
