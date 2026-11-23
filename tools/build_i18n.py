"""Builds the translated home pages (/hi/, /gu/, /ta/ ...) from index.html.

    python tools/build_i18n.py            build every language
    python tools/build_i18n.py --source   also write i18n/_source.json (every
                                          translatable string, in page order)

index.html is the only source. Nothing in it is marked up for translation:
this script finds each piece of copy, looks its English text up in
i18n/<lang>.json ({"English": "translation"}) and writes <lang>/index.html.
A string with no translation stays in English and is listed at the end of
the run, so changed copy never breaks a page, it just shows up as missing.

A piece of copy that contains tags keeps them as numbered placeholders, so a
translator can move them but not break them:

    Journeys<0>: follow-ups that run themselves</0><1> are here</1>

The strings script.js draws (journey steps, captions) are sent to the page as
window.WO_I18N and read through t() there. Add a language: one line in LANGS,
one file in i18n/, one --font-indic rule in styles.css if it is a new script.
Put translate="no" on anything that must stay as written.
"""
import html
import io
import json
import os
import re
import sys
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://web.wogent.in"

# code, name in its own script, name in English
LANGS = [
    ("en", "English", "English"),
    ("hi", "हिन्दी", "Hindi"),
    ("gu", "ગુજરાતી", "Gujarati"),
    ("mr", "मराठी", "Marathi"),
    ("bn", "বাংলা", "Bengali"),
    ("ta", "தமிழ்", "Tamil"),
    ("te", "తెలుగు", "Telugu"),
    ("kn", "ಕನ್ನಡ", "Kannada"),
    ("ml", "മലയാളം", "Malayalam"),
    ("pa", "ਪੰਜਾਬੀ", "Punjabi"),
    ("or", "ଓଡ଼ିଆ", "Odia"),
    ("as", "অসমীয়া", "Assamese"),
]

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
# Never looked inside.
OPAQUE = {"script", "style", "svg", "select", "output"}
# A piece of copy may contain these and still be translated as one string.
INLINE = {"a", "b", "i", "em", "strong", "small", "span", "br", "svg", "u", "mark", "sup", "sub", "code", "abbr"}
ATTRS = ("aria-label", "placeholder", "alt", "title", "data-caption", "data-states")
META = {"description", "keywords", "og:title", "og:description", "og:image:alt", "twitter:title", "twitter:description"}
PLACEHOLDER = re.compile(r"<(/?)(\d+)(/?)>")
LETTER = re.compile(r"[^\W\d_]")


def read(path):
    return io.open(os.path.join(ROOT, path), encoding="utf-8", newline="").read()


def write(path, text):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    io.open(full, "w", encoding="utf-8", newline="").write(text)


def squash(text):
    return re.sub(r"\s+", " ", text).strip()


class Node:
    def __init__(self, tag, attrs, start, open_end):
        self.tag, self.attrs = tag, dict(attrs)
        self.start, self.open_end = start, open_end  # the start tag is src[start:open_end]
        self.close_start = self.end = open_end       # the end tag is src[close_start:end]
        self.kids = []


class Tree(HTMLParser):
    """html.parser, keeping the source offsets of every tag and comment."""

    def __init__(self, src):
        super().__init__(convert_charrefs=False)
        self.src = src
        self.line_starts = [0]
        for m in re.finditer("\n", src):
            self.line_starts.append(m.end())
        self.root = Node("#root", [], 0, 0)
        self.root.end = self.root.close_start = len(src)
        self.stack = [self.root]
        self.feed(src)
        self.close()

    def at(self):
        line, col = self.getpos()
        return self.line_starts[line - 1] + col

    def handle_starttag(self, tag, attrs):
        start = self.at()
        node = Node(tag, attrs, start, start + len(self.get_starttag_text()))
        self.stack[-1].kids.append(node)
        if tag not in VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        start = self.at()
        self.stack[-1].kids.append(Node(tag, attrs, start, start + len(self.get_starttag_text())))

    def handle_endtag(self, tag):
        start = self.at()
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                node = self.stack[i]
                node.close_start = start
                node.end = self.src.index(">", start) + 1
                del self.stack[i:]
                return

    def handle_comment(self, data):
        start = self.at()
        node = Node("#comment", [], start, start + len(data) + 7)
        self.stack[-1].kids.append(node)


def has_text(src, node):
    """True if anything inside node (at any depth) is readable text."""
    if node.tag in OPAQUE or node.tag == "#comment":
        return False
    pos = node.open_end
    for kid in node.kids:
        if LETTER.search(src[pos:kid.start]):
            return True
        if has_text(src, kid):
            return True
        pos = kid.end
    return bool(LETTER.search(src[pos:node.close_start]))


def own_text(src, node):
    pos, out = node.open_end, []
    for kid in node.kids:
        out.append(src[pos:kid.start])
        pos = kid.end
    out.append(src[pos:node.close_start])
    return "".join(out)


def all_inline(node):
    return all(k.tag == "#comment" or (k.tag in INLINE and all_inline(k)) for k in node.kids)


def key_of(src, node, slots):
    """The translator's view of node's contents; fills slots with its tags."""
    pos, out = node.open_end, []
    for kid in node.kids:
        out.append(html.unescape(src[pos:kid.start]))
        pos = kid.end
        if kid.tag == "#comment":
            continue
        n = len(slots)
        slots.append(kid)
        if has_text(src, kid) and kid.attrs.get("translate") != "no":
            out.append("<%d>%s</%d>" % (n, key_of(src, kid, slots), n))
        else:
            out.append("<%d/>" % n)
    out.append(html.unescape(src[pos:node.close_start]))
    return squash("".join(out))


def fill(src, text, slots):
    """Turns a translated string back into HTML using the original tags."""
    out, pos, open_slots = [], 0, []
    for m in PLACEHOLDER.finditer(text):
        out.append(html.escape(text[pos:m.start()], quote=False))
        pos = m.end()
        kid = slots[int(m.group(2))]
        if m.group(3):
            out.append(src[kid.start:kid.end])
        elif m.group(1):
            out.append(src[kid.close_start:kid.end])
        else:
            out.append(src[kid.start:kid.open_end])
    out.append(html.escape(text[pos:], quote=False))
    return "".join(out)


class Page:
    """Finds the copy in a page once; render() then swaps it per language."""

    def __init__(self, src):
        self.src = src
        self.edits = []  # (start, end, key, kind, slots)
        self.walk(Tree(src).root)
        self.edits.sort(key=lambda e: e[0])

    def walk(self, node):
        src = self.src
        if node.tag in OPAQUE or node.tag == "#comment" or node.attrs.get("translate") == "no":
            return
        self.attributes(node)
        if LETTER.search(html.unescape(own_text(src, node))) and all_inline(node) and node.tag != "#root":
            slots = []
            key = key_of(src, node, slots)
            self.edits.append((node.open_end, node.close_start, key, "html", slots))
            for kid in slots:
                self.attributes(kid)
            return
        for kid in node.kids:
            self.walk(kid)

    def attributes(self, node):
        names = [a for a in ATTRS if node.attrs.get(a)]
        if node.tag == "meta" and (node.attrs.get("name") in META or node.attrs.get("property") in META):
            names.append("content")
        tag_src = self.src[node.start:node.open_end]
        for name in names:
            m = re.search(r'\s%s="([^"]*)"' % re.escape(name), tag_src)
            if m and LETTER.search(m.group(1)):
                self.edits.append((node.start + m.start(1), node.start + m.end(1), html.unescape(m.group(1)), "attr", None))

    def keys(self):
        seen, out = set(), []
        for e in self.edits:
            if e[2] not in seen:
                seen.add(e[2])
                out.append(e[2])
        return out

    def render(self, table, missing=None):
        src, out, pos = self.src, [], 0
        for start, end, key, kind, slots in self.edits:
            if start < pos:
                continue  # an attribute inside a piece of copy already written
            text = table.get(key)
            if text and kind == "html" and sorted(PLACEHOLDER.findall(text)) != sorted(PLACEHOLDER.findall(key)):
                print("  ! tags don't match the English, kept English:", key[:70])
                text = None
            if not text:
                if missing is not None and key not in missing:
                    missing.append(key)
                continue
            out.append(src[pos:start])
            out.append(fill(src, text, slots) if kind == "html" else html.escape(text, quote=True))
            pos = end
        out.append(src[pos:])
        return "".join(out)


def js_keys(js):
    """The strings script.js passes through t()."""
    keys = []
    string = r'"((?:[^"\\\n]|\\.)*)"|\'((?:[^\'\\\n]|\\.)*)\''

    def add(m):
        raw = m.group(1) if m.group(1) is not None else m.group(2)
        text = raw.replace('\\"', '"').replace("\\'", "'")
        if LETTER.search(text) and text not in keys:
            keys.append(text)

    chats = js[js.index("var CHAT_DATA = {"):js.index("function tickIcon")]
    for m in re.finditer(r'[ {]text: (%s)' % string, chats):
        add(re.match(string, m.group(1)))
    for m in re.finditer(r"label: (%s) \}, text:" % string, js):
        add(re.match(string, m.group(1)))
    start = js.index("var JOURNEY_FLOWS = {")
    flows = js[start:start + re.search(r"\n  \};", js[start:]).start()]
    flows = re.sub(r"people: \[[^\]]*\]", "", flows)
    flows = re.sub(r'\b(id|kind): "[^"]*"', "", flows)
    for m in re.finditer(string, flows):
        add(m)
    for m in re.finditer(r"\bt\((%s)\)" % string, js):
        add(re.match(string, m.group(1)))
    quick = re.search(r"var CHAT_QUICK_REPLIES = \[([\s\S]*?)\]", js).group(1)
    tiers = re.search(r"var PRX_TIERS = (.*);", js).group(1)
    for m in re.finditer(string, quick + tiers):
        add(m)
    return keys


def between(src, name, body):
    """Replaces what sits between <!-- i18n:name --> and <!-- /i18n:name -->."""
    a, b = "<!-- i18n:%s -->" % name, "<!-- /i18n:%s -->" % name
    i, j = src.index(a) + len(a), src.index(b)
    return src[:i] + body + src[j:]


def url(code):
    return SITE + ("/" if code == "en" else "/%s/" % code)


def path(code):
    return "/" if code == "en" else "/%s/" % code


def shared_blocks(src, current):
    """The parts every page carries: hreflang links and the two language lists."""
    nl = "\r\n" if "\r\n" in src else "\n"
    links = ['<link rel="alternate" hreflang="%s" href="%s" />' % ("en-IN" if c == "en" else c, url(c)) for c, _, _ in LANGS]
    links.append('<link rel="alternate" hreflang="x-default" href="%s" />' % url("en"))
    src = between(src, "hreflang", nl + nl.join(links) + nl)

    def item(c, inner):
        here = ' aria-current="true"' if c == current else ""
        return '<li><a href="%s" lang="%s" hreflang="%s" data-lang-pick="%s"%s>%s</a></li>' % (path(c), c, c, c, here, inner)

    menu = [" " * 12 + item(c, "<span>%s</span><small>%s</small>" % (own, eng)) for c, own, eng in LANGS]
    foot = [" " * 8 + item(c, own) for c, own, _ in LANGS]
    src = between(src, "langs", nl + nl.join(menu) + nl)
    src = between(src, "footer-langs", nl + nl.join(foot) + nl)
    src = between(src, "code", current.upper())
    return src


# On "/" only: a visitor who chose a language before goes back to it. Arriving
# from another page of this site (the switcher itself) is left alone.
REDIRECT = """<script>
  (function () {
    try {
      var l = localStorage.getItem("wo-lang");
      var inside = document.referrer && new URL(document.referrer).origin === location.origin;
      if (l && !inside && location.pathname === "/" && /^(%s)$/.test(l)) {
        location.replace("/" + l + "/" + location.search + location.hash);
      }
    } catch (e) {}
  })();
</script>"""


def faq_schema(page_html):
    out = []
    for m in re.finditer(r"<summary>([\s\S]*?)</summary>\s*<p>([\s\S]*?)</p>", page_html):
        q, a = (squash(html.unescape(re.sub(r"<[^>]+>", "", g))) for g in m.groups())
        out.append({"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}})
    return out


def localise_schema(page_html, code, table):
    m = re.search(r'(<script type="application/ld\+json">)([\s\S]*?)(</script>)', page_html)
    data = json.loads(m.group(2))

    def tr(v):
        if isinstance(v, str):
            return table.get(v, v)
        if isinstance(v, list):
            return [tr(x) for x in v]
        if isinstance(v, dict):
            return {k: (x if k.startswith("@") or k in ("url", "image", "logo", "email") else tr(x)) for k, x in v.items()}
        return v

    data = tr(data)
    for node in data["@graph"]:
        if node["@type"] == "WebPage":
            node["@id"] = url(code) + "#webpage"
            node["url"] = url(code)
            node["inLanguage"] = code + "-IN"
        if node["@type"] == "FAQPage":
            node["mainEntity"] = faq_schema(page_html)
    body = json.dumps(data, ensure_ascii=False, indent=2)
    return page_html[:m.end(1)] + "\n" + body + "\n" + page_html[m.start(3):]


def build():
    src = read("index.html")
    nl = "\r\n" if "\r\n" in src else "\n"
    codes = "|".join(c for c, _, _ in LANGS if c != "en")

    # The English page carries the same language lists, plus the redirect.
    base = between(shared_blocks(src, "en"), "redirect", nl + REDIRECT.replace("\n", nl) % codes + nl)
    if base != src:
        write("index.html", base)
        src = base

    page = Page(src)
    assert page.render({}) == src, "render() must reproduce the page when nothing is translated"
    js = read("script.js")
    from_js = js_keys(js)
    source = page.keys() + [k for k in from_js if k not in page.keys()]
    if "--source" in sys.argv:
        write("i18n/_source.json", json.dumps(source, ensure_ascii=False, indent=1) + "\n")

    sitemap = read("sitemap.xml")
    sitemap = re.sub(r"\s*<url>\s*<loc>%s/(%s)/</loc>[\s\S]*?</url>" % (re.escape(SITE), codes), "", sitemap)
    today = re.search(r'"dateModified": "([\d-]+)"', src).group(1)
    entries = []

    for code, own, eng in LANGS[1:]:
        name = "i18n/%s.json" % code
        if not os.path.exists(os.path.join(ROOT, name)):
            print("%s: no %s, skipped" % (code, name))
            continue
        table = json.loads(read(name))
        missing = []
        out = page.render(table, missing)
        missing += [k for k in from_js if k not in table and k not in missing]
        unused = [k for k in table if k not in source]

        out = shared_blocks(out, code)
        out = between(out, "redirect", nl)
        out = out.replace('<html lang="en">', '<html lang="%s">' % code, 1)
        out = out.replace('<link rel="canonical" href="%s/" />' % SITE, '<link rel="canonical" href="%s" />' % url(code), 1)
        out = out.replace('<meta property="og:url" content="%s/" />' % SITE, '<meta property="og:url" content="%s" />' % url(code), 1)
        out = out.replace('content="en_IN"', 'content="%s_IN"' % code, 1)
        out = out.replace('href="styles.css"', 'href="/styles.css"', 1)
        strings = {k: table[k] for k in from_js if k in table}
        loader = '["script.js", ""]'
        assert loader in out and "<script>" + nl + "  (function () {" + nl + "    var scripts" in out
        out = out.replace(loader, '["/script.js", ""]', 1)
        out = out.replace(
            "<script>" + nl + "  (function () {" + nl + "    var scripts",
            "<script>window.WO_I18N = %s;</script>%s<script>%s  (function () {%s    var scripts"
            % (json.dumps(strings, ensure_ascii=False).replace("</", "<\\/"), nl, nl, nl), 1)
        out = localise_schema(out, code, table)
        write("%s/index.html" % code, out)
        entries.append("  <url>%s    <loc>%s</loc>%s    <lastmod>%s</lastmod>%s  </url>" % (nl, url(code), nl, today, nl))
        print("%s %-9s %d of %d strings translated%s" % (
            code, eng, len(source) - len(missing), len(source),
            ", %d unused in %s" % (len(unused), name) if unused else ""))
        for k in missing if "--missing" in sys.argv else []:
            print("    missing:", k[:90])

    sitemap = sitemap.replace("</urlset>", nl.join(entries) + nl + "</urlset>") if entries else sitemap
    write("sitemap.xml", sitemap)


if __name__ == "__main__":
    build()
