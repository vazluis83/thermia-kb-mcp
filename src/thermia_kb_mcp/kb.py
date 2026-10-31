"""Loading, indexing and searching the Thermia Duo 12 knowledge base.

Pure Python with no MCP dependency, so it can be unit-tested directly. The knowledge base is two Markdown files
(English and European Portuguese) with numbered headings ("## 6. ...", "### 6.1 ..."); sections are addressed by
that number.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from importlib import resources
from pathlib import Path
from typing import Literal

Lang = Literal["en", "pt"]

KB_FILES: dict[str, str] = {
    "en": "thermia-duo12-knowledge-base-EN.md",
    "pt": "thermia-duo12-knowledge-base-PT.md",
}

_HEADING = re.compile(r"^(#{2,3}) (\d+(?:\.\d+)?)\.?\s+(.*)$")
_IMAGE_EXT = {".png", ".jpg", ".jpeg", ".svg"}


def _fold(text: str) -> str:
    """Lower-case and strip accents so 'ligação' matches 'ligacao'."""
    decomposed = unicodedata.normalize("NFKD", text.lower())
    return "".join(c for c in decomposed if not unicodedata.combining(c))


@dataclass
class Section:
    id: str  # "6" or "6.1"
    title: str
    level: int  # 2 for "##", 3 for "###"
    lines: list[str] = field(default_factory=list)  # heading line + own body, without subsections

    @property
    def body(self) -> str:
        return "\n".join(self.lines).strip()


@dataclass
class Hit:
    section_id: str
    section_title: str
    text: str
    score: float


class KnowledgeBase:
    """One language of the knowledge base, split into numbered sections."""

    def __init__(self, markdown: str, lang: str) -> None:
        self.lang = lang
        self.markdown = markdown
        self.sections: list[Section] = []
        current: Section | None = None
        preamble: list[str] = []
        for line in markdown.splitlines():
            m = _HEADING.match(line)
            if m:
                current = Section(id=m.group(2), title=m.group(3).strip(), level=len(m.group(1)), lines=[line])
                self.sections.append(current)
            elif current is None:
                preamble.append(line)
            else:
                current.lines.append(line)
        self.preamble = "\n".join(preamble).strip()
        self._by_id = {s.id: s for s in self.sections}

    # --- sections ------------------------------------------------------------------------------------------

    def section_ids(self) -> list[str]:
        return [s.id for s in self.sections]

    def get_section(self, section_id: str) -> str | None:
        """Return a section; a top-level id ("6") includes its subsections ("6.1", "6.2", ...)."""
        sid = section_id.strip().lstrip("§").rstrip(".")
        sec = self._by_id.get(sid)
        if sec is None:
            return None
        parts = [sec.body]
        if sec.level == 2:
            parts += [s.body for s in self.sections if s.level == 3 and s.id.split(".")[0] == sid]
        return "\n\n".join(parts)

    def _section_of(self, sid: str) -> Section:
        return self._by_id[sid]

    # --- blocks used by search and lookups --------------------------------------------------------------------

    def _blocks(self):
        """Yield (section, text) for every table row (with its header row), list item and paragraph."""
        for sec in self.sections:
            header: str | None = None
            para: list[str] = []
            for line in sec.lines[1:]:
                stripped = line.strip()
                if stripped.startswith("|"):
                    if para:
                        yield sec, " ".join(para)
                        para = []
                    if re.fullmatch(r"\|[\s\-:|]+\|", stripped):
                        continue  # separator row
                    if header is None:
                        header = stripped
                        continue
                    yield sec, f"{header}\n{stripped}"
                    continue
                header = None
                if not stripped:
                    if para:
                        yield sec, " ".join(para)
                        para = []
                    continue
                if stripped.startswith(("- ", "* ")) or re.match(r"^\d+\. ", stripped):
                    if para:
                        yield sec, " ".join(para)
                        para = []
                    yield sec, stripped
                    continue
                para.append(stripped)
            if para:
                yield sec, " ".join(para)

    def search(self, query: str, max_results: int = 10) -> list[Hit]:
        terms = [t for t in re.split(r"[\s,;]+", _fold(query)) if t]
        if not terms:
            return []
        hits: list[Hit] = []
        for sec, text in self._blocks():
            folded = _fold(text)
            title = _fold(sec.title)
            score = 0.0
            matched = 0
            for t in terms:
                n = len(re.findall(r"(?<![\w])" + re.escape(t) + r"(?![\w])", folded))
                partial = folded.count(t) - n
                if n or partial or t in title:
                    matched += 1
                score += 3 * n + partial + (2 if t in title else 0)
            if matched == 0:
                continue
            score *= matched / len(terms)  # favour blocks that contain every term
            hits.append(Hit(sec.id, sec.title, text, round(score, 2)))
        hits.sort(key=lambda h: -h.score)
        return hits[:max_results]

    def lookup_token(self, pattern: re.Pattern[str], sections: set[str] | None = None) -> list[Hit]:
        out = []
        for sec, text in self._blocks():
            top = sec.id.split(".")[0]
            if sections is not None and top not in sections and sec.id not in sections:
                continue
            if pattern.search(text):
                out.append(Hit(sec.id, sec.title, text, 1.0))
        return out


def terminal_pattern(terminal: str) -> re.Pattern[str]:
    """Match a terminal label such as 211, 303, 1L1, PE5 or N3 as a whole token (also inside gy-211, 303/304)."""
    t = re.escape(terminal.strip().upper())
    # Not part of a longer word or a decimal number ("2.14", "2,5"), and not a quantity ("20 A", "30 °C").
    return re.compile(
        r"(?<![\w])(?<!\d[.,])" + t + r"(?![\w]|[.,]\d|\s?(?:°|kΩ|Ω|kW|W\b|A\b|V\b|mm|min|s\b|bar|%))", re.I
    )


def normalize_register(reg: str) -> str:
    """'r32', 'R32', '0x32', '32' (hex as in the map) -> 'r32'; 'r0a' -> 'r0A'."""
    r = reg.strip().lower()
    r = r.removeprefix("0x").removeprefix("r")
    if not re.fullmatch(r"[0-9a-f]{1,2}", r):
        raise ValueError(f"not a register: {reg!r} (expected r00–r7F)")
    value = int(r, 16)
    if value > 0x7F:
        raise ValueError(f"register out of range: {reg!r} (EXT registers are 0x00–0x7F)")
    return f"r{value:02X}"


def register_pattern(reg: str) -> re.Pattern[str]:
    canonical = normalize_register(reg)
    return re.compile(r"(?<![\w])" + re.escape(canonical) + r"(?![\w])", re.I)


class Library:
    """Both languages plus the image folder."""

    def __init__(self, data_dir: Path | None = None) -> None:
        if data_dir is None:
            data_dir = Path(str(resources.files("thermia_kb_mcp") / "data"))
        self.data_dir = data_dir
        self.kbs: dict[str, KnowledgeBase] = {
            lang: KnowledgeBase((data_dir / name).read_text(encoding="utf-8"), lang) for lang, name in KB_FILES.items()
        }
        self.image_dir = data_dir / "images"

    def kb(self, lang: str) -> KnowledgeBase:
        key = (lang or "en").lower()[:2]
        if key not in self.kbs:
            raise ValueError(f"unknown language {lang!r}; use 'en' or 'pt'")
        return self.kbs[key]

    def images(self) -> list[str]:
        if not self.image_dir.is_dir():
            return []
        return sorted(p.name for p in self.image_dir.iterdir() if p.suffix.lower() in _IMAGE_EXT)

    def image_path(self, name: str) -> Path:
        candidates = self.images()
        if name in candidates:
            return self.image_dir / name
        # Allow a unique prefix/substring, e.g. "ELEC_p040" or "sheet2".
        matches = [c for c in candidates if name.lower() in c.lower()]
        if len(matches) == 1:
            return self.image_dir / matches[0]
        if not matches:
            raise FileNotFoundError(f"no image matches {name!r}; call list_images")
        raise FileNotFoundError(f"{name!r} is ambiguous: {', '.join(matches)}")


# --- original source documents ---------------------------------------------------------------------------------

SOURCE_TITLES: dict[str, str] = {
    "INST": "Thermia Duo – Installation instructions 9680-54961001 v4 (PDF page = printed page)",
    "ELEC": "Thermia Duo – Electrical installation instructions 9680-55353001 Rev 2 (PDF page = printed + 2)",
    "USER": "Thermia Duo – User's manual 9680-54962001 Rev 2 (PDF page = printed + 2)",
    "EXP1": "Thermia Diplomat Expansion Card instructions 9680-55173001 Rev 3 (wiring drawing on p.7)",
    "EXP2": "Expansion card installation 086U6715, multilingual (English p.4–5)",
    "COOL": "Cooling module Passive / Passive-Active installation 086U7815, multilingual (English p.5, wiring p.28–29)",
    "FAN": "Zantia fan-coil (ventiloconvector) catalogue, Portuguese",
}


def _source_files(data_dir: Path) -> dict[str, Path]:
    src = data_dir / "sources"
    out: dict[str, Path] = {}
    if src.is_dir():
        for p in sorted(src.glob("*.pdf")):
            out[p.name.split("_", 1)[0].upper()] = p
    return out


def _open_pdf(path: Path):
    import pypdfium2 as pdfium  # imported lazily: only needed for source pages

    return pdfium.PdfDocument(str(path))


def list_sources(data_dir: Path) -> list[dict[str, object]]:
    rows = []
    for tag, path in _source_files(data_dir).items():
        pdf = _open_pdf(path)
        try:
            pages = len(pdf)
        finally:
            pdf.close()
        rows.append({"tag": tag, "file": path.name, "pages": pages, "title": SOURCE_TITLES.get(tag, "")})
    return rows


def _source_page(data_dir: Path, tag: str, page: int):
    files = _source_files(data_dir)
    key = tag.strip().upper()
    if key not in files:
        raise ValueError(f"unknown source {tag!r}; available: {', '.join(files)}")
    pdf = _open_pdf(files[key])
    if not 1 <= page <= len(pdf):
        n = len(pdf)
        pdf.close()
        raise ValueError(f"{key} has pages 1–{n} (PDF page numbers, as cited in the knowledge base)")
    return pdf, pdf[page - 1]


def render_source_page(data_dir: Path, tag: str, page: int, dpi: int = 110) -> bytes:
    """Render one PDF page (1-based PDF page number, as cited in the KB) to PNG bytes."""
    import io

    dpi = max(50, min(dpi, 300))
    pdf, pg = _source_page(data_dir, tag, page)
    try:
        bitmap = pg.render(scale=dpi / 72)
        img = bitmap.to_pil()
        buf = io.BytesIO()
        img.save(buf, format="PNG", optimize=True)
        return buf.getvalue()
    finally:
        pdf.close()


def source_page_text(data_dir: Path, tag: str, page: int) -> str:
    """Plain text of one PDF page. Schematics are vector drawings, so their text is sparse – render them instead."""
    pdf, pg = _source_page(data_dir, tag, page)
    try:
        return pg.get_textpage().get_text_range()
    finally:
        pdf.close()
