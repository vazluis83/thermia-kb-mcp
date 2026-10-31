"""MCP server exposing the Thermia Duo 12 (400 V) knowledge base.

Run with stdio (default, for Claude Desktop / Claude Code / any MCP client):
    thermia-kb-mcp
or over HTTP (streamable-http) for remote clients:
    thermia-kb-mcp --http --host 0.0.0.0 --port 8000
"""

from __future__ import annotations

import argparse
import re
from typing import Any

from mcp.server.mcpserver import Image, MCPServer

from .kb import (
    Hit,
    Library,
    list_sources,
    register_pattern,
    render_source_page,
    source_page_text,
    terminal_pattern,
)

INSTRUCTIONS = """\
Knowledge base for the Thermia Duo 12 400 V 3N ground-source heat pump (standard drawing 56960 and Duo Optimum 12
drawing 57156): specifications, electrical wiring and terminals, control logic, menus and factory settings,
alarms, expansion card, cooling module, Zantia fan coils, and ESP32 integration (EXT I2C bus register map, room
sensor protocol on 303/304, EVU on 307/308).

How to use:
- Start with search_kb or list_sections; read whole sections with get_section (e.g. "6.1" = control unit relay
  terminals, "16.8" = factory settings, "21.5" = EXT register map).
- lookup_terminal("211") / lookup_register("r32") collect every table row about one terminal or register.
- Facts carry source tags like [ELEC p.40] = source PDF and PDF page; section 0.1 lists the files.
- Confidence markers: [schematic] read from a drawing, [inference] deduction, [community] third-party
  reverse-engineering. Say so when an answer relies on them.
- get_image returns pre-rendered schematic pages; list_images shows names (they encode source and page).
- The original PDFs are included: list_source_documents, then get_source_page(source, page) renders any cited
  page (e.g. [ELEC p.40] -> source='ELEC', page=40) and get_source_page_text extracts its text. Use them to
  verify a citation or to answer something the knowledge base does not cover.
- Languages: lang="en" (default) or lang="pt" (European Portuguese).
Safety: this is reference data, not authority to work on mains wiring. Advise a qualified electrician for 400 V
work and never suggest bypassing the pump's safety devices (B1/B2/B3 pressure switches, F11, T1).
"""

server = MCPServer(name="thermia-duo12-kb", instructions=INSTRUCTIONS, version="0.1.0")
_lib: Library | None = None


def lib() -> Library:
    global _lib
    if _lib is None:
        _lib = Library()
    return _lib


def _hits(hits: list[Hit]) -> list[dict[str, Any]]:
    return [{"section": h.section_id, "title": h.section_title, "text": h.text} for h in hits]


@server.tool()
def list_sections(lang: str = "en") -> list[dict[str, str]]:
    """List all numbered sections of the knowledge base (id, title, level). lang: 'en' or 'pt'."""
    kb = lib().kb(lang)
    return [{"id": s.id, "title": s.title, "level": "section" if s.level == 2 else "subsection"} for s in kb.sections]


@server.tool()
def get_section(section_id: str, lang: str = "en") -> str:
    """Return the full Markdown of a section. A top-level id like '6' includes its subsections; '6.1' returns only
    that subsection. lang: 'en' or 'pt'."""
    kb = lib().kb(lang)
    text = kb.get_section(section_id)
    if text is None:
        raise ValueError(f"unknown section {section_id!r}; valid ids: {', '.join(kb.section_ids())}")
    return text


@server.tool()
def search_kb(query: str, lang: str = "en", max_results: int = 10) -> list[dict[str, Any]]:
    """Keyword search over paragraphs, list items and table rows (accent-insensitive). Returns the best matching
    blocks with their section id; read the section with get_section for context. lang: 'en' or 'pt'."""
    max_results = max(1, min(max_results, 50))
    return [
        {"section": h.section_id, "title": h.section_title, "score": h.score, "text": h.text}
        for h in lib().kb(lang).search(query, max_results)
    ]


@server.tool()
def lookup_terminal(terminal: str, lang: str = "en") -> list[dict[str, Any]]:
    """Every table row / note mentioning a terminal of the heat pump, expansion card or cooling module, e.g. '211',
    '303', '1L1', 'PE5', '251', '357'. Gives function, wiring, wire number and source page."""
    if not re.fullmatch(r"[A-Za-z0-9]{1,6}", terminal.strip()):
        raise ValueError("terminal must be a short label such as 211, 303, 1L1, N3, PE5")
    pattern = terminal_pattern(terminal)
    sections = {"4", "5", "6", "7", "8", "10", "11", "12", "13", "14", "17", "18", "20", "22", "23"}
    return _hits(lib().kb(lang).lookup_token(pattern, sections))


@server.tool()
def lookup_register(register: str, lang: str = "en") -> list[dict[str, Any]]:
    """Everything about one EXT-bus register (ThermIQ map, as used by esphome-thermia): accepts 'r32', '0x32' or
    '32' (hex). Returns the register-map rows with meaning, unit, range, matching pump menu parameter and whether it
    is confirmed on real hardware."""
    pattern = register_pattern(register)
    return _hits(lib().kb(lang).lookup_token(pattern, {"21", "22", "26"}))


@server.tool()
def list_images() -> list[str]:
    """Names of the rendered schematic / drawing images. Names encode source and PDF page, e.g.
    'ELEC_p040_Duo12-400V_sheet2_control-unit-E1.png' = electrical installation manual, PDF page 40."""
    return lib().images()


@server.tool()
def get_image(name: str) -> Image:
    """Return one image (PNG/JPG; SVG is returned as an image with format svg+xml). Accepts the exact name or a
    unique fragment such as 'ELEC_p040' or 'sheet3_external'."""
    path = lib().image_path(name)
    fmt = "svg+xml" if path.suffix.lower() == ".svg" else path.suffix.lower().lstrip(".").replace("jpg", "jpeg")
    return Image(data=path.read_bytes(), format=fmt)


@server.tool()
def list_source_documents() -> list[dict[str, Any]]:
    """The original PDF manuals the knowledge base was built from: tag (as used in citations like [ELEC p.40]),
    file name, page count and title."""
    return list_sources(lib().data_dir)


@server.tool()
def get_source_page(source: str, page: int, dpi: int = 110) -> Image:
    """Render one page of an original PDF so you can check a citation or read a schematic yourself.
    source: tag INST, ELEC, USER, EXP1, EXP2, COOL or FAN. page: PDF page number exactly as cited in the knowledge
    base (e.g. [ELEC p.40] -> source='ELEC', page=40). dpi 50–300; use ~200 for dense schematics."""
    return Image(data=render_source_page(lib().data_dir, source, page, dpi), format="png")


@server.tool()
def get_source_page_text(source: str, page: int) -> str:
    """Extract the text layer of one page of an original PDF (same arguments as get_source_page). Schematic pages
    contain little text; render them with get_source_page instead."""
    return source_page_text(lib().data_dir, source, page)


@server.resource("kb://{lang}", name="knowledge-base", mime_type="text/markdown")
def kb_resource(lang: str) -> str:
    """The complete knowledge base in one language ('en' or 'pt')."""
    return lib().kb(lang).markdown


def main() -> None:
    parser = argparse.ArgumentParser(description="Thermia Duo 12 knowledge-base MCP server")
    parser.add_argument("--http", action="store_true", help="serve streamable HTTP instead of stdio")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    lib()  # fail fast if the data files are missing
    if args.http:
        server.run("streamable-http", host=args.host, port=args.port)
    else:
        server.run()


if __name__ == "__main__":
    main()
