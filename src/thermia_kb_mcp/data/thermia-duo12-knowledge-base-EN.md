# Thermia Duo 12 (400 V 3N) – technical knowledge base

Reference for building an ESP32 controller/monitor for a **Thermia Duo 12, 400 V three-phase** brine/water (ground-source) heat pump. It collects everything in the supplied manuals about wiring, electrical design, control logic, parameters, accessories and integration, plus the reverse-engineered EXT bus and room-sensor protocols used by the `esphome-thermia` projects.

Language: English. A European Portuguese version with the same content is in `thermia-duo12-knowledge-base-PT.md`.

---

## 0. How to use this document

### 0.1 Source files and page numbering

Every fact carries a source tag such as **[INST p.21]**. Page numbers are **PDF page numbers**, the number a PDF viewer shows. Where the printed page number differs, it is given as "printed p.X".

| Tag | File (as supplied) | Document | PDF page vs printed page |
|---|---|---|---|
| **INST** | `180449c4-Duo-installation.pdf` | Thermia Duo – Installation instructions, 9680-54961001, Version 4 (60 pp.) | same |
| **ELEC** | `b90a054f-Duo-electrical_installation.pdf` | Thermia Duo – Electrical installation instructions, 9680-55353001 Rev. 2, 2006 (139 pp.) | PDF = printed + 2 |
| **USER** | `6dbc84d0-Duo-user_manual.pdf` | Thermia Duo – User's manual, 9680-54962001 Rev. 2 (36 pp.) | PDF = printed + 2 |
| **EXP1** | `e73e7672-Expansionskort_EN_rev3.pdf` | Thermia Diplomat Expansion Card – Instructions, 9680-55173001 Rev 3 (9 pp.) | PDF p.3–6 = printed p.1–4; p.7 = wiring drawing 54201 EN; p.8 = printed p.5 (blank) |
| **EXP2** | `d05bb0cb-Thermia_expansioncard_install_086U6715_MULTI.pdf` | Expansion card installation instructions 086U6715 (multilingual; English on p.4–5) | same |
| **COOL** | `53c4c5d0-CoolingModule_install_086U7815_MULTI.pdf` | Cooling module Passive / Passive-Active installation 086U7815 (English text p.5, drawings p.14–29) | same |
| **FAN** | `b442635d-Ventiloconvectores.pdf` | Zantia fan-coil (ventiloconvector) catalogue, Portuguese (printed pp. 296–326) | PDF p.N = printed p.294+N |
| **REPO-T** | github.com/mdepa91/esphome-thermia @ `ab88ec7` (2026-10-14) | ESPHome EXT-port component (README, `__init__.py`, `example.yaml`, `docs/`) | – |
| **REPO-R** | github.com/mdepa91/esphome-thermia-room @ `f8f71de` (2026-10-24) | ESPHome room-sensor emulator (README) | – |
| **TIQ** | github.com/ThermIQ/thermiq_mqtt-ha @ `e1123c5` (2026-10-22), `heatpump/thermiq_regs.py` | Full register map used by REPO-T | – |

In the GitHub repository / MCP server the PDFs are in `src/thermia_kb_mcp/data/sources/`, renamed `TAG_<title>.pdf` (e.g. `ELEC_Duo-electrical-installation_9680-55353001.pdf`). The MCP tool `get_source_page(source, page)` renders any cited page.

### 0.2 Image folder

`images/` holds rendered pages of every schematic and drawing that matters. File names give the source and PDF page, e.g. `ELEC_p040_Duo12-400V_sheet2_control-unit-E1.png` = ELEC, PDF page 40. The index is in [section 27](#27-image-index).

### 0.3 Confidence markers

- No marker: stated in the source text or table.
- **[schematic]**: read by me from a drawing (traced wires). Accurate to the drawing, but worth checking on the unit.
- **[inference]**: my deduction from several facts; not stated anywhere. Verify before relying on it.
- **[community]**: reverse-engineered by third parties (REPO-T / REPO-R / TIQ), not from Thermia.

### 0.4 Which Duo 12 do you have?

The documents cover several variants. Look at the type plate and control board:

| Variant | Supply | Drawing no. | Where |
|---|---|---|---|
| **Duo 12 (standard), 400 V 3N** | 400 V 3-N | 56960 (sheets 1–4, rev 2, 2006) | ELEC p.39–42 (printed 37–40) |
| **Duo Optimum 12, 400 V 3N** | 400 V 3-N | 57156 (sheets 1–5, rev 1, 2006) | ELEC p.102–107 (printed 100–105) |
| Duo 12 ES | 230 V 1-N | – | ELEC printed p.17–20; not covered in detail here |

The **Optimum** has speed-controlled (0–10 V) circulation pumps with alarm contacts and an extra "Thermia Duo Optimum" service menu ([§16.9](#169-optimum-only-menu-inst-p42)). Everything else is shared. On the tri-phase standard unit, assume drawing 56960 unless the pumps are speed-controlled Wilo units wired to terminals 327–334.

### 0.5 Reference installation (this repository)

The unit this knowledge base was built for is a **Thermia Duo Optimum 12, 400 V 3N, installed without a hot-water tank**. For it:

- Use the Optimum drawings, 57156: [ELEC p.102–107]. They add speed-controlled Wilo pumps on 327–334, the Optimum service menu ([§16.9](#169-optimum-only-menu-inst-p42)) and the pump alarms CIRC. PUMP / BRINE PUMP ([§16.3](#163-alarms-inst-p34-p4850-user-p2930)). There is no WSK in the 309/310 overload chain.
- **No tank**, so the hot-water sensors 311/312 (WW TEMP) and 325/326 (TOPP TWS) are not connected, and the diverting valve output 214 / M3 has no hot-water circuit behind it.
  - Set **WARMWATER → START = OFF**, which per [INST p.38] means "no sensor alarm". Otherwise the open sensor raises **SENSOR WARMWATER** [INST p.34].
  - Set TOPH. INTERVAL = OFF [INST p.52].
  - **[inference]** Verify on the display that hot-water production never starts. Check whether M3 is physically fitted or plugged, and that the heating circuit is not routed through its hot-water port.
- With no hot-water demand, the TIME HEAT / TIME WARMWATER alternation, the 45-min hot-water limit and the hot-water top-up logic ([§15.4](#154-hot-water-inst-p30-p33-p4647)) never apply.
- EXT-bus registers specific to this setup: r1E / r1F (pump speeds %), r62 bit 0x40 (Optimum installed), r44 (hot-water start; how OFF is encoded is unknown, so read it before writing).

---

## 1. Product overview

- Complete ground-source heating unit: scroll compressor, stainless-steel heat exchangers, brine (collector) pump, heating circulation pump, hot-water diverting valve, built-in 9 kW 3-step electric immersion heater in the supply line, and control computer with graphic display. Hot water is made in an **external** tank. [USER p.6–7]
- Maximum supply temperature to the heating system 55 °C ("low-temperature system"). The heat pump covers as much of the demand as possible before the auxiliary heater is switched in. [USER p.6]
- Three fluid circuits: brine/coolant circuit (antifreeze mix, ground loop), refrigerant circuit (R407C on 400 V models), heating circuit (water to radiators/UFH and tank). Refrigerant loop: evaporator → compressor → condenser → **sub-cooler** (pre-heats heating return water) → expansion valve. [USER p.7–8]
- Control panel "Thermia Diplomat": character/graphic display, 4 keys (+, −, right, left) and an alarm LED (steady = running, flashing = alarm). [INST p.31], [USER p.9–10]
- Control unit **E1**: Kimsafe AB, part 9588-55701001 (standard) / 9588-56464001 (Optimum). Display **E3**: Kimsafe 9588-55702001 / 9588-56562001. [ELEC p.42, p.107]
- **[community]** The Duo controller board is built around a Microchip **PIC16F887**, with Omron G2RL-1-E 24 V DC (16 A/250 V) relays. The display connects via an RJ45 socket; the **EXT** header (GND, SDA, SCL, 5 V) sits next to it on the top edge. [REPO-T README, `docs/hardware/ext-port-pinout.jpg`]. Photo: `images/REPO_esphome-thermia_ext-port-pinout.jpg`.

---

## 2. Technical specifications – Duo 12 (400 V)

From the Duo 400 V table [INST p.55] (`images/INST_p055_tech-specs-400V.png`). Values for the other sizes are in [§2.2](#22-full-400-v-table-all-sizes-inst-p55).

| Item | Duo 12 (400 V 3-N) |
|---|---|
| Refrigerant | R407C, **1.7 kg** |
| Test / design pressure | 3.2 MPa / 2.9 MPa |
| Compressor | Scroll, ester oil (Copeland, 400 V, part 9686-53314001 [ELEC p.42]) |
| Mains supply | **400 V 3-N** (3 phases + neutral + PE) |
| Compressor electrical power | **4.4 kW** |
| Compressor + aux heater | **7.4 / 10.4 / 13.4 kW** with 3 / 6 / 9 kW aux heater |
| Immersion (aux) heater | 3 / 6 / 9 kW (2 element banks: EP2 = 3 kW, EP1 = 6 kW) |
| Starting current (LRA) | **28 A** (drawing 56960 shows a soft starter R1 in the compressor circuit) |
| Fuse (group) | **16 A / 20 A / 25 A** with 3 / 6 / 9 kW aux heater |
| Heat output (EN 255, brine in/heating out 0/35 °C and 0/50 °C, incl. pumps) | **11.12 kW / 10.53 kW** |
| COP (same conditions) | **4.5 / 3.3** |
| Nominal flow – brine (coolant) | **0.63 l/s** (≈ 2.27 m³/h) |
| Nominal flow – heating medium | **0.26 l/s** (≈ 0.94 m³/h) |
| External available pressure – brine (standard) | **64 kPa** (requires collector hose 40 × 2.4 mm) |
| External available pressure – heating (standard) | **48 kPa** |
| External available pressure – Duo Optimum, brine / heating | **82 kPa / 97 kPa** |
| Brine in temperature max/min | **+20 / −10 °C** |
| Heating medium temperature max/min | **55 / 20 °C** |
| Weight (no packaging) | **165 kg** |
| Thermal overload F11 setting range | 9–13 A [ELEC p.42] |

Notes [INST p.55]: "External available pressure" is the pressure drop allowed outside the heat pump before the flow falls below nominal. "*" in the table = data not available at the time of printing.

### 2.1 Refrigerant handling [INST p.54]

- 400 V Duo: **R407C**; 230 V Duo: R404A. Using another refrigerant voids the warranty unless Thermia approves it in writing.
- Not flammable; heavier than air (risk of suffocation in small, unventilated rooms); forms phosgene with open flame. Work only by certified refrigeration personnel; refill amount per nameplate.

### 2.2 Full 400 V table (all sizes) [INST p.55]

| | Duo 4 | Duo 6 | Duo 8 | Duo 10 | **Duo 12** | Duo 16 |
|---|---|---|---|---|---|---|
| R407C charge (kg) | 0.75 | 1.1 | 1.25 | 1.6 | **1.7** | 1.8 |
| Compressor power (kW) | * | 2 | 2.3 | 3.6 | **4.4** | 5.6 |
| Comp. + AH 3/6/9 kW (kW) | * | 5.0/8.0/11.0 | 5.3/8.3/11.3 | 6.6/9.6/12.6 | **7.4/10.4/13.4** | 8.6/11.6/14.6 |
| LRA (A) | 36 | 14 | 25 | 28 | **28** | 47 |
| Fuse 3/6/9 kW AH (A) | * | 10/16/20 | 16/16/20 | 16/16/20 | **16/20/25** | 20/20/25 |
| Output 0/35 / 0/50 (kW) | 3.76/3.67 | 5.78/5.52 | 8.13/7.73 | 9.54/9.24 | **11.12/10.53** | 16.61/15.78 |
| COP 0/35 / 0/50 | 4.07/2.83 | 4.2/3.1 | 4.6/3.4 | 4.4/3.3 | **4.5/3.3** | 4.4/3.2 |
| Brine flow (l/s) | 0.20 | 0.31 | 0.47 | 0.57 | **0.63** | 0.92 |
| Heating flow (l/s) | 0.09 | 0.13 | 0.19 | 0.22 | **0.26** | 0.4 |
| Ext. pressure brine / heating (kPa) | 35/50 | 31/43 | 33/39 | 32/34 | **64/48** | 56/40 |
| Optimum brine / heating (kPa) | * | 89/109 | 92/106 | 82/99 | **82/97** | 70/88 |
| Weight (kg) | 140 | 145 | 150 | 155 | **165** | 175 |

[INST p.56] has the 230 V "ES" models (R407C, immersion 1.5/3/4.5 kW except ES16) and [INST p.57] the "Duo D" 230 V models (R404A). They are not the user's unit.

---

## 3. Mechanical and hydraulic

### 3.1 Placement and dimensions [INST p.4–8]

- Not where it can freeze; floor must carry the weight; stable floor; adjustable feet. Condensate drain from drip bowl to floor drain, hose 14/10 mm, exits through bottom panel. [INST p.4]
- Unit size: **600 mm wide × 690 mm deep × 1490 mm high** (feet in highest position). [INST p.7]
- Service clearance: 300 mm each side, 300 mm above, 600 mm in front, 10 mm behind. [INST p.7]
- Front panel: open hinged top panel, remove screws, slide panel up and off – mind the control-system wiring. [INST p.6, p.28]

### 3.2 Pipe connections [INST p.8] (`images/INST_p008_connection-dimensions.png`)

| Connection | Size |
|---|---|
| Brine out (from HP) | 28 mm copper |
| Brine in (to HP) | 28 mm copper |
| Heating supply line | 28 mm copper |
| Heating return line | 28 mm copper |
| Line from hot-water tank | 22 mm (can be connected left or right) |
| Cable exits (power/sensors) | top panel; separate exit for communication cable |

### 3.3 Internal components [INST p.13] (`images/INST_p013_heat-pump-components.png`)

1 front panel · 2 instrument panel · 3 **switching (diverting) valve** · 4 supply line sensor · 5 heating circulation pump · 6 electric aux heater · 7 evaporator (insulated) · 8 expansion valve · 9 drying filter · 10 brine (cooling-system) circulation pump · 11 heating return 28 mm Cu · 12 heating supply 28 mm Cu · 13 cable exits for power and sensors · 14 sub-cooler · 15 return line sensor · 16 condenser with drain for primary side · 17 compressor · 18 brine in 28 mm Cu · 19 brine out 28 mm Cu · 20 exit for communication cable.

### 3.4 Hydraulic systems [INST p.11–12]

- **System VL** (`images/INST_p011_hydraulic-system-VL.png`): heat pump with its internal electric heater; radiators/UFH, hot-water tank via the internal diverting valve, expansion.
- **System D** (`images/INST_p012_hydraulic-system-D.png`): two layouts – "Duo with external shunt option" and "Duo in parallel with external immersion heater". (Drawing position numbers 4, 5, 7, 47, 50, 51, 57–62, 64, 65, 77, 87, 96–99, 115, 117 are not explained in the text.)

### 3.5 Safety valve, expansion, filling [INST p.9–10], [USER p.4, p.27–28]

- A heating system with closed expansion vessel needs an approved pressure gauge and safety valve, min. DN 20, max. opening pressure **1.5 bar**. The pipe from vessel to safety valve must rise continuously.
- Fill heating system to ~1 bar, bleed completely, top up. Check monthly: 1–1.5 bar; top up below 0.8 bar (cold). Do not add water-treatment chemicals. Test both safety valves (heating and tank) at least 4× per year.
- Fit the particle filter as indicated in the system layout (heating return).
- Brine lines: flexible lines through rubber sleeves in the top panel, insulated with vapour barrier. Wall entries slope ≥1 cm per 30 cm downwards to the outside; separate holes for out and in. [INST p.5, p.10]

### 3.6 Brine (coolant) filling [INST p.25–26] (`images/INST_p026_brine-filling.png`)

- Antifreeze: ethylene glycol or ethanol with corrosion inhibitor, **30 % by volume**. Collector hose DN40 holds ~1.0 l/m.
- Volume formula: (hose length + 5) × 0.30 = antifreeze volume. Example 400 m: (400+5)×0.30 = 121.5 l → freezing point ≈ −15 °C. Unit volume 5 l.
- Procedure: operating mode OFF; mix in an external container; fill with an external pump with ≤1 mm strainer via the filler connection near shut-off valve 62; close 57; open 62 and 64; open 61 with hose back to the bowl; start external pump, then start the **brine pump from the MANUAL service menu** (it switches off after ~10 min); let air collect in the bleed tank; release excess pressure at valve 60; liquid level must not fall below 2/3 of tank height; close 61 and 62; switch from OFF/manual to the chosen mode.
- **The brine pump must run to fill → electrical installation must be complete first.**
- Check: brine level must always be visible in the expansion tank; slight drop in month one is normal. [USER p.27]

### 3.7 Commissioning order [INST p.4, p.27]

1. Pipe work → 2. fill and bleed heating system → 3. electrical installation → 4. fill brine circuit → 5. adjust factory settings → 6. function test → 7. installation certificate [INST p.58].

- Do not start before heating system, tank and brine circuit are filled (pump damage).
- To run on electric heat only before the brine circuit is ready: select operating mode **ADD.HEATER** so neither brine pump nor compressor can start.
- **Phase sequence:** start the compressor; wrong rotation shows **"Err. phase seq."** → swap two incoming phases (e.g. L1 and L3). [INST p.27] (`images/INST_p027_phase-rotation-check.png`)

---

## 4. Electrical supply and power distribution

### 4.1 Supply requirements [INST p.15], [ELEC p.2]

- Permanently wired connection. Isolation by an **all-pole switch (circuit breaker) with ≥3 mm contact opening**. The safety switch is the way to de-energise the unit.
- **Max. load for externally connected units: 2 A.** [INST p.15]
- Supply cable enters through the top panel to the designated terminal block **only**.
- The max. power of the aux heater must be selected in the menu (MAX STEP). [INST p.15]
- Group fuse for Duo 12: 16 / 20 / 25 A for MAX STEP 3 / 6 / 9 kW. [INST p.55]
- Low-voltage sensor cables must be kept away from mains cables: **≥25 cm separation when run in parallel, for runs up to 100 m**; more for longer runs. [ELEC p.2]
- Before power-up: heating system, brine circuit and hot-water heater filled and vented. [ELEC p.2]

### 4.2 Incoming terminal block X1 (400 V 3N) [ELEC p.41 sheet 3], [INST p.16 fig. 8]

Images: `images/ELEC_p041_Duo12-400V_sheet3_external-connections.png`, `images/INST_p016_fig8_electrical-connections.png`.

Terminals, left to right: **N3 · 3L1 · PE5 · 1L1 · 1L2 · 1L3** | **2L1 · 2L2 · 2L3 · PE1**

| Terminal | Feeds | Source |
|---|---|---|
| 1L1, 1L2, 1L3 | Compressor (via F11 → R1 → M2) and, through jumpers, 2L1–2L3 | [ELEC p.39, p.41] |
| 2L1, 2L2, 2L3 | Aux heater (via T1 and E1 relays) | [ELEC p.39] |
| 3L1 | Control phase: F0 (10 A) → control unit, diverting valve, pressure switch; strapped to 2L1 at delivery | [ELEC p.39, p.41] **[schematic]** |
| N3 (linked to N2, N1b) | Neutral for pumps, valve, control | [ELEC p.39] |
| PE1 | Incoming protective earth | [ELEC p.41] |
| PE5 | Earth terminal (drawn as a separate PE next to 2L1–2L3; no conductor to EP drawn) | [ELEC p.39] |

- Factory default ("Strapt at delivery"): **3L1 bridged to 2L1**, and 1L1→2L1, 1L2→2L2, 1L3→2L3 jumpered, so a single 5-core cable (L1, L2, L3, N, PE) supplies everything. [ELEC p.41] **[schematic]**
- Fig. 8 (400 V): incoming 5-core cable PE→PE, core 1→**N2**, 2→**1L1**, 3→**1L2**, 4→**1L3**; jumpers 1L1–2L1, 1L2–2L2, 1L3–2L3. [INST p.16]
- The drawing shows an external 3-pole isolator **Q1** (1-2, 3-4, 5-6) in the incoming cable. [ELEC p.41]
- **[inference]** Removing the jumpers would allow separate supplies (compressor 1Lx, heater 2Lx, control 3L1) – for example for tariff control – but no procedure is given for the 400 V Duo. Fig. 8 shows separate "incoming cable to heat pump" and "to auxiliary heater" only for the 230 V version.

### 4.3 Electrical cubicle layout [INST p.17–18]

Two cubicle versions, both with: K1 compressor contactor/starter · F11 compressor overcurrent relay · F2 fuse circulation pump · F1 fuse brine pump · F0 fuse switching valve · control computer · T1 thermal cut-out electric heater · terminal blocks for incoming supply and temperature sensors. Version **53369-A** also has (9) terminal blocks for warm water, supply line and operating additional heater. Images: `images/INST_p017_electrical-cubicle-55527-B.png`, `images/INST_p018_electrical-cubicle-53369-A.png`.

Note: the 2006 Duo 12 drawing 56960 shows a **soft starter R1** instead of a contactor K1. Your unit may have either. [ELEC p.39]

### 4.4 Protection devices (Duo 12, drawing 56960) [ELEC p.42]

| Ref | Device | Rating | Protects |
|---|---|---|---|
| F0 | Merlin Gerin MCB 1P | C10 A | 3L1 control phase: control unit supply (via 217), diverting valve M3, pressure switch B1 |
| F1 | Merlin Gerin MCB 1P | C3 A | Brine pump M1 |
| F2 | Merlin Gerin MCB 1P | C3 A | Heating circulation pump M4 |
| F3 | Merlin Gerin MCB 1P | C3 A | Output 209 (aux/top heating) |
| F4 | Merlin Gerin MCB 1P | C3 A | Output 210 (oil/El) |
| F11 | Telemecanique thermal overload + aux block | 9–13 A | Compressor M2; NC aux contact 95-96 to control unit 309/310 |
| T1 | Ego temperature guard (3-pole) | 30 A 230 V | Aux heater over-temperature; opens all three heater phases |
| R1 | Kimsafe soft starter | 400 V 3N | Compressor start (drawing shows thyristors in two of the three phases – not stated in text) |

---

## 5. Power circuit – sheet 1 (Duo 12, drawing 56960) [ELEC p.39]

Image: `images/ELEC_p039_Duo12-400V_sheet1_power-circuit.png`. All wires grey ("gy-NNN") unless noted; "bl" = blue neutral. Cross-references like "/2.1B" mean sheet 2, column 1, row B. **[schematic]** for the whole section.

### 5.1 Compressor M2

1L1 / 1L2 / 1L3 (gy-501/502/503) → **F11** 1/3/5 → 2/4/6 (gy-601/602/603) → **R1 soft starter** L1/L2/L3 → U/V/W (gy-701/702/703) → **M2** T1/T2/T3 (3~), PE3.
- R1 control coil: **A1 ← control unit terminal 212**, A2 → neutral (line F). → The compressor runs when E1 relay 212 is on.
- F11 auxiliary contacts: **95-96 (NC)** → control unit 309/310 (overload trip input); 97-98 (NO) unused.

### 5.2 Brine pump M1

Control unit **211** → gy-211 → **F1** (C3 A) → gy-101 → M1 L; N blue; PE3.
- Standard Duo: M1 has a winding thermal contact **WSK** (X3 "WSK" terminal) wired in series into the overload input (350-351). [ELEC p.40, p.42]

### 5.3 Heating circulation pump M4

Control unit **213** → gy-213 → **F2** (C3 A) → gy-102 → M4 L; N blue; PE3.

### 5.4 Hot-water diverting (reversing) valve M3 – Honeywell, 9360-37547001

3-wire motorised valve: **terminal 3** = permanent L (3L1 → F0 → gy-103), **terminal 6** = switched L from control unit **214** (gy-214) = hot-water position, **terminal 2** = neutral (N2). [ELEC p.39] **[schematic]**

### 5.5 Auxiliary heater EP (Backer 3 kW + 6 kW, 9571-53938A00)

```
2L1 (gy-401) → T1 11-12 → gy-404 → E1 relay common "L1" (1)
2L2 (gy-402) → T1 21-22 → gy-407 → E1 relay common "L2" (2)
2L3 (gy-403) → T1 31-32 → gy-410 → EP1 L3 (6 kW) and gy-411 → EP2 L3 (3 kW)   (L3 not switched)
E1 "6KW" L1-side (5) → gy-405 → EP1 L1 ;  E1 "6KW" L2-side (6) → gy-406 → EP1 L2
E1 "3KW" L1-side (7) → gy-409 → EP2 L1 ;  E1 "3KW" L2-side (8) → gy-408 → EP2 L2
```

- Each bank is energised by closing **both** its L1 and L2 relay contacts on E1; L3 is permanently connected through T1.
- Steps: 3 kW = EP2 · 6 kW = EP1 · 9 kW = EP1 + EP2. [USER p.8], [INST p.39]
- T1 (Ego 30 A) breaks all three phases on over-temperature → alarm **ADD.HEATER** ("Thermal cut-out triggered"). [INST p.34]
- The control unit's on-board relays switch the heater phases directly; there is no separate heater contactor on this drawing. **[schematic]**

---

## 6. Control unit E1 – full terminal map (sheet 2) [ELEC p.40]

Image: `images/ELEC_p040_Duo12-400V_sheet2_control-unit-E1.png` (Optimum: `images/ELEC_p103_Duo12-Optimum_sheet2_control-unit-E1.png`).

E1 connectors: **Ext. COM** (expansion card / EXT bus, see [§21](#21-ext-port--i2c-bus-protocol-community-repo-t)) · **DISPLAY** (to E3) · relay/power terminals · SELV sensor terminals.

### 6.1 Relay and 230 V terminals

| E1 terminal | Function | Connected to | Type |
|---|---|---|---|
| L1 (1) | Heater relay common, phase 2L1 via T1 | gy-404 | 400 V system phase |
| 6KW (5) | Switched 2L1 → EP1 6 kW bank | gy-405 | relay output |
| 3KW (7) | Switched 2L1 → EP2 3 kW bank | gy-409 | relay output |
| L2 (2) | Heater relay common, phase 2L2 via T1 | gy-407 | phase |
| 6KW (6) | Switched 2L2 → EP1; **also feeds field terminal 209 via F3** | gy-406 | relay output |
| 3KW (8) | Switched 2L2 → EP2; **also feeds field terminal 210 via F4** | gy-408 | relay output |
| **211** | **Brine pump M1** (via F1) | gy-211 | 230 V output |
| **212** | **Compressor run** – soft starter R1 coil A1 | – | 230 V output |
| **213** | **Heating circulation pump M4** (via F2) | gy-213 | 230 V output |
| **214** | **Diverting valve M3 → hot water** (valve terminal 6) | gy-214 | 230 V output |
| **215** | **Shunt motor OPEN (+)** – field terminal 215 | – | 230 V output |
| **216** | **Shunt motor CLOSE (−)** – field terminal 216 | – | 230 V output |
| **217** | **L supply into E1** (from F0, gy-217b); also feeds flow guard terminal 1 | gy-217b | 230 V supply |
| **218** | **Input: operating pressure switch B1** (B1 fed with L from F0 via gy-104) | – | 230 V input |
| **219** | **Input: flow guard FL** return (accessory) | – | 230 V input |
| **220** | **Neutral** (N1b) | – | N |

**[schematic]** for the 211–220 allocation. Wire numbers gy-211, gy-213, gy-214, gy-217 match the terminal numbers, which supports the reading.

### 6.2 SELV (low-voltage) terminals

| Terminals | Function | Device | Wire colours |
|---|---|---|---|
| **301–302** | Supply line sensor ("Sensor radiator out", Rad Out) | B4 NTC (Betatherm 9588-54680001) | 301 white, 302 red |
| **303–304** | **Room sensor (accessory)** | room unit 086U6003 / emulator | – |
| **305–306** | **Outdoor sensor** | NTC (outdoor table) | – |
| **307–308** | **EVU / timer input** | potential-free contact or 10 kΩ | – |
| 309–310 | Overload relay trip input: chain M1 WSK (350-351, standard only) + F11 95-96 | internal | – |
| **311–312** | **Hot-water sensor** (WW TEMP) | NTC | 311 white, 312 red |
| 313–314 | Return line sensor ("Sensor radiator in", Rad In) | B6 NTC 9588-53809001 | internal |
| 315–316 | Brine out sensor | B7 NTC 9588-53808001 | internal |
| 317–318 | Brine in sensor | B8 NTC 9588-53807001 | internal |
| 319–320 | High-pressure switch | B2 Saginomiya 31 bar 9578-55973001 | internal |
| 321–322 | Low-pressure switch | B3 Saginomiya 0.8 bar 9578-55212001 | internal |
| 323–324 | Discharge pipe sensor ("TRYCKRÖR" = hot gas) | B9 NTC 9588-55322001 | internal |
| **325–326** | **Hot-water top sensor** ("TOPP TWS") | NTC | 325 white, 326 red |

All sensor, room-thermostat and EVU connections are **SELV**. [INST p.19–22]

### 6.3 Optimum-only terminals (drawing 57156 sheet 3) [ELEC p.104]

Image: `images/ELEC_p104_Duo12-Optimum_sheet3_pump-0-10V-alarm.png`.

| Terminals | Function |
|---|---|
| 327–328 | Heating circulation pump M4 alarm contact (pump wires 3, 4) |
| 329–330 | M4 speed control 0–10 V (pump wires 1, 2) |
| 331–332 | Brine pump M1 alarm contact (pump wires 3, 4) |
| 333–334 | M1 speed control 0–10 V (pump wires 1, 2) |

Both pumps: Wilo 9675-57045002. On the Optimum the overload input 309/310 has only F11 95-96 (no WSK). [ELEC p.103, p.107]

---

## 7. Field (external) connections – sheet 3 [ELEC p.41], [INST p.16, p.21]

Images: `images/ELEC_p041_Duo12-400V_sheet3_external-connections.png`, `images/INST_p021_fig9_control-and-sensor-connections.png`.

| Block | Terminals | What you connect | Notes |
|---|---|---|---|
| Incoming supply | N3, 3L1, PE5, 1L1, 1L2, 1L3, 2L1, 2L2, 2L3, PE1 | 400 V 3N + PE via isolator Q1 | see [§4.2](#42-incoming-terminal-block-x1-400-v-3n-elec-p41-sheet-3-inst-p16-fig-8) |
| Shunt valve / aux heating | **PE, N1, 215 (+), 216 (−)** | 230 V 3-point shunt motor (cable PE, 1=N1, 2=215, 3=216) | System D or sub-shunt |
| Flow guard (accessory) | **217, 219** | NC flow switch contact (1-2) | enable "F" in SYSTEM |
| Room sensor (accessory) | **303, 304** | Thermia room unit | dashed = accessory |
| Outdoor sensor | **305, 306** | outdoor NTC | standard |
| EVU (accessory) | **307, 308** | potential-free contact | |
| Top heating | **PE, N4, 209** | coil of contactor for external tank heater | 230 V, via F3 C3 A |
| Oil / El | **N4, 210** | control of external boiler/electric heater | 230 V, via F4 C3 A |
| Supply line sensor | **301 (white), 302 (red)** | B4 "Rad OUT" | moved when external heater is used |
| Hot-water sensor | **311 (white), 312 (red)** | "WW TEMP" | in tank |
| Hot-water top sensor | **325 (white), 326 (red)** | "TOPP TWS" | in tank |

- External 230 V loads (209, 210, 215/216): total max **2 A**. [INST p.15]
- 209 and 210 are **live 230 V outputs**, not dry contacts. [ELEC p.40] **[schematic]**

---

## 8. Parts lists

### 8.1 Duo 12 400 V 3N, drawing 56960 sheet 4 (rev 2, 2006-10-18) [ELEC p.42]

| Ref | Designation | Manufacturer | Electrical data | Part no. |
|---|---|---|---|---|
| B1 | Operating pressure switch | Saginomiya | 26.5 bar | 9578-37142002 |
| B1 (alt.) | Operating pressure switch | Saginomiya | 28.5 bar | 9578-55974001 |
| B2 | High-pressure switch | Saginomiya | 31 bar | 9578-55973001 |
| B3 | Low-pressure switch | Saginomiya | 0.8 bar | 9578-55212001 |
| B4 | Sensor radiator out (supply) | Betatherm | NTC | 9588-54680001 |
| B6 | Sensor radiator in (return) | Betatherm | NTC | 9588-53809001 |
| B7 | Sensor brine out | Betatherm | NTC | 9588-53808001 |
| B8 | Sensor brine in | Betatherm | NTC | 9588-53807001 |
| B9 | Sensor discharge pipe | Betatherm | NTC | 9588-55322001 |
| E1 | Control unit | Kimsafe AB | – | 9588-55701001 |
| E3 | Display | Kimsafe AB | – | 9588-55702001 |
| EP | Auxiliary heater | Backer | 3 kW / 6 kW | 9571-53938A00 |
| F0 | Circuit breaker | Merlin Gerin | 1P C10A | 9588-51463001 |
| F1–F4 | Circuit breaker | Merlin Gerin | 1P C3A | 9585-53791001 |
| F11 | Thermal overload relay | Telemecanique | 9–13 A | 9588-38379012 |
| F11 | Auxiliary switch block | Telemecanique | – | 9575-54492001 |
| M1 | Pump circulation (brine) | Wilo | – | 9675-54178001 |
| M2 | Compressor | Copeland | 400 V | 9686-53314001 |
| M3 | Reversing valve | Honeywell | – | 9360-37547001 |
| M4 | Pump circulation (heating) | Wilo | – | 9675-53865002 |
| R1 | Soft start | Kimsafe AB | 400 V 3N | 9588-56851001 |
| T1 | Temperature guard | Ego | 30 A 230 V | 9579-54513001 |
| X1 | Terminal block | Phoenix | 400 V 3N | 9583-56893001 |
| X2 | Terminal block | Phoenix | Duo | 9583-55837001 |
| X3 | Terminal | Phoenix | WSK | 9583-56967001 |

### 8.2 Duo Optimum 12, drawing 57156 sheet 5 (rev 1, 2006-08-21) [ELEC p.107]

Same as 8.1 except: E1 **9588-56464001**, E3 **9588-56562001**, M1 and M4 **Wilo 9675-57045002** (speed-controlled, alarm contact), no X3 WSK terminal; B4 sheet ref /4.6B.

---

## 9. Temperature sensors

### 9.1 Resistance tables [INST p.14] (`images/INST_p014_outdoor-sensor_NTC-tables.png`)

Measure with sensor cables disconnected from the control equipment: first sensor + cable, then sensor alone.

**Outdoor sensor (Ω)**

| °C | −30 | −25 | −20 | −15 | −10 | −5 | 0 | 5 | 10 | 15 | 20 | 25 | 30 | 35 | 40 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Ω | 1884 | 1443 | 1115 | 868 | 681 | 538 | 428 | 343 | 276 | 224 | 183 | 150 | 124 | 103 | 86 |

**Supply / return / hot water / brine ("coolant out") sensors (kΩ)**

| °C | 0 | 5 | 10 | 15 | 20 | 25 | 30 | 35 | 40 | 45 | 50 | 55 | 60 | 65 | 70 | 75 | 80 | 85 | 90 | 95 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| kΩ | 66.3 | 52.4 | 41.8 | 33.5 | 27.1 | 22.0 | 18.0 | 14.8 | 12.2 | 10.1 | 8.5 | 7.1 | 6.0 | 5.0 | 4.2 | 3.7 | 3.1 | 2.7 | 2.3 | 2.0 |

### 9.2 Curve fits for firmware (my calculation from the tables)

Steinhart–Hart, 1/T = A + B·ln(R) + C·ln(R)³, T in K, R in Ω:

| Sensor | A | B | C | Max error vs table |
|---|---|---|---|---|
| Outdoor | 1.964301e-03 | 2.712476e-04 | 2.395526e-07 | 0.04 °C |
| Supply/return/HW/brine | 8.741949e-04 | 2.347277e-04 | 1.325708e-07 | 0.55 °C (table rounding at high T) |

Beta approximations: outdoor ≈ **150 Ω @ 25 °C, B ≈ 3416** (0–25 °C); others ≈ **22 kΩ @ 25 °C, B ≈ 3665** (25–50 °C).

Use these only for **your own** sensors of the same type. Do not read the pump's own sensors in parallel with the controller – an extra load/bias changes what E1 measures.

### 9.3 Placement and handling

- Outdoor sensor: on buildings up to 3 storeys, 2/3 up the wall; higher buildings, between 2nd and 3rd floor; not sheltered from wind and not in direct wind; not on reflective metal; ≥1 m from openings that leak warm air; seal any conduit. [INST p.14]
- Supply line sensor placement: **after** the internal heater; if an external heater exists, after that heater's shunt. Terminals 301-302. [INST p.20–22]
- Calibration offsets −5…+5 °C per sensor in SERVICE → INSTALLATION → CALIBRATION SENSOR (OUTDOOR, SUPPLYLINE, RETURNLINE, WARMWATER, BRINE OUT, BRINE IN). [INST p.41, p.53]

### 9.4 Sensor fault behaviour [INST p.34, p.50]

| Sensor | Behaviour on fault |
|---|---|
| Outdoor | 0 °C used (shown flashing) |
| Supply | Control switched to OFF; only heating circulation pump runs |
| Return | Return = supply − 5 °C (−15 °C two minutes after hot-water production starts); max. estimated supply 45 °C |
| Hot water | No hot-water production |
| Room | Actual room temp not shown; 20 °C used for calculation |

---

## 10. Pressure switches and safety chain

| Device | Setting | Function | Effect |
|---|---|---|---|
| B1 operating pressure switch ("control pressostat") | 26.5 bar (alt. 28.5 bar) | Ends hot-water charging; required closed (=1) for compressor and aux starts | Input 218 [ELEC p.40, p.42], [INST p.29–30] |
| B2 high-pressure switch | 31 bar | Trip → **HIGHPRESS ERROR** | 319–320 |
| B3 low-pressure switch | 0.8 bar | Trip → **LOWPRESS ERROR** | 321–322 |
| F11 overload (+ WSK on std.) | 9–13 A | Trip → **MOTOR P ERROR** | 309–310 |
| T1 heater guard | 30 A | Trip → **ADD.HEATER** alarm | heater phases |
| Flow guard FL (option) | – | Not active at start attempt → **BRINEFLOW** | 217/219 |
| Phase sequence | – | **ERR. PHASE SEQ.** (display only, first 10 min) | – |

Hot water from the compressor stops at the B1 pressure, equivalent to **≈50–55 °C** tank water; not adjustable. [USER p.9]

---

## 11. Auxiliary heating and heating-system types

### 11.1 Steps [USER p.8], [INST p.39]

MAX STEP: 0 = no aux heater, **1 = 3 kW, 2 = 6 kW (factory), 3 = 9 kW**. Runtime counters: ADD.HEATER = 3 kW step, ADD.HEATER 2 = 6 kW step. [INST p.37]

### 11.2 System VL (factory default) [INST p.20–22]

- Internal heater connected; output limited to 3 / 6 / 9 kW (400 V).
- **VL + external heater without shunt, >9 kW:** control of the external heater on **N + 210**; SYSTEM = VL; **move the supply sensor after the external heater**.
- MAX STEP set to the "lightning" value.

### 11.3 System D [INST p.20–23] (`images/INST_p023_system-D_external-heaters.png`)

- **D with other external heaters (electric boiler or oil boiler with shunt):** shunt valve on **N, 215 (+), 216 (−)**; external heater control on **210**; supply sensor moved after the shunt; MAX STEP = **1H** (switch-off delay 1 h).
- **D with external electric heater only:** disconnect the internal heater by unplugging its supply connectors and insulating them; control of external heater on **210**; MAX STEP = "lightning".
- **Top heating (legionella) in D:** separate electric heater in the final tank on **209** via contactor K + thermostat + thermal cut-out; a separate thermostat sets the stop temperature; interval in WARMWATER menu; duration TOPH. TIME D (1–10 h).
- Fig. on p.23 shows external terminals labelled "901 — 510" on the HP block next to 209/210/215/216 (meaning not explained).

### 11.4 Aux heater for hot water [INST p.30]

Normally not used for hot water, except (VL): heater already on when HW starts; during top heating (heater switched on 2 min after top-heating start); in mode ADD.HEATER only. VL heater stops at TOPH. STOP, or in ADD.HEATER mode at WW STOP.

---

## 12. EVU and room-reduction input (307–308) [INST p.24]

Image: `images/INST_p024_EVU-and-room-reduction.png`.

| 307–308 state | Function | Display |
|---|---|---|
| Open | Normal | – |
| **Short (closed contact)** | **EVU block** – heat pump, aux heater **and circulation pump** stopped while closed | **"EVU STOP"** |
| **10 kΩ resistor** | **ROOM REDUCTION** – set room temperature lowered by REDUCTION (factory 3 °C, 1–10 °C) | clock symbol |

The input is SELV. **[inference]** An ESP32 can drive this with a relay/photoMOS (dry contact) for EVU, and a second contact in series with a 10 kΩ resistor for night setback. Never put a voltage on these terminals.

---

## 13. Room sensor (303–304)

- Optional Thermia room unit (086U6003 per REPO-R), SELV. Shows set value (e.g. 20.0); +/− adjust; both buttons = outdoor temp for 10 s; "A" on alarm. [USER p.9], [INST p.19]
- ROOM FACTOR (0–4) only shown when a room unit is connected; recommendation UFH 1–3, radiators 2–4. [INST p.46]
- **[community]** The port is **not** a resistive input: it idles at **~27 V DC** with ~1.7 kΩ in series and carries a pulse-coded digital protocol. Details and an emulator in [§22](#22-room-sensor-port-protocol-303304-community-repo-r).

---

## 14. Flow guard (217–219)

Optional brine flow monitor, NC contact between 217 (L) and 219 (input). Enable with SYSTEM = VL+F / D+F. If not active at a start attempt → alarm **BRINEFLOW**, compressor off, no hot water. Display shows "F" next to the HP symbol when installed. [INST p.32–34, p.41], [ELEC p.40–41]

---

## 15. Control logic

### 15.1 Heat curve [INST p.36, p.44–46], [USER p.13–22]

- **CURVE** = supply temperature at 0 °C outdoor (factory 40 °C, floor setting 30 °C; range 22–56 °C). Higher value = steeper curve.
- **ROOM** shifts the whole curve **3 °C supply per 1 °C ROOM** (parallel shift). Factory 20 °C (10–30). Temporary changes → ROOM; long-term → CURVE.
- **CURVE 5 / CURVE 0 / CURVE −5:** local ±5 °C bumps at +5, 0, −5 °C outdoor; the −5 bump acts progressively between 0 and −10 °C.
- **MIN / MAX** supply limits. UFH with parquet: max supply 45 °C. UFH with stone floor: MIN 22–25 °C even in summer (raise HEATSTOP too).
- **HEATSTOP**: heating off when outdoor ≥ setting (factory 17 °C). Circulation pump then off except during hot water; anti-seize run **1 min/day**. [USER p.23]
- **Integral** ("degree-minutes"): (actual supply − calculated supply) × time. Shown in TEMPERATURE menu (example values −40, −660). [USER p.31]

### 15.2 Compressor start / stop [INST p.29]

Start when **all**: integral < "Integral HP" (A1) · ≥5 min since last stop · STARTINTERVAL elapsed since last start · control pressostat closed (=1) · outdoor < heat stop.

Stop when **any**: integral > 0 °C·min · return ≥ MAX RETURN · outdoor > heat stop.

Brine pump starts 30 s before the compressor ("START" message). [USER p.11] BRINETIME ON/OFF default 30 s. [INST p.53]

### 15.3 Aux heater start / stop [INST p.29]

Start when all: integral < Integral HP + Integral TS (A1 + A2) · supply >3 °C below set · control pressostat closed.
Stop when any: integral > Integral HP · supply >3 °C above set.

### 15.4 Hot water [INST p.30, p.33, p.46–47]

- Start (compressor): HW temp ≤ START (factory 44 °C), or up to 2 °C above START when heating is off ("top-up").
- Stop: control pressostat open >5 s (40 s during the first 2 min); or alternation with heating per TIME HEAT / TIME WARMWATER (20/20 min); or after max. **45 min** (then 5 min heating-demand check).
- Legionella "top heating" to 65 °C every TOPH. INTERVAL days (factory 14). [USER p.9]
- Tank symbol: empty = start temp; full = temp at last fill (51 °C at start, max 54, min 49).

### 15.5 Operating modes [INST p.35, p.43]

OFF (alarms reset; drain heating in winter if left off) · AUTO · HEATPUMP (compressor only) · ADD.HEATER (heater only, for commissioning) · WARMWATER (hot water only, heater for top heating) · MANUAL TEST.

---

## 16. Menus, display and parameters

### 16.1 Navigation [USER p.11–13], [INST p.31–32]

- Normal display: ROOM, demand text, OPERATION. Right/left → INFORMATION (OPERATION, HEAT CURVE, [HEAT CURVE 2], TEMPERATURE, OPERATING TIME). Up/down select; right opens; left back. Returns to normal after 10 s.
- **SERVICE menu: hold right + left for 5 s.** [INST p.38]
- History: last 60 min (LOGGTIME 1 min), shown as graph; not logged for 1 week during an alarm. [INST p.37]

### 16.2 Display messages (normal view) [INST p.32–33]

| Message | Meaning |
|---|---|
| ROOM | Desired temperature (set and actual with room unit) |
| ERR. PHASE SEQ. | Wrong phase sequence (first 10 min only) |
| HIGH RETURN | Return too high for HP |
| HEATPUMP | Demand for HP |
| START | Demand for HP, no delay (30 s brine pre-run) |
| START_MIN | Start delay (minutes) |
| ADD.HEATER | Demand for aux heater |
| EVU STOP | EVU input closed, all off |
| COOLING / COOLING A | Passive / active cooling running |

Symbols: HP (F = flow monitor installed, 0 = operating pressostat activated) · lightning + step count · house · cooling (A = active) · tap (HW on) · SYSTEM (VL / D / VL+F / D+F) · clock (reduction) · tank (+ lightning = top heating).

### 16.3 Alarms [INST p.34, p.48–50], [USER p.29–30]

Alarms 1–5 reset with OPERATION = OFF or power cycle.

| Alarm | Meaning / effect | Typical causes |
|---|---|---|
| HIGHPRESS ERROR | Compressor off, no HW | Heating thermostats closed, air in heating, clogged filter in HP return, over-charged refrigerant, heating pump stopped/slow |
| LOWPRESS ERROR | Compressor off, no HW | Low antifreeze/air in brine, clogged brine filter, brine pump stopped/slow (ΔT in/out should be 3–5 °C), ice in brine, refrigerant leak, clogged drying filter (ΔT max 2 °C) |
| MOTOR P ERROR | F11 tripped; compressor off | Lost phase/fuse, loose connections, low mains voltage |
| BRINE OUT | Brine out below ALARM BRINE; compressor off (auto-resets when brine warms) | Normally inactive |
| BRINEFLOW | Flow monitor not active at last start | Low brine flow |
| ADD.HEATER | T1 tripped, no aux heat | – |
| SENSOR OUTDOOR / SUPPLY / RETURN / WARMWATER / ROOM | See [§9.4](#94-sensor-fault-behaviour-inst-p34-p50) | Wiring/sensor |
| CIRC. PUMP* / BRINE PUMP* | Optimum only: pump's integrated alarm; reset by holding the red button on the pump ≥1 s | – |
| ERR PHASE SEQ. | Compressor reverse; heat by aux only | Swap two phases |
| HIGH RETURN | Return too high | Open all thermostat valves |

### 16.4 INFORMATION → HEAT CURVE / HEAT CURVE 2 [INST p.36]

CURVE · MIN · MAX · CURVE5 · CURVE0 · CURVE-5 · HEATSTOP · REDUCTION · ROOM FACTOR (with room unit). HEAT CURVE 2 (sub-shunt sensor/expansion card): CURVE2 · MIN · MAX.

### 16.5 INFORMATION → TEMPERATURE [INST p.37]

OUTDOOR · ROOM · SUPPLYLINE act(set) · RETURNLINE act(max) · WARMWATER act(start) · INTEGRAL · BRINE OUT · BRINE IN · COOLING act(set) (exp. card) · SUBSHUNT act(set) (exp. card) · CURRENT act(set by main fuse) (exp. card).

### 16.6 INFORMATION → OPERATING TIME [INST p.37]

HEATPUMP · ADD.HEATER (3 kW) · ADD.HEATER 2 (6 kW) · WARMWATER · COOLING (total, if cooling sensor) · COOLING A (if NODE > 19).

### 16.7 SERVICE menus [INST p.38–41]

- **WARMWATER:** START (OFF = no sensor alarm), TIME WARMWATER, TIME HEAT, TOPH. INTERVAL (1 = constant), TOPH. STOP (VL).
- **HEATPUMP:** INTEGRAL A1, HYSTERESIS (forced start), MAX RETURN, STARTINTERVAL, ALARM BRINE, SHUNT COOLING (exp. card; condensation protection), LIQUID LINE (test sensor).
- **ADD.HEATER:** INTEGRAL A2, HYSTERESIS, MAX STEP, MAX CURRENT (needs current-measuring board), SHUNTTIME (all sub-shunts), WW STOP (VL).
- **MANUAL TEST:** 0 = show outputs, 1 = manual, 2 = manual with temperatures. Outputs: HEATPUMP (also starts brine pump; blocked during alarm), BRINEPUMP, CIRC.PUMP, VXV WARMWATER, ADD.HEATER 3, ADD.HEATER 6, ADD.HEATER (oil, D), SHUNT 1 (D), TOPH. WARMWATER (D), ALARM, SHUNT COOLING, SUBSHUNT, COOLING P, COOLING A, 0–10 V (last six = expansion card).
- **INSTALLATION 1A** (control card v1, display vA): language, SERVICETIME (1 = integral and delays ×60 faster), FACTORY SET (R = radiator, G = floor), RESET OPERATE TIME, CALIBRATION SENSOR, SYSTEM (VL / D, + F), LOGGTIME, NODE (shown if interface connected), BRINETIME ON/OFF, TOPH.TIME (3 h top heating ON, VL), TOPH.TIME D.

### 16.8 Factory settings (complete) [INST p.51–53]

| Parameter | Factory | Min | Max |
|---|---|---|---|
| ROOM | 20 °C | 10 | 30 |
| OPERATION | AUTO (OFF when delivered) | | |
| CURVE | 40 °C (floor = 30) | 22 | 56 |
| MIN | 10 °C | 10 | 50 |
| MAX | 55 °C (floor = 45) | 40 | 70 |
| CURVE 5 / 0 / −5 | 0 °C | −5 | 5 |
| HEATSTOP | 17 °C | 0 | 40, OFF |
| REDUCTION | 3 °C | 1 | 10 |
| ROOM FACTOR | 2 | 0 | 4 |
| CURVE2 (exp. card) | 40 °C | 22 | 56 |
| MIN2 | 10 °C | 10 | 40 |
| MAX2 | 55 °C | 30 | 70 |
| WW START | 44 °C | OFF, 30 (card) | 46 (card) |
| TIME WARMWATER | 20 min | 5 | 40 |
| TIME HEAT | 20 min | 5 | 40 |
| TOPH. INTERVAL | 14 d | OFF, 1 | 90 |
| TOPH. STOP | 65 °C | 50 | 65 |
| INTEGRAL A1 | 60 | 5 | 99 |
| HYSTERESIS (HP) | 7 °C | 1 | 15 |
| MAX RETURN | 48 °C | 30 | 55 |
| STARTINTERVAL | 20 min | 1 | 30 |
| ALARM BRINE | OFF | OFF, −14 | 10 |
| SHUNT COOLING | 16 °C | 0 | 30 |
| INTEGRAL A2 | 600 | 50 | 990 |
| HYSTERESIS (AH) | 15 °C | 5 | 30 |
| MAX STEP | 2 | OFF, 1 | 3 |
| MAX CURRENT | 20 A | 16 | 35 |
| SHUNTTIME | 60 s | 30 | 99 |
| WARMWATER STOP | 65 °C | 50 | 65 |
| CALIBRATION (each sensor) | 0 °C | −5 | 5 |
| SYSTEM | VL | | |
| LOGGTIME | 1 min | 1 | 60 |
| NODE | 1 | 0 | 30 |
| BRINETIME ON | 30 s | 10 | 600 |
| BRINETIME OFF | 30 s | 10 | 600 |
| TOPH. TIME | OFF | OFF | ON |
| TOPH. TIME D | 1 h | 1 | 10 |

**MAX RETURN rule** [INST p.46]: with the system in steady heating, max return = 55 − (supply set − return set). Example: 36 − 30 = 6 → 55 − 6 = 49 °C.

### 16.9 Optimum-only menu [INST p.42]

CIRC. DIFF (desired ΔT heating) · BRINE DIFF (desired ΔT brine) · FLOW RAD AUTO / 3–10 (manual speed) · FLOW BRINE AUTO / 3–10 · MAX HW / MIN HW (supply limits during hot water). No factory values given.

---

## 17. Diplomat expansion card (901 515)

Images: `images/EXPCARD-EN_p007_wiring-901515.png`, `images/EXPCARD-086U6715_p005_EN-wiring.png`.

### 17.1 Functions [EXP1 p.3], [EXP2 p.4]

1. **Overload / power guard:** 3 current transformers on the phases of the protected fuse group; aux heater steps down when current > MAX CURRENT; margin 5 A; step-up delayed 1 min when within margin; limit lowered 5 A temporarily while the HP starts.
2. **Cooling:** passive (borehole) or passive + active (compressor), with the cooling module ([§18](#18-cooling-module-086u7815)).
3. **Sub shunt / shunt group:** second temperature level with CURVE 2 (e.g. radiators + UFH). Constant temperature: MIN = MAX.
4. **Pool:** separate sensor; flow must always pass over the pool sensor. Not with shunt group or active cooling.
5. **Sum alarm:** output on every alarm (EXP1: 230 V output signal, max 5 A; EXP2: potential-free NC/C/NO, max 230 V / 5 A).
6. **0–10 V output:** for future compressor frequency control; not used.

Mounting: card in the slot in the electrical compartment, connected with the supplied cable between **Ext.COM** on the control unit and Ext.COM on the card (the card has two Ext.COM sockets). [EXP1 p.4], [EXP2 p.4]

### 17.2 Terminals [EXP1 p.7 drawing 54201], [EXP2 p.5]

| Terminal | Function | Level |
|---|---|---|
| 251 / 252 | Card supply 230 V – **from HP N1 and 217** | 230 VAC |
| 253–256 | Passive cooling relay block (253 = switched output, 254 N, 255 L, 256 N) | 230 VAC |
| 257 (L) / 258 (N) | Cooling circulation pump | 230 VAC |
| 259 (L) / 260 (N) | Permanent L / N for cooling module | 230 VAC |
| 261 / 262 (N) / 263 (L) / 264 (N) | Reversing valve active cooling / pool (261 = switched → valve pin 6, 262 → pin 2, 263 → pin 3) | 230 VAC |
| 351, 352, 353 / 354 | Current transformers T1, T2, T3 / common | – |
| 355 (−) / 356 (com) / 357 (+) / 358 (com) | Shunt cooling motor | 24 VAC |
| 359 / 360 | Sensor shunt cooling (white/red) | – |
| 361 (−) / 362 (com) / 363 (+) / 364 (com) | Shunt group 2 motor | 24 VAC |
| 365 / 366 | Sensor shunt group 2 / pool (white/red) | – |
| 369 / 370 | 0–10 V output | – |
| NC / C / NO | Alarm relay | ≤230 V 5 A |

**Discrepancy:** EXP1 (drawing 54201) labels **251 = N, 252 = L**, and the cooling-module drawing [COOL p.28–29] wires 251 (blue) → N1 and 252 (black) → 217, which agrees. EXP2 [p.5] labels 251 = L, 252 = N. Check the card itself before wiring.

### 17.3 Configuration on the Duo (older controller, NODE-based) [EXP1 p.5–6]

| NODE | Mode |
|---|---|
| 2–18 | Passive cooling **with** room sensor: start room +2 °C over set, stop +0.9 °C |
| 19 | Passive cooling **without** room sensor: always when outdoor > HEATSTOP |
| 20 | Active/passive **without** room sensor: passive when outdoor > HEATSTOP; active when BRINE IN > COOLING setpoint for 2 min |
| 21–30 | Active/passive **with** room sensor: passive start +2 / stop +0.9 °C; active start +4 / stop +1.9 °C |
| 11 | Pool function (pool temp and "pool hysteresis" in HEAT CURVE menu; <5 °C = off). Note: 11 also falls inside the 2–18 passive-cooling range – EXP1 does not explain the overlap |

Cooling setpoint: SERVICE → HEATPUMP → SHUNT COOLING (factory 16 °C, anti-condensation).

### 17.4 Newer controller menus (EXP2, for reference) [EXP2 p.4–5]

SERVICE → AUX.HEATER → MAX CURRENT; SERVICE → INSTALLATION → SYSTEM → COOLING → PASSIVE COOLING (EXTERNAL / INTEGRATED IN HP – Comfort only), ACT COOLING (EXTERNAL), ROOM SENSOR (OFF/ON; with room sensor start +2 / stop +1, active +4 / +2); SYSTEM → SHUNT GROUP = ON; SYSTEM → POOL = ON. Heating and cooling never at the same time: cooling only in HEAT STOP. Pool/HW/house alternate every 20 min (HW–Pool–HW–House–…). These menu paths may not exist on the Duo's older display; on the Duo use NODE ([§17.3](#173-configuration-on-the-duo-older-controller-node-based-exp1-p56)).

---

## 18. Cooling module 086U7815

Images: `images/COOLMOD_p0*.png`.

### 18.1 General [COOL p.5]

- Two versions: **P** (passive) and **P/A** (passive/active). P/A for cooling demand up to **20 kW**. Wall-hung, vertical; mounting hole spacing **530 mm**. Housing ≈ 599 × 475 mm, height 722 mm + 60 mm pipe stubs top and bottom [COOL p.14, p.16].
- Distribution: radiators/fan convectors or UFH. Cooling starts when outdoor > HEATSTOP.
- **Stage 1 passive:** outdoor > heat stop; room above set by ≥ ROOM FACTOR °C; both within 5 min → HP brine pump circulates brine through the module to the borehole; module shunt mixes to the set cooling temperature.
- **Stage 2 active (P/A only):** passive conditions + room above set by 2 × room factor for 1 min; or brine-in > cooling set during passive → active forced after **120 s**. Compressor starts; excess heat goes first to hot water, then to the borehole.

### 18.2 Pipe connections, all Ø 28 [COOL p.14–17]

P: A brine out · B brine in · H cooling supply · J cooling return.
P/A: A brine out 1 · B brine in 1 · C brine out 2 · D brine in 2 · E heating supply (to radiators/fan heat) · F heating supply from HP · G heating return · H cooling supply · J cooling return.
External available pressure H–J (P/A curve, read from graph): ≈51 kPa @ 0.2 l/s, 45 @ 0.3, 41 @ 0.4, ≈30 @ 0.6, ≈18 @ 0.8 l/s [COOL p.19]. Passive curve on p.18.

### 18.3 Wiring [COOL p.28–29] **[schematic]**

HP expansion card (E2) → module terminal strip (1–9 at 230 V, 10–14 at <24 V):

| Card | Wire | Module | Function |
|---|---|---|---|
| 251 | bl | HP N1 | card supply N |
| 252 | bk | HP 217 | card supply L |
| 257 | gy-257 | 8 | passive cooling command (pump M1 + valve V2 pin 6 on P) |
| 259 | gy-259 | 7 | permanent L (valve pins 3) |
| 260 | bl-260 | 5 | N |
| 261 | gy-261 | 6 | active cooling command (P/A: V2 + V3 pin 6, excess-heat pump M2) |
| PE | – | 9 | PE |
| 355 (−) | rd-355 | 13 | shunt V1 pin 3 |
| 356 (com) | wh-356 | 12 | shunt V1 pin 2 (blue) |
| 357 (+) | rd-357 | 14 | shunt V1 pin 6 |
| 359 | rd-359 | 10 | cooling sensor B1 |
| 360 | wh-360 | 11 | cooling sensor B1 |

Inside P/A: V2 reversing valve passive/active (2 → 4, 3 → 7, 6 → 6), V3 reversing valve active cooling (2 → 3, 3 → 7, 6 → 6), M1 circulation pump (1 → 8, 2 → 5), M2 excess-heat pump (1 → 6, 2 → 5), V1 shunt 24 V (pin 2 → 12, pin 3 → 13, pin 6 → 14), B1 sensor (10/11). Valve neutrals land on 3/4 while HP neutral lands on 5 – the link 3/4/5 is not drawn; check on site.

---

## 19. Fan coils (Zantia catalogue) [FAN]

Generic catalogue, not Thermia. Relevant for cooling/heating emitters with the cooling module.

### 19.1 Families [FAN p.2]

| Type | Pipes | Heating kW | Cooling kW | Air m³/h | Noise dB(A) | Water cooling / heating |
|---|---|---|---|---|---|---|
| Centrifugal | 2 / 4 | 1.4–10.1 / 1.3–6.1 | 1.1–7.5 / 1.1–6.3 | 190–1400 | 31–54 / 31–57 | 7/12 °C / +50 (2T), +70/+60 (4T) |
| Tangential | 2 / 4 | 1.46–6.9 / 1.2–4.4 | 1.04–5.3 / 1.04–4.2 | 190–1000 | 25–47 / 25–45 | 7/12 / +50, +70/+60 |
| Vertical | 2 | 1.6–8.8 | 0.89–6.51 | 185–1360 | 33–40 | 7/12 / 70/60 |
| Wall (mural) | 2 | 1.93–5.82 | 1.45–4.45 | 327–1020 | 23–38 | 7/12 / 70/60 |
| Cassette 4-way | 2 / 4 | 2.67–13.20 / 2.27–7.75 | 1.84–12.89 / 2.50–10.58 | 300–2550 / 300–1330 | 39–49 / 28–47 | 7/12 / 70/60; 4T 5/27?, 50/20 (as printed) |

Model code (centrifugal/tangential): `C V 1.3 2T` = fan type (C centrifugal, T tangential) · position (V vertical, H horizontal – needs kit 2199.0403 –, N built-in) · model 1–7 (6–7 centrifugal only) · coil rows 3/4 · pipes 2T/4T. 2 pipes = heating in winter / cooling in summer; 4 pipes = simultaneous. [FAN p.2]

### 19.2 Centrifugal – electrical and performance [FAN p.4–7]

- 230 V ~ 50 Hz single-phase motor, 4 speeds of which 3 connected, sealed bearings, IP21. Coil copper/aluminium, connections 1/2" (+1/8" vent/drain), both on the left (seen from front). Condensate tray outlet Ø 15 mm. Filter washable, 73 %.
- Motor power / current by size: 1 = 53 W / 0.23 A · 2 = 64 W / 0.28 A · 3 = 79 W / 0.36 A · 4 = 98 W / 0.44 A · 5 = 170 W / 0.74 A · 6 = 190 W / 0.84 A · 7 = 310 W / 1.4 A.
- Test conditions: cooling air 27 °C DB / 19 °C WB, water 7/12 °C; heating air 20 °C, water in +50 °C (2T).

2-pipe performance (speeds 1/2/3):

| Model | Air m³/h | Cooling kW | Heating kW | Fan W |
|---|---|---|---|---|
| 1.3 2T | 190/240/300 | 1.1/1.3/1.5 | 1.4/1.7/2.1 | 20/30/40 |
| 1.4 2T | 190/240/300 | 1.3/1.5/1.8 | 1.6/2.0/2.3 | 20/30/50 |
| 2.3 2T | 290/360/450 | 1.8/2.2/2.5 | 2.3/2.7/3.3 | 45/50/60 |
| 2.4 2T | 290/360/450 | 2.0/2.4/2.8 | 2.5/3.0/3.5 | 45/50/60 |
| 3.3 2T | 380/480/600 | 2.5/2.9/3.5 | 3.0/3.7/4.5 | 60/80/95 |
| 3.4 2T | 380/480/600 | 2.7/3.3/3.9 | 3.2/4.0/4.8 | 60/80/95 |
| 4.3 2T | 480/600/750 | 2.9/3.4/4.0 | 3.7/4.4/5.2 | 65/80/95 |
| 4.4 2T | 480/600/750 | 3.2/3.9/4.6 | 4.0/4.8/5.8 | 65/80/95 |
| 5.3 2T | 650/800/1000 | 3.6/4.2/4.8 | 4.7/5.5/6.5 | 65/85/125 |
| 5.4 2T | 650/800/1000 | 4.2/4.8/5.7 | 5.2/6.2/7.4 | 65/85/125 |
| 6.3 2T | 750/950/1200 | 4.3/5.1/6.0 | 5.5/6.7/8.0 | 120/145/180 |
| 6.4 2T | 750/950/1200 | 4.6/5.5/6.6 | 6.0/7.3/8.8 | 120/145/180 |
| 7.3 2T | 850/1100/1400 | 4.8/5.7/6.7 | 6.2/7.5/9.1 | 135/170/190 |
| 7.4 2T | 850/1100/1400 | 5.2/6.3/7.5 | 6.7/8.3/10.1 | 135/170/190 |

Water flow limits, 3-row coil (l/h): models 1–7 min 100/150/150/200/250/300/400, max 500/750/1000/1000/1500/2000/2000. Weights 14–42 kg. [FAN p.7]

### 19.3 Controls and valves [FAN p.3, p.15–20, p.31]

| Controller | For | ON/OFF | Speed | Summer/winter | Thermostat | Low-temp cut | 3-way valve |
|---|---|---|---|---|---|---|---|
| MV-3V (2199.0101) | CV (built-in) | yes | 3 manual | no | no | TMM | no |
| TMV-T (2199.0102) | CV | yes | 3 | yes | yes | TME | yes |
| MO-3V (2199.0103) | CH/NC (wall) | yes | 3 | no | no | TMM | no |
| TMO-T (2199.0104) | CH/NC | yes | 3 | yes | yes | TME | yes |
| TMO-DI (2199.0109) | CV/CH/NC | yes | manual/auto | manual/central | fan + valve thermostats | TME | yes |
| TMO 503-SV2 (2199.0110) | CV/CH/NC | yes | manual/auto | manual | valve thermostat | TME | yes |

- TMV-T in summer with fan selector OFF runs the fan 2 min every 15 min.
- Repeater (2199.0106 CV / 2199.0107 CH/NC): up to 8 fan coils from one TMO-T thermostat.
- **TMM** (2199.0202): stops fan below 32 °C primary water, restarts above 42 °C (MV-3V/MO-3V). **TME** (2199.0201): stops below 38 °C, restarts above 42 °C (TMV-T/TMO-T). Change-over 15-25 (2199.0204): automatic summer/winter on water inlet (2-pipe, TMO-T/TMO-DI).
- Valves: VBP 1-3 (1/2", DN15, 2199.0401), VBP 4-7 (3/4", DN20, 2199.0402) for 2-pipe; VBA 1-7 (2199.0404) for 4-pipe; only with TMV-T/TMO-T.
- Zone valve 3-way 22C series (1605.0211, 3/4", 16 bar, 4–110 °C) + **electrothermal head 230 V NC (1906.0306)**: wax actuator, 140 N, open/close 90/180 s, 2.5 W, auxiliary contact 700 W.
- Vertical Zantia (2101.0301–0308): 230 V ~ 50 Hz, 3-speed centrifugal with thermal protection; digital thermostat 2199.0203: heat/cool/fan, 3 speeds, 17–32 °C, drives an optional 3-way valve, anti-cold-air (fan stops when coil <35 °C) and anti-hot-air (printed "coil >20 °C") functions. Condensate drain only needed for cooling. [FAN p.22–24]
- Wall units (2102.0401–0405): 3-way valve, IR remote, display included. Cassettes: grille, remote and condensate pump (0.75 m lift) included; optional CZFI 1 wired remote, CZFC 1 central (64 units), network modules, dry-contact module. [FAN p.25–32]

**[inference]** Integration: catalogue cooling ratings are at 7/12 °C water. With the Thermia cooling module the supply is shunted to SHUNT COOLING (factory 16 °C, to prevent condensation), so real capacity is far lower. Fans, valves and change-over can be switched by ESP32 relays (230 V, use rated relays/contactors), using cooling-active state from the pump (r11 bits, [§21.5](#215-register-map)) as an interlock.

---

## 20. Integration overview for the ESP32

| Path | Terminals / connector | Direction | What it gives | Risk |
|---|---|---|---|---|
| **A. EXT bus (I2C slave 0x2E)** | EXT header on E1 (GND, SDA, SCL, 5 V) | read + write | All temperatures, states, alarms, counters; write setpoints, mode, curve, HW, MAX STEP, … | low with level shifter; writes unacknowledged |
| **B. Room sensor emulation** | 303 / 304 | ESP → pump | Real room temperature + room setpoint (0.5 °C) | needs photoMOS; never connect directly |
| **C. EVU / reduction** | 307 / 308 | ESP → pump | Block (EVU STOP) or night setback (10 kΩ) | dry contact only |
| **D. Current measurement** | CTs on phases | ESP | Power/energy (also expansion card r0C) | mains-side install by electrician |
| **E. State detection of 230 V outputs** | 211, 212, 213, 214, 209, 210, 215, 216 | ESP reads | Redundant with r10/r11 bits | isolated 230 V detectors only |
| **F. Own sensors** | separate NTC/DS18B20 | ESP | Extra temps (tank, UFH loops) | – |

Avoid: driving the pump's relays or outputs directly, bypassing B1/B2/B3/F11/T1, connecting to sensor lines in parallel, or switching the compressor/heater from outside the controller.

---

## 21. EXT port – I2C bus protocol [community, REPO-T]

### 21.1 Hardware

- 4-pin EXT header, left → right **GND, SDA, SCL, 5 V** (verify on your board). Next to the RJ45 display socket on the top edge of the Duo board. (`images/REPO_esphome-thermia_ext-port-pinout.jpg`)
- **5 V bus** with the pump's own pull-ups → use a bidirectional level shifter (BSS138 type). Connect only GND, SDA, SCL; power the ESP separately. Wire with the pump off.
- ESP32: GPIO0–31 only, avoid strapping pins (0, 2, 5, 12, 15) and flash pins; GPIO21/22 work well. REPO-T was tested on a **Thermia Duo 400 V 10 kW** with a Wemos D1 mini and an ESP32-S3 (the combined example in REPO-R uses SDA GPIO12 / SCL GPIO11).
- Do **not** declare an ESPHome `i2c:` block: the pump is the master.
- **[inference]** E1's "Ext. COM" (drawing) and the EXT header are very likely the same port used by the expansion card (the pump also polls addresses 0x32 and 0x37). If you fit an expansion card, the bus is shared.

### 21.2 Protocol

- Pump = I2C master, ~20 kHz; accessory = slave at 7-bit address **0x2E**.
- Pump writes a **ping** `0xFE` (`0xFD` after its own boot).
- Pump then **reads one byte** from the slave: `0xFF` = nothing; `0x00–0x7F` = "send me register N"; or a 3-byte `[reg | 0x80, lo, hi]` = **write** value to register.
- After a register request, the pump writes a data frame `[reg, lo, hi]` – **little-endian signed int16**.
- Example: `S 5C FE P` (ping) → `S 5D [06] P` (ask r06) → `S 5C 06 18 00 P` (r06 = 24 °C).
- No write acknowledgement: poll the register after writing. Some registers (r00, r01, r32, r34) answer only rarely (up to minutes); r10 is not answered while the compressor is idle.
- REPO-T's implementation: GPIO interrupt on SDA falling edge, IRAM busy-poll until STOP; 1.5 ms per-edge and 8 ms per-transaction timeouts; circuit breaker after 50 failed transactions; plausibility −60…200 °C; bus gate (attach after Wi-Fi up 5 s). ESP32 hardware I2C slave not used because the reply depends on the preceding ping.

### 21.3 esphome-thermia configuration

```yaml
external_components:
  - source: github://mdepa91/esphome-thermia
    components: [thermia]
thermia:
  sda_pin: GPIO21   # via level shifter
  scl_pin: GPIO22
  update_interval: 10s
  stale_timeout: 1h  # some registers answer rarely
  request_tries: 50  # default; r00 needs long waits
```

Options: `debug_frames`, `sniff` (raw waveforms, disables protocol), `selftest`, `link`, `card_map`, generic `registers:` (read 0x00–0x7F, scale, signed) and `set_registers:` (write; min/max required).

### 21.4 Diagnostics [REPO-T]

`pings=0, isr=0` → not connected · `isr` grows, `pings=0` → SDA/SCL swapped · `pings` grows, `data=0` → pump not sending registers · `err` grows with pings → ISR too slow · `unanswered` grows → normal for some registers · `foreign` grows → normal (0x32, 0x37).

### 21.5 Register map

Source: TIQ map, used by REPO-T. ✅ = confirmed on a real Duo by REPO-T; others are from the ThermIQ map. "Menu" column = my mapping to the Duo menu parameter **[inference]**, based on name, unit and range.

**Measurements (read-only)**

| Reg | Name (TIQ) | Unit | Meaning | Menu / hardware |
|---|---|---|---|---|
| r00 | outdoor_t | °C | Outdoor | TEMPERATURE→OUTDOOR (305/306) |
| r01 / r02 | indoor_t / indoor_dec_t | °C / 0.1 | Indoor (virtual or room unit), integer + tenths | ROOM |
| r03 / r04 | indoor_target_t / dec | °C / 0.1 | Indoor target in use | – |
| r05 | supplyline_t | °C | Supply (T1) | B4 301/302 |
| r06 | returnline_t | °C | Return (T2) | B6 |
| r07 | boiler_t | °C | Hot-water tank (T3) | 311/312 |
| r08 | brine_out_t | °C | Brine out | B7 |
| r09 | brine_in_t | °C | Brine in | B8 |
| r0A | cooling_t | °C | Cooling | exp. card 359/360 |
| r0B | supply_shunt_t | °C | Sub-shunt supply | exp. card 365/366 |
| r0C | current_consumed_a | A | Measured current | exp. card CTs |
| r0D bit 0x01 / 0x02 | boiler_3kw_on / boiler_6kw_on | – | Aux 3 kW / 6 kW relay | E1 3KW / 6KW |
| r0E | supplyline_target_t | °C | Supply target | SUPPLYLINE (set) |
| r0F | supplyline_shunt_target_t | °C | Sub-shunt target | – |
| r10 bits | 0x01 brine pump · 0x02 compressor · 0x04 supply pump · 0x08 hot-water production · 0x10 aux2 · 0x20 shunt1 − · 0x40 shunt1 + · 0x80 aux1 | – | Output states | 211 · 212 · 213 · 214 · – · 216 · 215 · – |
| r11 bits | 0x01 shunt2 − · 0x02 shunt2 + · 0x04 shunt cooling − · 0x08 shunt cooling + · 0x10 active cooling · 0x20 passive cooling · 0x40 alarm | – | Exp. card outputs + sum alarm | 361/363 · 355/357 · 261 · 253/257 |
| r12 | pwm_out_period | % | PWM out | – |
| r13 bits | 0x01 high pressure · 0x02 low pressure · 0x04 motor breaker · 0x08 brine flow · 0x10 brine temperature | – | Alarms | B2 · B3 · F11 · FL · ALARM BRINE |
| r14 bits | 0x01 outdoor · 0x02 supply · 0x04 return · 0x08 hot-water · 0x10 indoor sensor · 0x20 phase order · 0x40 overheating | – | Alarms | sensors · ERR PHASE · T1 |
| r15 / r16 | demand1 / demand2 | – | Demand | – |
| r17 | pressurepipe_t | °C | Discharge (hot gas) | B9 323/324 |
| r18 | hgw_water_t | °C | Hot-water supply line | (HGW option) |
| r19 | integral1 | °C·min | Integral A1 | TEMPERATURE→INTEGRAL |
| r1A | integral1_a_step | – | Integral, reached A-limit | – |
| r1B | defrost_time_m | ×10 s | Defrost | (n/a for brine) |
| r1C | time_to_start_min_m | min | Min. time to start | START_MIN |
| r1D | sw_version | – | Program version | – |
| r1E / r1F | supply / brine pump speed | % | Pump speeds | Optimum 0–10 V |
| r20 | status3_m | – | Status | – |
| r68 / r6A / r6C / r6E / r70 / r72 | runtimes | h | Compressor / 3 kW / hot water / passive cooling / active cooling / 6 kW | OPERATING TIME |
| r69 / r6B / r6D / r6F / r71 / r73 | msd1_* | – | Alternative runtime counters (s) | – |
| r74 | graph_display_offset | – | – | – |

**Settings (read/write)**

| Reg | Name (TIQ) | TIQ range | Duo menu (factory, min–max) | REPO-T |
|---|---|---|---|---|
| r32 | indoor_requested_t | 0–50 °C | ROOM (20, 10–30) | ✅ |
| r33 | main_mode | 0–16 | OPERATION: 0 Off, 1 Auto, 2 Heatpump only, 3 Heater only, 4 Hot water only (5–16 undocumented) | ✅ |
| r34 | integral1_curve_slope | 0–200 | CURVE (40, 22–56) | range from menu |
| r35 / r36 | curve min / max | 0–200 °C | MIN (10, 10–50) / MAX (55, 40–70) | |
| r37 / r38 / r39 | curve +5 / 0 / −5 | −5…5 | CURVE 5 / 0 / −5 | |
| r3A | heating_stop_t | 0–200 | HEATSTOP (17, 0–40) | |
| r3B | reduction_t | 0–100 | REDUCTION (3, 1–10) | |
| r3C | room_factor | 0–4 | ROOM FACTOR (2) | |
| r3D / r3E / r3F | curve 2 slope / min / max | 0–200 | CURVE2 / MIN2 / MAX2 | |
| r40 / r41 | curve 2 target / actual | 0–200 | SUBSHUNT set / act | |
| r42 | outdoor_stop_t | 0–100 | "(20 = −20 °C)", inverted sign? – left out by REPO-T | |
| r43 | pressure_pipe_limit_t | 0–200 | discharge temp. limit (not in Duo manual) | |
| r44 | hotwater_start_t | 0–100 | WW START (44) | |
| r45 | hotwater_runtime_m | min | TIME WARMWATER (20, 5–40) | |
| r46 | heatpump_runtime_m | min | TIME HEAT (20, 5–40) | |
| r47 | legionella_interval_d | days | TOPH. INTERVAL (14) | |
| r48 | legionella_stop_t | 0–100 | TOPH. STOP (65) | |
| r49 | integral1_a_limit | °C·min | INTEGRAL A1 (60, 5–99) – scaling to verify | |
| r4A | integral1_hysteresis_t | 0–100 | HYSTERESIS HP (7) | |
| r4B | returnline_max_t | 0–100 | MAX RETURN (48) | |
| r4C | start_interval_min_m | min | STARTINTERVAL (20) | |
| r4D | brine_min_t | −25…100 (−15 = OFF) | ALARM BRINE (OFF, −14…10) | |
| r4E | cooling_target_t | 0–50 | SHUNT COOLING (16) | |
| r4F | integral2_a_limit | ×10 °C·min | INTEGRAL A2 (600) – register likely 60 | |
| r50 | integral2_hysteresis_t | 0–100 | HYSTERESIS AH (15) | |
| r51 | elect_boiler_steps_max | 0–3 | MAX STEP (2) | |
| r52 | current_consumption_max_a | A | MAX CURRENT (20) | |
| r53 | shunt_time_s | s | SHUNTTIME (60) | |
| r54 | hotwater_stop_t | 0–100 | WW STOP (65) | |
| r55 | manual_test_mode_on | – | MANUAL TEST | read |
| r56 / r58 | status7 (DT_LARMOFF) / status8 (SERVFAS) | – | – | read |
| r57 | language | 0–255 | language | |
| r59 / r5A | factory reset / reset runtime counters | – | FACTORY SET / RESET OPERATE TIME | not exposed (dangerous) |
| r5B…r60 | sensor offsets outdoor, supply, return, hot water, brine in, brine out | −5…5 | CALIBRATION SENSOR (TIQ labels r5F/r60 "brine out"/"brine in" – likely swapped) | |
| r61 | heatingsystem_type | 0 = VL, 4 = D | SYSTEM | |
| r62 bits | 0x01 phase-measure · 0x02 opt2 · 0x04 HGW · 0x08/0x10/0x20 opt4–6 · 0x40 Optimum · 0x80 flow guard | – | installed options | read |
| r63 | internal_logging_t | min | LOGGTIME (1) | |
| r64 / r65 | brine run-out / run-in | ×10 s | BRINETIME OFF / ON (30 s = 3) | |
| r66 | legionella_run_on | 0/1 | TOPH. TIME (OFF) | |
| r67 | legionella_run_length_h | h | TOPH. TIME D (1) | |

REPO-T exposes: r32, r33 (select), r34–r39, r3A, r3C, r44, r54, r51, r52; everything else via `registers:` / `set_registers:` with your own min/max. **Writing r01 (indoor temperature) is ignored by the pump.** Change one setting at a time, with the display at hand.

---

## 22. Room sensor port protocol (303–304) [community, REPO-R]

- Line idles at **~27 V DC**, ~1.7 kΩ in series on the pump side. A pulse = load across the line (1.1 kΩ 1 W pulls it to ~10 V).
- Reference circuit: ESP32 GPIO → 220 Ω → **Toshiba TLP241A photoMOS** (DIP-4, 40 V, isolated) → 1.1 kΩ 1 W across 303/304; optional P6KE33CA TVS. ESP stays on its own supply. (`images/REPO_esphome-thermia-room_wiring.svg`)
- **Pulse-distance coding:** each bit = idle gap + **60 ms** pulse; gap ≈ **82 ms → raw 1**, ≈ **388 ms → raw 0**. Logical bit = NOT raw bit; fields LSB first.
- **Frame (29 bits, 6–9 s):** start(1) | setpoint × 2 (8 bits, 0.5 °C) | integer °C (8) | tenths (4) | checksum (5) | tail `011` (3). Frames separated by **2–4 s** idle (the pump syncs on it).
- **Checksum** = (integer XOR tenths XOR setpoint×2) AND 31. Bad frames are silently dropped.
- Ranges: room 0.0–31.9 °C; setpoint frame 5–35 °C; the pump raises a room-sensor alarm below 16 °C.
- Pump behaviour: with valid frames and ROOM FACTOR 1–4, uses setpoint (r03/r04) and room temp (r01/r02). Without frames → room-sensor alarm (r14 bit 0x10) → falls back to r32. ROOM FACTOR 0 → room sensor ignored, r32 used, no alarm.
- Compatible family: Diplomat, Diplomat Optimum, Duo, Legend; Danfoss DHP-H/C/L. Needs an ESP32 (RMT peripheral).

Examples: room 20.5 / set 21.0 → raw `1|10101011|11010111|0101|00100|011`; room 22.4 / set 21.5 → `1|00101011|10010111|1101|01100|011`.

---

## 23. Recommended ESP32 hardware outline **[inference]**

1. **EXT bus:** BSS138 level shifter (5 V side from the pump's 5 V reference, 3.3 V side from the ESP), SDA/SCL on GPIO0–31, short shielded cable, common GND only.
2. **Room sensor:** TLP241A + 1.1 kΩ 1 W + TVS on 303/304, as in [§22](#22-room-sensor-port-protocol-303304-community-repo-r).
3. **EVU / reduction:** two small relays or photoMOS: contact 1 shorts 307-308 (EVU), contact 2 puts 10 kΩ across 307-308 (reduction). Interlock in firmware so both are never on together.
4. **Power monitoring:** 3 split-core CTs on the incoming phases or an external energy meter (Modbus); mains work by an electrician.
5. **Supply:** separate 5 V DIN-rail PSU for the ESP. Keep low-voltage wiring ≥25 cm from mains cables ([§4.1](#41-supply-requirements-inst-p15-elec-p2)).
6. **Fail-safe:** if the ESP dies, the pump must run normally → room emulation dropout makes the pump use r32 (keep r32 sensible); EVU contact must be normally open.

---

## 24. Open points to check on your unit

1. Standard (drawing 56960) or Optimum (57156)? Check pumps (0–10 V wiring at 327–334) and the type plate.
2. Soft starter R1 or contactor K1 (cubicle 53369-A / 55527-B)?
3. Straps at X1: 3L1–2L1 and 1Lx–2Lx present?
4. Expansion card fitted? If yes, Ext.COM/EXT is already used – plan a shared connection; check 251/252 labelling.
5. EXT header pin order (GND, SDA, SCL, 5 V) with a meter before connecting.
6. INTEGRAL A1/A2 register scaling (r49, r4F) – read them and compare with the display before writing.
7. Cooling-module terminals 3/4/5 neutral link.
8. Current MAX STEP, SYSTEM (VL/D) and NODE values on the display.

---

## 25. Glossary

| Term | Meaning |
|---|---|
| VL | System with internal electric heater (factory) |
| D | System with external heater/boiler (shunt) |
| F | Flow guard installed (VL+F, D+F) |
| EVU | Elektrizitäts-Versorgungs-Unternehmen – utility block input |
| VXV | Växelventil – diverting valve (hot water) |
| TRYCKRÖR | Swedish "pressure pipe" = compressor discharge sensor |
| TOPP TWS | Hot-water top sensor |
| WSK | Wicklungsschutzkontakt – pump winding thermal contact |
| HGW | Hot gas water (option) |
| A1 / A2 | Integral limits for compressor / aux heater |
| Top heating (TOPH) | Legionella heating of the tank |
| Sub-shunt / shunt group | Second mixing circuit with its own curve (CURVE 2) |
| NODE | Address/mode number; on the Duo also selects cooling mode and pool |
| HUONE | Finnish "room" – the pump's own room setpoint (r32) in community docs |
| Brine / coolant / chilled water | Same circuit (ground loop antifreeze), different translations |

---

## 26. Document conflicts and quirks

- Expansion card 251/252 N/L labelling differs between EXP1 and EXP2 ([§17.2](#172-terminals-exp1-p7-drawing-54201-exp2-p5)).
- EXP1 says the sum alarm "sends a 230 V output", EXP2 describes a potential-free contact; the drawings show an NC/C/NO relay.
- Room-sensor stop hysteresis: EXP1 0.9 / 1.9 °C, EXP2 1 / 2 °C.
- [INST p.20] (230 V text) gives heater steps 1.5/3/4.5 kW; [INST p.21–22] (400 V text) gives 3/6/9 kW – the latter applies to the Duo 12 400 V.
- [INST p.37] says history over "selected time interval"; [USER p.15] says last 60 minutes (LOGGTIME 1 min × buffer).
- USER heat-curve example shows "MIN 22 °C, MAX 70 °C" on screen, while factory MIN is 10 °C and MAX 55 °C [USER p.14 vs INST p.51].
- TIQ labels r5F/r60 as brine out/in although keys say brine_in/brine_out.
- Incoming neutral: ELEC p.41 lands it on **N3**, INST p.16 fig. 8 on **N2**. N2/N3/N1b are linked internally [ELEC p.39], so either works electrically.
- NODE 11 (pool) overlaps the NODE 2–18 passive-cooling range in EXP1 [§17.3](#173-configuration-on-the-duo-older-controller-node-based-exp1-p56).

---

## 27. Image index

| File | Source | Content |
|---|---|---|
| `ELEC_p002_reference-explanation.png` | ELEC p.2 | How to read sheet/row/column cross-references; general rules |
| `ELEC_p039_Duo12-400V_sheet1_power-circuit.png` | ELEC p.39 (printed 37) | Power circuit: X1, compressor, pumps, valve, heater |
| `ELEC_p040_Duo12-400V_sheet2_control-unit-E1.png` | ELEC p.40 (printed 38) | E1 terminals 1–8, 209–220, 301–326 |
| `ELEC_p041_Duo12-400V_sheet3_external-connections.png` | ELEC p.41 (printed 39) | Field terminals |
| `ELEC_p042_Duo12-400V_sheet4_parts-list.png` | ELEC p.42 (printed 40) | Parts list |
| `ELEC_p102…p107_Duo12-Optimum_*.png` | ELEC p.102–107 (printed 100–105) | Optimum sheets 1–5 (p.105 and p.106 are two versions of the external-connections sheet) |
| `INST_p008_connection-dimensions.png` | INST p.8 | Pipe connections |
| `INST_p011/p012_hydraulic-system-*.png` | INST p.11–12 | System VL / D |
| `INST_p013_heat-pump-components.png` | INST p.13 | Components |
| `INST_p014_outdoor-sensor_NTC-tables.png` | INST p.14 | Sensor tables |
| `INST_p016_fig8_electrical-connections.png` | INST p.16 | Fig. 8 |
| `INST_p017/p018_electrical-cubicle-*.png` | INST p.17–18 | Cubicle layouts |
| `INST_p021_fig9_control-and-sensor-connections.png` | INST p.21 | Fig. 9 |
| `INST_p023_system-D_external-heaters.png` | INST p.23 | System D wiring |
| `INST_p024_EVU-and-room-reduction.png` | INST p.24 | EVU / 10 kΩ |
| `INST_p026_brine-filling.png` | INST p.26 | Brine filling |
| `INST_p027_phase-rotation-check.png` | INST p.27 | Phase check |
| `INST_p055_tech-specs-400V.png` | INST p.55 | Specifications |
| `EXPCARD-EN_p004_connection-overload.png` | EXP1 p.4 | Card mounting, overload |
| `EXPCARD-EN_p007_wiring-901515.png` | EXP1 p.7 | Card wiring 54201 EN |
| `EXPCARD-086U6715_p004_EN-text-fig1.png`, `…p005_EN-wiring.png` | EXP2 p.4–5 | Newer card instructions, wiring |
| `COOLMOD_p014/p016_*` | COOL p.14, 16 | Module dimensions, connections |
| `COOLMOD_p018/p019_*` | COOL p.18–19 | Pressure curves |
| `COOLMOD_p020/p022/p024_*` | COOL p.20, 22, 24 | Heating / passive / active modes |
| `COOLMOD_p028/p029_*` | COOL p.28–29 | Module wiring |
| `FANCOIL_p006–p008_*` | FAN p.6–8 | Fan-coil dimensions, installation |
| `REPO_esphome-thermia_ext-port-pinout.jpg` | REPO-T | EXT header photo |
| `REPO_esphome-thermia-room_*.svg` | REPO-R | Room-sensor wiring, timing, frame layout |
