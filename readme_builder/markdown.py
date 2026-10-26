"""Conservative README presentation migration; fenced samples stay byte-for-byte intact."""

from html import escape, unescape
import re
import unicodedata
from urllib.parse import unquote, quote

from .icons import icon

# Explicit pictograph ranges, not all non-ASCII: Spanish, CJK and accents survive.
EMOJI = re.compile(
    r"(?:[\U0001F1E6-\U0001F1FF]{2}|[\U0001F000-\U0001FAFF\u2600-\u27BF]"
    r"[\uFE0E\uFE0F]?[\U0001F3FB-\U0001F3FF]?"
    r"(?:\u200D[\U0001F000-\U0001FAFF\u2600-\u27BF][\uFE0E\uFE0F]?[\U0001F3FB-\U0001F3FF]?)*)"
)
ALIASES = {
    "🔗": "link", "🛡": "shield", "📦": "box", "🦀": "code", "🚫": "close",
    "✋": "shield", "🤐": "search", "🔁": "repeat", "🌿": "branch", "🤖": "bot",
    "🧠": "cpu", "📄": "file", "🚀": "rocket", "✨": "spark", "🎯": "target",
    "🔒": "lock", "🔐": "lock", "⚙": "settings", "🛠": "settings", "📚": "book",
    "✅": "check", "❌": "close", "⬆": "arrow-up", "💾": "database", "👥": "users",
    "🤝": "users", "🧭": "globe", "💻": "terminal", "🐳": "box", "📊": "chart",
    "🎨": "palette", "🌍": "globe", "🌐": "globe", "⚡": "bolt", "❤": "heart",
    "💡": "spark", "📌": "target", "🔑": "lock", "🏗": "layers", "🎬": "play",
    "movie_camera": "play", "scroll": "file", "bookmark": "book", "arrow_down": "download",
    "dart": "target", "open_file_folder": "layers", "joystick": "settings",
    "globe_with_meridians": "globe", "spider": "workflow", "package": "box",
    "world_map": "globe", "performing_arts": "palette", "construction": "settings",
    "man_technologist": "code", "woman_technologist": "code",
}
SHORTCODE = re.compile(r":(" + "|".join(re.escape(k) for k in ALIASES if k.isascii()) + r"):")
INLINE = re.compile(r"(`+)[^`\n]*?\1|<[^>\n]+>|\[!\[[^\]\n]*\]\([^\)\n]*\)\]\([^\)\n]*\)|!?\[[^\]\n]*\]\([^\)\n]*\)|https?://[^\s<>]+")


def strip_emoji(value):
    """Remove decorative pictographs but preserve ordinary Unicode text."""
    return EMOJI.sub("", value).replace("\ufe0f", "").replace("\ufe0e", "")


def slug(value):
    """Approximate GitHub's plain heading slug for alias preservation."""
    value = re.sub(r"<[^>]+>", "", unescape(value)).lower()
    value = "".join(c for c in value if c in "-_ " or unicodedata.category(c)[0] in "LMN")
    return value.replace(" ", "-")


def migrate(source, asset_prefix="assets/readme-builder/icons"):
    """Return migrated Markdown and the exact icon files needed; no I/O."""
    files = {}
    prefix = asset_prefix.rstrip("/")
    if not re.fullmatch(r"[A-Za-z0-9_./-]+", prefix):
        raise ValueError("icon prefix must be a local portable path")

    def replacement(match):
        symbol = match.group(0)
        name = ALIASES.get(strip_emoji_variants(symbol), ALIASES.get(symbol.strip(":"), "spark"))
        files[f"{prefix}/{name}.svg"] = icon(name)
        return f'<img src="{prefix}/{name}.svg" width="20" height="20" alt="" />'

    def prose(value):
        value = SHORTCODE.sub(replacement, value)
        return EMOJI.sub(replacement, value)

    def url_clean(value):
        decoded = unquote(value)
        cleaned = strip_emoji(decoded)
        return quote(cleaned, safe=":/?#[]@!$&'()*+,;=%-._~") if cleaned != decoded else value

    def inline(value):
        pieces, end = [], 0
        for match in INLINE.finditer(value):
            pieces.append(prose(value[end:match.start()]))
            token = match.group(0)
            if token.startswith("`"):
                pass
            elif token.startswith("<"):
                # HTML attributes must never receive nested <img> markup.
                token = re.sub(r'([\w-]+)=("[^"]*"|\x27[^\x27]*\x27)',
                               lambda m: f'{m[1]}={m[2][0]}{url_clean(strip_emoji(m[2][1:-1]))}{m[2][-1]}', token)
            elif token.startswith("[!["):
                token = re.sub(r"\]\(([^)]*)\)", lambda m: "](" + url_clean(m[1]) + ")", token)
                token = re.sub(r"!\[([^]]*)\]", lambda m: "![" + strip_emoji(m[1]) + "]", token)
            elif token.startswith(("[", "![")):
                head, address = token.rsplit("](", 1)
                head = strip_emoji(head) if token.startswith("![") else prose(head)
                token = head + "](" + url_clean(address[:-1]) + ")"
            else:
                token = url_clean(token)
            pieces.append(token)
            end = match.end()
        return "".join(pieces) + prose(value[end:])

    output, fence, fence_size, mermaid = [], None, 0, False
    heading_counts = {}
    for line in source.splitlines(keepends=True):
        boundary = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)", line)
        if boundary:
            marker = boundary[1]
            if fence is None:
                fence, fence_size = marker[0], len(marker)
                mermaid = boundary[2].strip() == "mermaid"
            elif marker[0] == fence and len(marker) >= fence_size and not boundary[2].strip():
                fence = None
                mermaid = False
            output.append(line)
            continue
        if fence:
            # Mermaid cannot embed local image tags in labels. Use clean labels.
            output.append(strip_emoji(line).replace('[" ', '["') if mermaid else line)
            continue
        heading = re.match(r"^(#{1,6}) (.+?)(\r?\n)?$", line)
        changed = inline(line)
        if heading:
            base = slug(heading[2])
            count = heading_counts.get(base, 0)
            heading_counts[base] = count + 1
            alias = base if count == 0 else f"{base}-{count}"
        if heading and changed != line:
            newline = "\r\n" if line.endswith("\r\n") else "\n"
            output.append(f'<a id="{escape(alias, quote=True)}"></a>{newline}{newline}')
        output.append(changed)
    return "".join(output), files


def strip_emoji_variants(value):
    """Resolve a coloured/variation-selector emoji to its base mapping."""
    return re.sub(r"[\uFE0E\uFE0F\U0001F3FB-\U0001F3FF]", "", value)
