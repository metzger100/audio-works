# SPDX-License-Identifier: GPL-3.0-or-later
"""Repository-wide structural checks over one exact content view."""

from html.parser import HTMLParser
from pathlib import PurePosixPath
import posixpath
import re
import tomllib
from urllib.parse import unquote, urlsplit

from markdown_it import MarkdownIt

from .base import MAX_FILE, private
from .data import load, parse
from .register import classify, immutable

MEDIA = {
    ".svg",
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".gif",
    ".pdf",
    ".otf",
    ".ttf",
    ".woff",
    ".woff2",
    ".zip",
}
CONTROL_NAMES = {
    "README.md",
    "INDEX.md",
    "AGENTS.md",
    "CONTRACT.md",
    "DECISIONS.md",
    "CURRENT.md",
    "QUALITY.md",
    "CONTRIBUTING.md",
    "COMPONENTS.md",
    "PATENTS.md",
    "LICENSE",
    "LICENSES",
}
MD = MarkdownIt("commonmark").enable("table")


def original(path, register):
    return (
        immutable(path, register)
        or path in register.get("external_files", {})
        or path in register.get("original_files", {})
    )


def valid_component(component, python=False, directory=False):
    if component in CONTROL_NAMES or component in {
        "__init__.py",
        ".githooks",
        ".github",
        ".gitignore",
        ".gitattributes",
    }:
        return True
    if re.fullmatch(r"(?:candidate|concept|fixture|scenario|discrete_candidate)_\d{4,}", component):
        return True
    if component == "meridian_lab":
        return True
    pattern = r"[a-z][a-z0-9]*(?:_[a-z0-9]+)*" if python else r"[a-z0-9]+(?:-[a-z0-9]+)*"
    if not directory:
        pattern += r"\.py" if python else r"(?:\.[a-z0-9]+)*"
    return bool(re.fullmatch(pattern, component))


class HTMLLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.anchors = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.anchors.add(attrs["id"])
        for key in ("href", "src"):
            if attrs.get(key):
                self.links.append(attrs[key])


def markdown(text):
    links = []
    anchors = set()
    seen = {}
    parser = HTMLLinks()
    tokens = MD.parse(text)
    for index, token in enumerate(tokens):
        if token.type in {"html_block", "html_inline"}:
            parser.feed(token.content)
        if token.type == "heading_open":
            heading = tokens[index + 1]
            visible = "".join(
                child.content
                for child in heading.children or []
                if child.type in {"text", "code_inline"}
            )
            slug = re.sub(r"[^\w\s-]", "", visible.lower()).strip().replace(" ", "-")
            count = seen.get(slug, 0)
            seen[slug] = count + 1
            anchors.add(slug + (f"-{count}" if count else ""))
        for child in token.children or []:
            if child.type == "link_open":
                links.append(child.attrGet("href"))
            elif child.type == "image":
                links.append(child.attrGet("src"))
            elif child.type == "html_inline":
                parser.feed(child.content)
    return links + parser.links, anchors | parser.anchors


def markdown_health(text):
    """Reject empty outline stubs and substantial copy-pasted paragraphs."""
    tokens = MD.parse(text)
    errors = []
    paragraphs = set()
    for index, token in enumerate(tokens):
        if token.type == "paragraph_open":
            content = re.sub(r"\s+", " ", tokens[index + 1].content).strip()
            if len(content) >= 180:
                if content in paragraphs:
                    errors.append("Repeated substantial paragraph")
                paragraphs.add(content)
        if token.type != "heading_open":
            continue
        title = tokens[index + 1].content
        rank = int(token.tag[1:])
        body = False
        for following in range(index + 2, len(tokens)):
            item = tokens[following]
            if item.type == "heading_open" and int(item.tag[1:]) <= rank:
                break
            if item.type == "inline" and tokens[following - 1].type != "heading_open":
                body |= bool(item.content.strip())
            elif item.type in {"fence", "code_block", "html_block"}:
                body |= bool(re.sub(r"<!--.*?-->", "", item.content, flags=re.S).strip())
        if not body:
            errors.append(f"Empty Markdown section: {title}")
    return errors


def destination(origin, raw):
    parsed = urlsplit(raw)
    if parsed.scheme or parsed.netloc:
        return None, None
    target = unquote(parsed.path)
    if target.startswith("/"):
        raise ValueError(f"Nonportable absolute local link: {raw}")
    path = (
        posixpath.normpath(posixpath.join(posixpath.dirname(origin), target)) if target else origin
    )
    if path.startswith("../"):
        raise ValueError(f"Link escapes repository: {raw}")
    return path, unquote(parsed.fragment)


def validate(view, register):
    errors = []
    oversized = []
    text_paths = []
    graphs = {}
    anchors = {}
    excluded = []
    folded = {}
    for path in sorted(view.paths):
        role = classify(path, register)
        if private(path):
            errors.append(f"Private/cache path included in project files: {path}")
        if role is None:
            errors.append(f"Unclassified file: {path}; register its module/role")
        if original(path, register):
            excluded.append(path)
            continue
        if hasattr(view, "root") and (
            (view.staged or view.revision)
            and view.index[path][0] == "120000"
            or not (view.staged or view.revision)
            and (view.root / path).is_symlink()
        ):
            errors.append(f"Symlink project inputs are unsupported: {path}")
        folded_path = path.casefold()
        if folded_path in folded:
            errors.append(f"Case-colliding filenames: {folded[folded_path]} and {path}")
        folded[folded_path] = path
        components = PurePosixPath(path).parts
        for index, component in enumerate(components):
            # Owner's Prompt13 explicitly names this output directory. Keep this
            # exception at the exact requested path; ordinary names stay kebab-case.
            if (
                "/".join(components[: index + 1])
                == ("meridian-microphone/lab/results/reports/architecture_comparison_002")
                and index < len(components) - 1
            ):
                continue
            package = "/".join(components[: index + 1]) + "/__init__.py" in view.paths
            if not valid_component(
                component,
                component.endswith(".py") or package,
                directory=index < len(components) - 1,
            ):
                errors.append(f"Invalid maintained filename: {path} ({component})")
                break
        suffix = PurePosixPath(path).suffix.lower()
        if suffix in MEDIA:
            continue
        try:
            text = view.text(path)
        except UnicodeError:
            errors.append(f"Maintained text must be UTF-8: {path}")
            continue
        text_paths.append(path)
        if len(text) > MAX_FILE:
            oversized.append({"path": path, "characters": len(text)})
            errors.append(f"Oversized maintained file: {path}: {len(text)} > {MAX_FILE} characters")
        if "\r" in text:
            errors.append(f"Non-LF line endings: {path}")
        if text and not text.endswith("\n"):
            errors.append(f"Missing final newline: {path}")
        if re.search(r"(?m)^(?:<<<<<<< |=======\s*$|>>>>>>> )", text):
            errors.append(f"Unresolved merge conflict: {path}")
        try:
            if suffix in {".json", ".yaml", ".yml"}:
                load(view.text, path)
                references = []

                def include_links(node, references=references):
                    if isinstance(node, dict):
                        if "$include" in node:
                            values = node["$include"]
                            references.extend([values] if isinstance(values, str) else values)
                        else:
                            for child in node.values():
                                include_links(child)
                    elif isinstance(node, list):
                        for child in node:
                            include_links(child)

                include_links(parse(text, suffix))
                graphs[path] = references
            elif suffix == ".toml":
                tomllib.loads(text)
            elif suffix == ".py":
                compile(text, path, "exec")
        except (ValueError, TypeError, SyntaxError, KeyError, Exception) as error:
            # Parser errors are content failures, never a successful skipped check.
            errors.append(f"Malformed structured/source file: {path}: {error}")
        if suffix == ".md" or path == "LICENSE":
            graphs[path], anchors[path] = markdown(text)
            if suffix == ".md":
                errors.extend(f"{error} in {path}" for error in markdown_health(text))
    edges = {}
    for origin, links in graphs.items():
        edges[origin] = set()
        for raw in links:
            try:
                target, fragment = destination(origin, raw)
            except ValueError as error:
                errors.append(f"{error} in {origin}")
                continue
            if target is None:
                continue
            if target not in view.paths:
                candidates = [target.rstrip("/") + "/INDEX.md", target.rstrip("/") + "/README.md"]
                target = next((p for p in candidates if p in view.paths), target)
            if target not in view.paths:
                errors.append(f"Broken local link in {origin}: {raw}")
            elif fragment and target in anchors and fragment not in anchors[target]:
                errors.append(f"Broken heading link in {origin}: {raw}")
            else:
                edges[origin].add(target)
    reachable = set()
    pending = ["docs/INDEX.md"]
    while pending:
        path = pending.pop()
        if path not in reachable:
            reachable.add(path)
            pending.extend(edges.get(path, ()))
    maintained = {p for p in view.paths if not original(p, register)}
    unreachable = sorted(maintained - reachable)
    errors.extend(
        f"Unreachable maintained file: {path}; connect it to an index hub" for path in unreachable
    )
    for module in register["modules"]:
        path = module.get("index")
        if path and path not in view.paths:
            errors.append(f"Missing module index: {path}")
        research_root = module.get("research_root")
        if research_root:
            roots = {
                "/".join(PurePosixPath(path).parts[: index + 1]) + "/"
                for path in maintained
                if path.startswith(module["prefix"])
                for index, component in enumerate(PurePosixPath(path).parts[:-1])
                if component == "research"
            }
            errors.extend(
                f"Competing research root: {root}; use {research_root}"
                for root in sorted(roots - {research_root})
            )
    return {
        "errors": errors,
        "oversized": oversized,
        "unreachable": unreachable,
        "maintained_text_files": len(text_paths),
        "indexed_maintained_files": len(maintained & reachable),
        "preserved_original_files": len(excluded),
    }
