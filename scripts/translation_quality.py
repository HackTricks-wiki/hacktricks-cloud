"""Check Markdown translations for common coverage and structure regressions."""

import posixpath
import re
import unicodedata
from collections import Counter
from functools import lru_cache
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit

from markdown_it import MarkdownIt


def fenced_code_spans(text):
    """Locate fenced blocks without treating indented inner backticks as fences."""
    spans = []
    opened = None
    offset = 0
    for line in text.splitlines(keepends=True):
        logical = line.rstrip("\r\n")
        quote = re.match(r"^[ ]{0,3}((?:> ?)+)", logical)
        depth = quote.group(1).count(">") if quote else 0
        if quote:
            logical = logical[quote.end():]
        if opened is None:
            marker = re.match(r"^([ \t]*)(`{3,}|~{3,})(.*)$", logical)
            if marker and not (marker.group(2)[0] == "`" and "`" in marker.group(3)):
                indent = len(marker.group(1).expandtabs(4))
                opened = (offset, marker.group(2)[0], len(marker.group(2)), depth, indent // 4 * 4)
        else:
            begin, character, length, quote_depth, base_indent = opened
            closing = re.fullmatch(r"([ \t]*)" + re.escape(character) + "{" + str(length) + r",}[ \t]*", logical)
            if (depth == quote_depth and closing and
                    base_indent <= len(closing.group(1).expandtabs(4)) <= base_indent + 3):
                spans.append((begin, offset + len(line)))
                opened = None
            elif quote_depth and depth < quote_depth and logical.strip():
                # An unclosed fence in a quote ends with that blockquote.
                spans.append((begin, offset))
                opened = None
        offset += len(line)
    if opened is not None:
        spans.append((opened[0], len(text)))
    return spans


SUMMARY_LINE = re.compile(
    r"(?P<prefix>^[ \t]*(?:(?:[-*+] |[0-9]+\. )?\[))(?P<label>.+?)"
    r"(?P<suffix>\]\(.*\)[ \t]*(?:<!--.*-->[ \t]*)?)$|"
    r"(?P<heading>^[ \t]*#{1,6}[ \t]+)(?P<title>\S.*?)"
    r"(?P<heading_suffix>[ \t]*(?:<!--.*-->[ \t]*)?)$"
)
SUMMARY_EXTERNAL = re.compile(r"(\$\$external:([^$<>]+)\$\$)$")
ENGLISH_FUNCTION_WORDS = frozenset(
    "the this these those is are was were be been has have had you your their them which "
    "who what when where how each from with without into between through before after "
    "for and or but if can could would should will must only also".split()
)
NAVIGATION_WORDS = frozenset(
    {"welcome", "introduction", "overview", "about", "getting started", "table of contents"}
)
FIXED_SUMMARY_NAMES = frozenset({
    "defender for cloud", "microsoft defender for cloud", "az defender for cloud",
})
SHARED_SUMMARY_WORDS = {"fr": {("introduction",)}, "french": {("introduction",)}}
LANGUAGE_CODES = frozenset("af de el es fr hi it ja ko pl pt sr sw tr uk vi zh".split())
SCRIPTS = {
    "el": ("GREEK",), "hi": ("DEVANAGARI",), "ja": ("HIRAGANA", "KATAKANA", "CJK"),
    "ko": ("HANGUL",), "uk": ("CYRILLIC",), "zh": ("CJK",),
}


def summary_parts(text):
    """Return one (prefix, label, suffix) tuple per line, including fixed lines."""
    parts = []
    for line in text.splitlines(keepends=True):
        body = line.rstrip("\r\n")
        eol = line[len(body):]
        match = SUMMARY_LINE.fullmatch(body)
        if match and body.strip() not in {"# Summary", "# SUMMARY.md"}:
            if match["heading"]:
                parts.append((match["heading"], match["title"], match["heading_suffix"] + eol))
            else:
                label, suffix = match["label"], match["suffix"]
                external = SUMMARY_EXTERNAL.search(label)
                if external:
                    label, suffix = label[:external.start()], external[1] + suffix
                parts.append((match["prefix"], label, suffix + eol))
        else:
            parts.append((line, None, ""))
    return parts


def summary_structure(parts):
    return [(prefix, label is None, suffix) for prefix, label, suffix in parts]


def verified_summary_name(label, language):
    words = " ".join(re.findall(r"[a-z]+", label.lower()))
    if words not in FIXED_SUMMARY_NAMES:
        return None
    locale = language.lower()
    if locale in {"ja", "japanese", "zh", "chinese", "simplified chinese"}:
        return label
    if locale in {"tr", "turkish"}:
        prefix = "Az - " if words.startswith("az ") else ""
        return prefix + "Bulut için Microsoft Defender"
    return None

def needs_summary_translation(label):
    words = re.findall(r"[a-z]+", label.lower())
    return (
        " ".join(words) in NAVIGATION_WORDS
        or (len(words) >= 3 and bool(ENGLISH_FUNCTION_WORDS.intersection(words)))
    )


def unchanged_summary_label(source, translated, language=""):
    if not needs_summary_translation(source) or verified_summary_name(source, language) == source:
        return False
    original = tuple(re.findall(r"[^\W\d_]+", source.casefold()))
    if original in SHARED_SUMMARY_WORDS.get(language.lower(), ()):
        return False
    return original == tuple(re.findall(r"[^\W\d_]+", translated.casefold()))


def summary_language_text(source_parts, target_parts):
    return " ".join(localized for (_, source, _), (_, localized, _) in zip(source_parts, target_parts)
                    if source is not None and localized and needs_summary_translation(source))


def reader_text(text):
    """Keep prose while removing code and reference syntax."""
    fragments = []
    cursor = 0
    for start, end in fenced_code_spans(text):
        fragments.append(text[cursor:start])
        cursor = end
    fragments.append(text[cursor:])
    text = "\n\n".join(fragments)
    text = re.sub(r"<!--.*?-->|<(?:pre|code)\b[^>]*>.*?</(?:pre|code)>", "", text, flags=re.S | re.I)
    text = re.sub(r"\{\{#ref\}\}.*?\{\{#endref\}\}|\{\{#[^{}]*\}\}", "", text, flags=re.S)
    text = re.sub(r"(?m)^\s*## References[ \t]*$|^- \[\d+\] .*?$", "", text)
    return re.sub(r"`+[^`\n]+`+|\]\([^\n)]*\)|<[^>]*>|https?://\S+", " ", text)


def prose_segments(text):
    for block in re.split(r"\n[ \t]*\n", reader_text(text)):
        # Separate headings, list items and table rows even without blank lines.
        for segment in re.split(r"\n(?=[ \t]*(?:#{1,6} |[-*+] |\d+\. |\|))", block):
            words = re.findall(r"[^\W\d_]+", segment.lower(), flags=re.UNICODE)
            if words:
                yield tuple(words)


def english_segments(text):
    return [
        words for words in prose_segments(text)
        if len(words) >= 8 and len(ENGLISH_FUNCTION_WORDS.intersection(words)) >= 2
    ]


def copied_prose(source, translated, *, majority=False):
    """Detect English passages carried over verbatim, ignoring Markdown punctuation."""
    english = english_segments(source)
    if not english:
        return False
    output = set(prose_segments(translated))
    copied = [words for words in english if words in output]
    if majority:
        return bool(copied) and sum(map(len, copied)) >= 0.75 * sum(map(len, english))
    return any(len(words) >= 12 for words in copied) or (bool(copied) and len(copied) == len(english))


def copied_sentence(source, translated):
    """Find substantial English sentences embedded inside otherwise translated prose."""
    def sentences(text):
        prose = re.sub(r"(?m)^[ \t]*>.*$", "", reader_text(text))
        for sentence in re.split(r"(?<=[.!?])\s+|\n", prose):
            words = tuple(re.findall(r"[^\W\d_]+", sentence.casefold()))
            if len(words) >= 12 and len(ENGLISH_FUNCTION_WORDS.intersection(words)) >= 3:
                yield words

    return not set(sentences(source)).isdisjoint(sentences(translated))


def expected_script(text, branch):
    """Catch clear wrong-script output for languages with distinctive scripts."""
    scripts = SCRIPTS.get(branch)
    if not scripts:
        return True
    letters = [char for words in prose_segments(text) for word in words for char in word]
    if len(letters) < 40:
        return True
    return sum(unicodedata.name(char, "").startswith(scripts) for char in letters) >= 0.1 * len(letters)


@lru_cache(maxsize=1)
def language_identifier():
    from py3langid.langid import LanguageIdentifier, MODEL_FILE

    return LanguageIdentifier.from_model_file(MODEL_FILE, norm_probs=True)


def wrong_language(text, branch):
    """Flag consistent, high-confidence evidence of a different language."""
    if branch not in LANGUAGE_CODES:
        return False
    if not expected_script(text, branch):
        return True
    sample = " ".join(
        " ".join(words) for words in prose_segments(text)
        if len(words) >= 8 or any(len(word) >= 20 and not word.isascii() for word in words)
    )
    if len(sample) < 500:
        return False

    # Closely related Serbian/Bosnian/Croatian varieties are difficult to
    # distinguish from short stretches of Serbian in the Latin script.
    acceptable = {"sr", "hr", "bs"} if branch == "sr" else {branch}
    identifier = language_identifier()
    start, end = sample[:len(sample) // 2], sample[len(sample) // 2:]
    first, certainty = identifier.classify(start[:1600])
    if first in acceptable or certainty < 0.995 or first == "zxx":
        return False
    second, certainty = identifier.classify(end[-1600:])
    return second == first and certainty >= 0.995


SOURCE_ANCHOR_CLASS = "translation-source-anchor"


PAIRED_HTML_TAGS = frozenset({
    "a", "b", "blockquote", "code", "details", "div", "em", "figure", "figcaption",
    "i", "kbd", "pre", "s", "span", "strong", "sub", "summary", "sup",
})


class ChapterHTML(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.targets = Counter()
        self.open_tags = Counter()
        self.unmatched_closing = Counter()

    def handle_starttag(self, tag, attrs):
        if tag in PAIRED_HTML_TAGS:
            self.open_tags[tag] += 1
        generated_alias = tag == "span" and dict(attrs).get("class") == SOURCE_ANCHOR_CLASS
        for name, value in attrs:
            if generated_alias and name == "id":
                self.targets[(tag, "translation alias", value)] += 1
            elif value is not None and (name in {"href", "src", "id"} or (tag == "a" and name == "name")):
                self.targets[(tag, name, value)] += 1


    def handle_endtag(self, tag):
        if tag not in PAIRED_HTML_TAGS:
            return
        if self.open_tags[tag]:
            self.open_tags[tag] -= 1
        else:
            self.unmatched_closing[tag] += 1


MARKDOWN = MarkdownIt("commonmark").enable("table")
HEADING_ATTRIBUTES = re.compile(r"\s+\{([^{}]+)\}\s*$")


@lru_cache(maxsize=128)
def markdown_inventory(text):
    """Inventory structural blocks and protected content with a CommonMark parser."""
    env = {}
    blocks, targets, literals = Counter(), Counter(), Counter()
    html = ChapterHTML()
    tokens = MARKDOWN.parse(text, env)
    for index, token in enumerate(tokens):
        if token.type == "heading_open":
            blocks[token.tag] += 1
            attributes = HEADING_ATTRIBUTES.search(tokens[index + 1].content)
            if attributes:
                for attribute in attributes[1].split():
                    if attribute.startswith("#") and len(attribute) > 1:
                        targets[("heading id", attribute[1:])] += 1
        elif token.type in {"paragraph_open", "list_item_open", "tr_open", "th_open", "td_open"}:
            blocks[token.type] += 1
        elif token.type == "code_block":
            literals[("indented code", token.content)] += 1
        elif token.type == "html_block":
            html.feed(token.content)

        for inline in token.children or ():
            if inline.type == "code_inline":
                literals[("inline code", inline.content)] += 1
            elif inline.type == "link_open":
                targets[("link", inline.attrGet("href"))] += 1
            elif inline.type == "image":
                targets[("image", inline.attrGet("src"))] += 1
            elif inline.type == "html_inline":
                html.feed(inline.content)
    html.close()
    for definition in env.get("references", {}).values():
        targets[("reference definition", definition["href"])] += 1
    targets.update(html.targets)
    return blocks, targets, literals, html.open_tags, html.unmatched_closing


def markdown_problems(source, translated, *, allow_source_aliases=False):
    """Return actionable diagnostics without including any prose or code in logs."""
    old_blocks, old_targets, old_literals, old_open, old_closing = markdown_inventory(source)
    new_blocks, new_targets, new_literals, new_open, new_closing = markdown_inventory(translated)
    problems = []
    if old_blocks - new_blocks:
        problems.append("missing Markdown sections, paragraphs, list entries, or table cells")
    if allow_source_aliases:
        old_targets = {key: count for key, count in old_targets.items() if key[1] != "translation alias"}
        new_targets = {key: count for key, count in new_targets.items() if key[1] != "translation alias"}
    if old_targets != new_targets:
        problems.append("changed link, image, or HTML anchor targets")
    if old_literals != new_literals:
        problems.append("changed inline or indented code")
    if new_open - old_open or new_closing - old_closing:
        problems.append("introduced unmatched HTML tags")
    return problems


class RenderedSidebar(HTMLParser):
    """Read the language, sections, and chapter links in mdBook's sidebar."""

    def __init__(self):
        super().__init__()
        self.language = None
        self.sections = []
        self.chapters = []
        self.in_section = False
        self.wrapper_depth = 0
        self.chapter_number = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = attrs.get("class", "").split()
        if tag == "html":
            self.language = attrs.get("lang")
        elif tag == "li" and "part-title" in classes:
            self.sections.append("")
            self.in_section = True
        elif tag == "span" and "chapter-link-wrapper" in classes:
            self.chapters.append(["", ""])
            self.wrapper_depth = 1
        elif self.wrapper_depth and tag == "strong" and attrs.get("aria-hidden") == "true":
            self.chapter_number = True
        elif self.wrapper_depth and tag in {"a", "span"}:
            self.wrapper_depth += 1
            if tag == "a" and "href" in attrs and "chapter-fold-toggle" not in classes:
                self.chapters[-1][1] = attrs["href"]

    def handle_endtag(self, tag):
        if tag == "li":
            self.in_section = False
        elif tag == "strong":
            self.chapter_number = False
        elif self.wrapper_depth and tag in {"a", "span"}:
            self.wrapper_depth -= 1

    def handle_data(self, data):
        if self.in_section:
            self.sections[-1] += data
        elif self.wrapper_depth and not self.chapter_number:
            self.chapters[-1][0] += data


def sidebar_destination(url, *, source=False):
    # Relative Markdown links are rendered as HTML links, with README.md
    # becoming index.html. Compare decoded paths and keep the fragment.
    if not url:
        return ""
    link = urlsplit(url)
    if link.scheme or link.netloc:
        return url
    path = unquote(link.path)
    if path:
        path = posixpath.normpath(path)
        if source and path.lower().endswith(".md"):
            root, name = posixpath.split(path)
            path = posixpath.join(root, "index.html" if name.lower() == "readme.md" else name[:-3] + ".html")
    return path, link.query, unquote(link.fragment)


def check_rendered_sidebar(summary, html, language):
    sidebar = RenderedSidebar()
    sidebar.feed(html)
    sidebar.close()
    if sidebar.language != language:
        raise ValueError(f"Expected rendered sidebar language {language}, got {sidebar.language}")
    sections, chapters = [], []
    for prefix, label, suffix in summary_parts(summary):
        if label is None:
            continue
        if prefix.lstrip().startswith("#"):
            sections.append((label, "", ""))
        else:
            inline = MARKDOWN.parseInline("[chapter" + suffix)[0].children or ()
            href = next((token.attrGet("href") for token in inline if token.type == "link_open"), "")
            # The theme converts the marker in a draft label to an external link.
            # toc.html retains that marker, which must be identical before conversion.
            external = suffix.split("](", 1)[0]
            chapters.append((label, sidebar_destination(href, source=True), external))

    if len(sections) != len(sidebar.sections):
        raise ValueError("Rendered sidebar section count differs from SUMMARY.md")
    if len(chapters) != len(sidebar.chapters):
        raise ValueError("Rendered sidebar chapter count differs from SUMMARY.md")

    def meaningful(text):
        return "".join(char for char in unicodedata.normalize("NFC", text) if char.isalnum())

    for kind, expected, rendered in (
        ("section", sections, [(label, "") for label in sidebar.sections]),
        ("chapter", chapters, sidebar.chapters),
    ):
        for index, ((label, destination, external), entry) in enumerate(zip(expected, rendered), start=1):
            rendered_label, rendered_href = entry
            marker = SUMMARY_EXTERNAL.search(rendered_label.rstrip())
            rendered_external = marker[1] if marker else ""
            if external != rendered_external:
                raise ValueError(f"Rendered sidebar {kind} {index} external destination differs from SUMMARY.md")
            if marker:
                rendered_label = rendered_label[:marker.start()]
            inline = MARKDOWN.parseInline(label)[0].children or ()
            expected_text = "".join(token.content for token in inline if token.type in {"text", "code_inline"})
            if meaningful(expected_text) != meaningful(rendered_label):
                raise ValueError(f"Rendered sidebar {kind} {index} differs from SUMMARY.md")
            if destination != sidebar_destination(rendered_href):
                raise ValueError(f"Rendered sidebar {kind} {index} destination differs from SUMMARY.md")


def check_rendered_anchor_collisions(book_dir):
    # The print page intentionally combines IDs from different chapters.
    for chapter in book_dir.rglob("*.html"):
        if chapter.name == "print.html":
            continue
        markup = chapter.read_text(encoding="utf-8")
        if SOURCE_ANCHOR_CLASS not in markup:
            continue
        html = ChapterHTML()
        html.feed(markup)
        html.close()
        ids = Counter()
        aliases = set()
        for (_, kind, ident), count in html.targets.items():
            if kind in {"id", "name", "translation alias"} and ident:
                ids[ident] += count
                if kind == "translation alias":
                    aliases.add(ident)
        if any(ids[alias] > 1 for alias in aliases):
            raise ValueError(f"Generated source bookmark duplicates a rendered ID in {chapter.relative_to(book_dir)}")


ATX_HEADING = re.compile(r"^ {0,3}#{1,6}[ \t]+")
HEADING_LINK_TAGS = re.compile(
    r"""(?:<a(?:\s+(?:id|name|href)=(?:"[^"]*"|'[^']*'))+\s*></a>)*""",
    re.I,
)


def chapter_headings(text):
    """Return the source line, level, and automatic or explicit mdBook ID."""
    tokens = MARKDOWN.parse(text)
    generated = set()
    for index, token in enumerate(tokens):
        if token.type != "heading_open":
            continue
        inline = tokens[index + 1]
        attributes = HEADING_ATTRIBUTES.search(inline.content)
        attributes_list = attributes[1].split() if attributes else ()
        explicit = next((value[1:] for value in attributes_list
                         if value.startswith("#") and len(value) > 1), None)
        if explicit:
            yield token.map[0], token.tag, explicit, False
            continue

        children = inline.children or ()
        if attributes:
            children = MARKDOWN.parseInline(inline.content[:attributes.start()])[0].children or ()
        # Legacy links and bookmarks preserve visible heading text. Other raw HTML
        # or images may change what the mdBook renderer uses to generate the ID.
        markup = "".join(child.content for child in children if child.type == "html_inline")
        text_parts = []
        for child in children:
            if child.type in {"text", "code_inline"}:
                text_parts.append(child.content)
            elif child.type in {"softbreak", "hardbreak"}:
                text_parts.append(" ")
        plain = "".join(text_parts).strip().lower()
        base = re.sub(r"\s", "-", re.sub(r"[^\w\s-]", "", plain))
        anchor = base
        suffix = 1
        while anchor in generated:
            anchor = f"{base}-{suffix}"
            suffix += 1
        generated.add(anchor)
        supported = (
            bool(base) and not attributes and HEADING_LINK_TAGS.fullmatch(markup) is not None
            and not any(child.type == "image" for child in children)
        )
        yield token.map[0], token.tag, anchor, supported


def preserve_source_heading_anchors(source, localized):
    """Keep source bookmarks when translation changes an mdBook section ID."""
    source_headings = list(chapter_headings(source))
    target_headings = list(chapter_headings(localized))
    if [heading[1] for heading in source_headings] != [heading[1] for heading in target_headings]:
        return localized

    used = {heading[2] for heading in target_headings}
    _, raw_targets, _, _, _ = markdown_inventory(localized)
    used.update(target[-1] for target in raw_targets
                if len(target) == 3 and target[1] in {"id", "name", "translation alias"})
    lines = localized.splitlines(keepends=True)
    for (_, _, anchor, source_supported), (line, _, _, target_supported) in zip(source_headings, target_headings):
        prefix = ATX_HEADING.match(lines[line])
        if source_supported and target_supported and anchor not in used and prefix:
            index = prefix.end()
            alias = f'<span class="{SOURCE_ANCHOR_CLASS}" id="{anchor}"></span>'
            lines[line] = lines[line][:index] + alias + lines[line][index:]
            used.add(anchor)
    return "".join(lines)


def chapter_title(text):
    """Extract a reusable chapter title without carrying generated bookmarks into the sidebar."""
    tokens = MARKDOWN.parse(text)
    for index, token in enumerate(tokens):
        if token.type != "heading_open" or token.tag != "h1":
            continue
        title = tokens[index + 1].content
        title = re.sub(r'^<span class="translation-source-anchor" id="[^"]+"></span>', "", title).strip()
        content = MARKDOWN.parseInline(title)[0].children or ()
        if title and "\n" not in title and all(
            item.type not in {"html_inline", "image", "link_open"} for item in content
        ):
            return title
        break
    return None
