# thermia-kb-mcp

An [MCP](https://modelcontextprotocol.io) server that gives any AI assistant (Claude, ChatGPT, Cursor, local models, …)
a verified technical knowledge base for the **Thermia Duo 12, 400 V 3N** ground-source heat pump, plus the original
manuals it was built from.

It is meant for people building their own controller or monitor (ESP32 / ESPHome / Home Assistant) for this pump,
and for anyone servicing or wiring one.

**What is in it**

- Knowledge base in **English** and **European Portuguese**, ~1,000 lines each:
  - specifications
  - power and control wiring with wire numbers
  - every control-unit terminal (211–220, 301–334)
  - sensor resistance tables with Steinhart–Hart fits
  - start/stop logic, menus, all factory settings with limits, alarms
  - expansion card, cooling module, fan coils
  - **ESP32 integration**: the EXT I2C bus with the full register map, the room-sensor protocol on 303/304, and EVU on 307/308
- Every fact carries its source and PDF page, e.g. `[ELEC p.40]`.
- Facts read from drawings or reverse-engineered by the community are marked as such.
- 45 pre-rendered schematic pages.
- The 7 original PDFs (~29 MB). The server can render or extract text from any page, so a model can verify a citation itself.

Covers the standard Duo 12 (drawing 56960) and the Duo Optimum 12 (drawing 57156). Much of it also applies to the
other Duo sizes and to Diplomat / Danfoss DHP pumps of the same generation, but check against your own unit.

## Tools

| Tool | What it does |
|---|---|
| `list_sections(lang)` | Table of contents (section ids like `6.1`, `16.8`, `21.5`) |
| `get_section(section_id, lang)` | Full Markdown of a section (`6` includes `6.1`, `6.2`, …) |
| `search_kb(query, lang, max_results)` | Accent-insensitive keyword search over paragraphs and table rows |
| `lookup_terminal(terminal, lang)` | Everything about one terminal: `211`, `303`, `1L1`, `PE5`, `357`, … |
| `lookup_register(register, lang)` | Everything about one EXT-bus register: `r32`, `0x33`, `19` (hex) |
| `list_images()` / `get_image(name)` | Pre-rendered schematic pages (name or unique fragment, e.g. `ELEC_p040`) |
| `list_source_documents()` | The original PDFs with their citation tags |
| `get_source_page(source, page, dpi)` | Render any page of an original PDF, e.g. `source="ELEC", page=40` |
| `get_source_page_text(source, page)` | Text layer of one PDF page |

Resource: `kb://en`, `kb://pt` – the complete knowledge base. `lang` is `en` (default) or `pt`.

## Install and connect

Requires Python ≥ 3.10. The easiest way is [uv](https://docs.astral.sh/uv/), which runs it straight from GitHub:

```sh
uvx --from git+https://github.com/vazluis83/thermia-kb-mcp thermia-kb-mcp
```

**Claude Code**

```sh
claude mcp add thermia-kb -- uvx --from git+https://github.com/vazluis83/thermia-kb-mcp thermia-kb-mcp
```

**Claude Desktop / other clients using a JSON config**

```json
{
  "mcpServers": {
    "thermia-kb": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/vazluis83/thermia-kb-mcp", "thermia-kb-mcp"]
    }
  }
}
```

**Without uv**

```sh
pip install git+https://github.com/vazluis83/thermia-kb-mcp
thermia-kb-mcp                                   # stdio
thermia-kb-mcp --http --host 0.0.0.0 --port 8000 # streamable HTTP at http://HOST:8000/mcp
```

The knowledge base itself is plain Markdown, so you can also read it directly or paste it into any model:
[`src/thermia_kb_mcp/data/thermia-duo12-knowledge-base-EN.md`](src/thermia_kb_mcp/data/thermia-duo12-knowledge-base-EN.md) ·
[`…-PT.md`](src/thermia_kb_mcp/data/thermia-duo12-knowledge-base-PT.md).

## Source documents

| Tag | File | Document |
|---|---|---|
| INST | `INST_Duo-installation_9680-54961001.pdf` | Thermia Duo – Installation instructions, v4 |
| ELEC | `ELEC_Duo-electrical-installation_9680-55353001.pdf` | Thermia Duo – Electrical installation (all Duo schematics), Rev 2 |
| USER | `USER_Duo-user-manual_9680-54962001.pdf` | Thermia Duo – User's manual, Rev 2 |
| EXP1 | `EXP1_Diplomat-expansion-card_9680-55173001.pdf` | Thermia Diplomat expansion card, Rev 3 |
| EXP2 | `EXP2_Expansion-card-install_086U6715.pdf` | Expansion card installation 086U6715 (multilingual) |
| COOL | `COOL_Cooling-module-install_086U7815.pdf` | Cooling module passive / passive-active 086U7815 (multilingual) |
| FAN | `FAN_Zantia-ventiloconvectores.pdf` | Zantia fan-coil catalogue (Portuguese) |

Page numbers in citations are **PDF page numbers**.

## Development

```sh
pip install -e ".[test]"
pytest
```

## Safety

This is reference information, not instructions to work on live equipment. The pump runs on 400 V three-phase:
mains work must be done by a qualified electrician. Never bypass the pump's safety devices (pressure switches B1/B2/B3,
overload F11, heater guard T1). Writing to the pump over the EXT bus is unacknowledged and at your own risk.

## Credits and licences

- Server code and the knowledge-base text: MIT (see [LICENSE](LICENSE)).
- EXT-bus protocol, register map and room-sensor protocol come from
  [mdepa91/esphome-thermia](https://github.com/mdepa91/esphome-thermia),
  [mdepa91/esphome-thermia-room](https://github.com/mdepa91/esphome-thermia-room) (MIT) and
  [ThermIQ/thermiq_mqtt-ha](https://github.com/ThermIQ/thermiq_mqtt-ha) (MIT), building on reverse engineering by rainisto.
- The PDF manuals and the images rendered from them are © their respective owners (Thermia Värme AB / Danfoss,
  Zantia). They are included unmodified for reference by owners of this equipment and are not covered by the MIT
  licence. Rights holders can ask for removal by opening an issue.
- Not affiliated with Thermia, Danfoss or Zantia.
