import re
import sys

import anyio
import pytest

from thermia_kb_mcp.kb import (
    Library,
    list_sources,
    normalize_register,
    register_pattern,
    render_source_page,
    source_page_text,
    terminal_pattern,
)


@pytest.fixture(scope="module")
def lib():
    return Library()


def test_both_languages_have_same_structure(lib):
    en, pt = lib.kb("en"), lib.kb("pt")
    assert en.section_ids() == pt.section_ids()
    assert "21.5" in en.section_ids() and "16.8" in en.section_ids()
    assert en.markdown.count("\n|") == pt.markdown.count("\n|")


def test_get_section_includes_subsections(lib):
    kb = lib.kb("en")
    top = kb.get_section("6")
    assert "### 6.1" in top and "### 6.3" in top
    assert "### 6.2" not in kb.get_section("6.1")
    assert kb.get_section("§16.8").startswith("### 16.8")
    assert kb.get_section("99") is None


def test_search_ranks_relevant_blocks(lib):
    hits = lib.kb("en").search("EVU 307 308")
    assert hits and any("EVU" in h.text for h in hits[:3])
    assert lib.kb("pt").search("ligação")  # accent folding / Portuguese


@pytest.mark.parametrize(
    "terminal, must_contain",
    [("211", "Brine pump"), ("214", "Diverting valve"), ("303", "Room sensor"), ("1L1", "Compressor")],
)
def test_lookup_terminal(lib, terminal, must_contain):
    hits = lib.kb("en").lookup_token(terminal_pattern(terminal), {"4", "5", "6", "7"})
    assert any(must_contain in h.text for h in hits)


def test_terminal_pattern_does_not_match_numbers_with_units():
    p = terminal_pattern("20")
    assert not p.search("MAX CURRENT 20 A")
    assert not p.search("value 20 °C")
    assert p.search("terminal 20 here")
    assert not terminal_pattern("14").search("value 2.14 or 2,14")
    assert terminal_pattern("1L1").search("| 1L1, 1L2, 1L3 |")


def test_registers():
    assert normalize_register("r32") == "r32"
    assert normalize_register("0x0a") == "r0A"
    assert normalize_register("R3c") == "r3C"
    with pytest.raises(ValueError):
        normalize_register("r80")
    with pytest.raises(ValueError):
        normalize_register("hello")
    assert register_pattern("r33").search("| r33 | main_mode |")
    assert not register_pattern("r3").search("r33")


def test_lookup_register(lib):
    hits = lib.kb("en").lookup_token(register_pattern("r33"), {"21"})
    assert any("main_mode" in h.text for h in hits)


def test_images(lib):
    names = lib.images()
    assert len(names) >= 40
    assert lib.image_path("ELEC_p040").name.startswith("ELEC_p040")
    with pytest.raises(FileNotFoundError):
        lib.image_path("sheet2")  # ambiguous
    with pytest.raises(FileNotFoundError):
        lib.image_path("does-not-exist")


def test_source_documents(lib):
    tags = {s["tag"] for s in list_sources(lib.data_dir)}
    assert tags == {"INST", "ELEC", "USER", "EXP1", "EXP2", "COOL", "FAN"}
    png = render_source_page(lib.data_dir, "ELEC", 40, dpi=60)
    assert png[:4] == b"\x89PNG"
    assert "307" in source_page_text(lib.data_dir, "inst", 24)
    with pytest.raises(ValueError):
        render_source_page(lib.data_dir, "ELEC", 999)
    with pytest.raises(ValueError):
        render_source_page(lib.data_dir, "NOPE", 1)


def test_citations_point_to_existing_pages(lib):
    """Every [TAG p.N] citation in the knowledge base must refer to a page that exists."""
    pages = {s["tag"]: s["pages"] for s in list_sources(lib.data_dir)}
    text = lib.kb("en").markdown
    cites = re.findall(r"\[(INST|ELEC|USER|EXP1|EXP2|COOL|FAN) p\.(\d+)", text)
    assert len(cites) > 50
    for tag, page in cites:
        assert 1 <= int(page) <= pages[tag], (tag, page)


def test_stdio_server_end_to_end():
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    async def run():
        params = StdioServerParameters(command=sys.executable, args=["-m", "thermia_kb_mcp.server"])
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = {t.name for t in (await session.list_tools()).tools}
                assert {"search_kb", "get_section", "lookup_terminal", "lookup_register", "get_image",
                        "get_source_page", "list_source_documents"} <= tools
                res = await session.call_tool("lookup_terminal", {"terminal": "212"})
                assert not res.is_error and "R1" in str(res.content)
                res = await session.call_tool("get_source_page", {"source": "ELEC", "page": 41, "dpi": 60})
                assert not res.is_error and res.content[0].type == "image"
                res = await session.call_tool("get_section", {"section_id": "nope"})
                assert res.is_error

    anyio.run(run)
