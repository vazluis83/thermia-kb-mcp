> Esta é a versão em português europeu (pt-PT) da base de conhecimento. A versão em inglês é `thermia-duo12-knowledge-base-EN.md`.

# Thermia Duo 12 (400 V 3N) – base de conhecimento técnica

Referência para construir um controlador/monitor com ESP32 para uma bomba de calor geotérmica (água glicolada/água) **Thermia Duo 12, 400 V trifásica**. Reúne tudo o que consta dos manuais fornecidos sobre ligações, projeto elétrico, lógica de controlo, parâmetros, acessórios e integração, bem como os protocolos do barramento EXT e do sensor de ambiente, obtidos por engenharia inversa e usados nos projetos `esphome-thermia`.

Idioma: português europeu. A versão em inglês, com o mesmo conteúdo, está em `thermia-duo12-knowledge-base-EN.md`.

---

## 0. Como usar este documento

### 0.1 Ficheiros de origem e numeração de páginas

Cada facto tem uma etiqueta de origem como **[INST p.21]**. Os números de página são **números de página do PDF**, ou seja, o número que um leitor de PDF mostra. Quando o número impresso difere, é indicado como "printed p.X" (p. impressa X).

| Etiqueta | Ficheiro (conforme fornecido) | Documento | Página PDF vs página impressa |
|---|---|---|---|
| **INST** | `180449c4-Duo-installation.pdf` | Thermia Duo – Installation instructions (instruções de instalação), 9680-54961001, Version 4 (60 pp.) | igual |
| **ELEC** | `b90a054f-Duo-electrical_installation.pdf` | Thermia Duo – Electrical installation instructions (instruções de instalação elétrica), 9680-55353001 Rev. 2, 2006 (139 pp.) | PDF = impressa + 2 |
| **USER** | `6dbc84d0-Duo-user_manual.pdf` | Thermia Duo – User's manual (manual do utilizador), 9680-54962001 Rev. 2 (36 pp.) | PDF = impressa + 2 |
| **EXP1** | `e73e7672-Expansionskort_EN_rev3.pdf` | Thermia Diplomat Expansion Card – Instructions (placa de expansão), 9680-55173001 Rev 3 (9 pp.) | PDF p.3–6 = impressa p.1–4; p.7 = esquema elétrico 54201 EN; p.8 = impressa p.5 (em branco) |
| **EXP2** | `d05bb0cb-Thermia_expansioncard_install_086U6715_MULTI.pdf` | Instruções de instalação da placa de expansão 086U6715 (multilingue; inglês nas p.4–5) | igual |
| **COOL** | `53c4c5d0-CoolingModule_install_086U7815_MULTI.pdf` | Instalação do módulo de arrefecimento Passive / Passive-Active 086U7815 (texto em inglês na p.5, desenhos nas p.14–29) | igual |
| **FAN** | `b442635d-Ventiloconvectores.pdf` | Catálogo de ventiloconvectores Zantia, em português (pp. 296–326 impressas) | PDF p.N = impressa p.294+N |
| **REPO-T** | github.com/mdepa91/esphome-thermia @ `ab88ec7` (2026-10-14) | Componente ESPHome para a porta EXT (README, `__init__.py`, `example.yaml`, `docs/`) | – |
| **REPO-R** | github.com/mdepa91/esphome-thermia-room @ `f8f71de` (2026-10-24) | Emulador ESPHome do sensor de ambiente (README) | – |
| **TIQ** | github.com/ThermIQ/thermiq_mqtt-ha @ `e1123c5` (2026-10-22), `heatpump/thermiq_regs.py` | Mapa completo de registos usado pelo REPO-T | – |

No repositório GitHub / servidor MCP os PDF estão em `src/thermia_kb_mcp/data/sources/`, com o nome `TAG_<título>.pdf` (por exemplo `ELEC_Duo-electrical-installation_9680-55353001.pdf`). A ferramenta MCP `get_source_page(source, page)` mostra qualquer página citada.

### 0.2 Pasta de imagens

`images/` contém as páginas renderizadas de todos os esquemas e desenhos relevantes. Os nomes dos ficheiros indicam a origem e a página PDF, por exemplo `ELEC_p040_Duo12-400V_sheet2_control-unit-E1.png` = ELEC, página PDF 40. O índice está na [secção 27](#27-índice-de-imagens).

### 0.3 Marcadores de confiança

- Sem marcador: indicado no texto ou na tabela da fonte.
- **[esquema]**: lido por mim a partir de um desenho (fios seguidos). Fiel ao desenho, mas convém confirmar na unidade.
- **[inferência]**: dedução minha a partir de vários factos; não está indicada em nenhum lado. Verificar antes de confiar.
- **[comunidade]**: obtido por engenharia inversa por terceiros (REPO-T / REPO-R / TIQ), não provém da Thermia.

### 0.4 Que Duo 12 tem?

Os documentos cobrem várias variantes. Veja a placa de características e a placa de controlo:

| Variante | Alimentação | N.º do desenho | Onde |
|---|---|---|---|
| **Duo 12 (standard), 400 V 3N** | 400 V 3-N | 56960 (folhas 1–4, rev 2, 2006) | ELEC p.39–42 (impressas 37–40) |
| **Duo Optimum 12, 400 V 3N** | 400 V 3-N | 57156 (folhas 1–5, rev 1, 2006) | ELEC p.102–107 (impressas 100–105) |
| Duo 12 ES | 230 V 1-N | – | ELEC p. impressas 17–20; não tratado em detalhe aqui |

O **Optimum** tem circuladores com velocidade regulada (0–10 V) e contactos de alarme, e um menu de serviço adicional "Thermia Duo Optimum" ([§16.9](#169-menu-exclusivo-do-optimum-inst-p42)). Tudo o resto é comum. Na unidade standard trifásica, assuma o desenho 56960, a menos que os circuladores sejam Wilo com velocidade regulada ligados aos bornes 327–334.

### 0.5 Instalação de referência (este repositório)

A unidade para a qual esta base de conhecimento foi construída é uma **Thermia Duo Optimum 12, 400 V 3N, instalada sem depósito de AQS**. Para ela:

- Usar os desenhos Optimum, 57156: [ELEC p.102–107]. Acrescentam circuladores Wilo de velocidade variável nos bornes 327–334, o menu de serviço Optimum ([§16.9](#169-menu-exclusivo-do-optimum-inst-p42)) e os alarmes dos circuladores CIRC. PUMP / BRINE PUMP ([§16.3](#163-alarmes-inst-p34-p4850-user-p2930)). Não há WSK na cadeia de sobrecarga 309/310.
- **Sem depósito**, por isso os sensores de AQS 311/312 (WW TEMP) e 325/326 (TOPP TWS) não estão ligados, e a saída 214 / válvula desviadora M3 não tem circuito de AQS a jusante.
  - Configurar **WARMWATER → START = OFF**, que segundo o [INST p.38] significa "sem alarme de sensor". Caso contrário, o sensor em aberto gera **SENSOR WARMWATER** [INST p.34].
  - Configurar TOPH. INTERVAL = OFF [INST p.52].
  - **[inferência]** Confirmar no visor que a produção de AQS nunca arranca. Verificar se a M3 está fisicamente montada ou tamponada, e que o circuito de aquecimento não passa pela sua porta de AQS.
- Sem pedido de AQS, a alternância TIME HEAT / TIME WARMWATER, o limite de 45 min de AQS e a lógica de reforço de AQS ([§15.4](#154-água-quente-sanitária-inst-p30-p33-p4647)) nunca se aplicam.
- Registos do barramento EXT específicos desta instalação: r1E / r1F (velocidade dos circuladores, %), r62 bit 0x40 (Optimum instalado), r44 (início de AQS; desconhece-se como o OFF é codificado, por isso ler antes de escrever).

---

## 1. Visão geral do produto

- Unidade de aquecimento geotérmica completa: compressor scroll, permutadores de calor em aço inoxidável, circulador de água glicolada (captação), circulador de aquecimento, válvula desviadora de AQS, resistência elétrica de imersão integrada de 9 kW com 3 escalões na linha de ida, e computador de controlo com ecrã gráfico. A água quente sanitária (AQS) é produzida num depósito **externo**. [USER p.6–7]
- Temperatura máxima de ida para o sistema de aquecimento: 55 °C ("sistema de baixa temperatura"). A bomba de calor (BC) cobre o máximo possível da necessidade antes de a resistência de apoio entrar. [USER p.6]
- Três circuitos de fluido: circuito de salmoura (água glicolada) / fluido de captação (mistura anticongelante, circuito enterrado), circuito frigorigéneo (R407C nos modelos de 400 V), circuito de aquecimento (água para radiadores/piso radiante e depósito). Circuito frigorigéneo: evaporador → compressor → condensador → **sub-arrefecedor** (pré-aquece a água de retorno do aquecimento) → válvula de expansão. [USER p.7–8]
- Painel de controlo "Thermia Diplomat": ecrã de caracteres/gráfico, 4 teclas (+, −, direita, esquerda) e um LED de alarme (fixo = em funcionamento, intermitente = alarme). [INST p.31], [USER p.9–10]
- Unidade de controlo **E1**: Kimsafe AB, ref. 9588-55701001 (standard) / 9588-56464001 (Optimum). Ecrã **E3**: Kimsafe 9588-55702001 / 9588-56562001. [ELEC p.42, p.107]
- **[comunidade]** A placa do controlador do Duo é construída em torno de um Microchip **PIC16F887**, com relés Omron G2RL-1-E de 24 V DC (16 A/250 V). O ecrã liga através de uma ficha RJ45; o conector **EXT** (GND, SDA, SCL, 5 V) fica junto a ela, na aresta superior. [REPO-T README, `docs/hardware/ext-port-pinout.jpg`]. Fotografia: `images/REPO_esphome-thermia_ext-port-pinout.jpg`.

---

## 2. Especificações técnicas – Duo 12 (400 V)

Da tabela do Duo 400 V [INST p.55] (`images/INST_p055_tech-specs-400V.png`). Os valores dos outros tamanhos estão em [§2.2](#22-tabela-completa-de-400-v-todos-os-tamanhos-inst-p55).

| Item | Duo 12 (400 V 3-N) |
|---|---|
| Fluido frigorigéneo | R407C, **1.7 kg** |
| Pressão de ensaio / de projeto | 3.2 MPa / 2.9 MPa |
| Compressor | Scroll, óleo éster (Copeland, 400 V, ref. 9686-53314001 [ELEC p.42]) |
| Alimentação da rede | **400 V 3-N** (3 fases + neutro + terra (PE)) |
| Potência elétrica do compressor | **4.4 kW** |
| Compressor + resistência de apoio | **7.4 / 10.4 / 13.4 kW** com resistência de apoio de 3 / 6 / 9 kW |
| Resistência de imersão (apoio) | 3 / 6 / 9 kW (2 bancos de elementos: EP2 = 3 kW, EP1 = 6 kW) |
| Corrente de arranque (LRA) | **28 A** (o desenho 56960 mostra um arrancador suave R1 no circuito do compressor) |
| Fusível (grupo) | **16 A / 20 A / 25 A** com resistência de apoio de 3 / 6 / 9 kW |
| Potência calorífica (EN 255, entrada de água glicolada/saída de aquecimento 0/35 °C e 0/50 °C, incl. circuladores) | **11.12 kW / 10.53 kW** |
| COP (mesmas condições) | **4.5 / 3.3** |
| Caudal nominal – água glicolada (fluido de captação) | **0.63 l/s** (≈ 2.27 m³/h) |
| Caudal nominal – meio de aquecimento | **0.26 l/s** (≈ 0.94 m³/h) |
| Pressão externa disponível – água glicolada (standard) | **64 kPa** (requer tubo de captação 40 × 2.4 mm) |
| Pressão externa disponível – aquecimento (standard) | **48 kPa** |
| Pressão externa disponível – Duo Optimum, água glicolada / aquecimento | **82 kPa / 97 kPa** |
| Temperatura de entrada da água glicolada máx./mín. | **+20 / −10 °C** |
| Temperatura do meio de aquecimento máx./mín. | **55 / 20 °C** |
| Peso (sem embalagem) | **165 kg** |
| Gama de regulação do relé térmico de sobrecarga F11 | 9–13 A [ELEC p.42] |

Notas [INST p.55]: "External available pressure" (pressão externa disponível) é a perda de carga admitida fora da bomba de calor antes de o caudal descer abaixo do nominal. "*" na tabela = dados não disponíveis à data de impressão.

### 2.1 Manuseamento do fluido frigorigéneo [INST p.54]

- Duo de 400 V: **R407C**; Duo de 230 V: R404A. A utilização de outro fluido frigorigéneo anula a garantia, salvo aprovação escrita da Thermia.
- Não inflamável; mais pesado que o ar (risco de asfixia em locais pequenos e sem ventilação); forma fosgénio em contacto com chama aberta. Trabalhos apenas por pessoal certificado em refrigeração; quantidade de recarga conforme a placa de características.

### 2.2 Tabela completa de 400 V (todos os tamanhos) [INST p.55]

| | Duo 4 | Duo 6 | Duo 8 | Duo 10 | **Duo 12** | Duo 16 |
|---|---|---|---|---|---|---|
| Carga de R407C (kg) | 0.75 | 1.1 | 1.25 | 1.6 | **1.7** | 1.8 |
| Potência do compressor (kW) | * | 2 | 2.3 | 3.6 | **4.4** | 5.6 |
| Comp. + RA 3/6/9 kW (kW) | * | 5.0/8.0/11.0 | 5.3/8.3/11.3 | 6.6/9.6/12.6 | **7.4/10.4/13.4** | 8.6/11.6/14.6 |
| LRA (A) | 36 | 14 | 25 | 28 | **28** | 47 |
| Fusível RA 3/6/9 kW (A) | * | 10/16/20 | 16/16/20 | 16/16/20 | **16/20/25** | 20/20/25 |
| Potência 0/35 / 0/50 (kW) | 3.76/3.67 | 5.78/5.52 | 8.13/7.73 | 9.54/9.24 | **11.12/10.53** | 16.61/15.78 |
| COP 0/35 / 0/50 | 4.07/2.83 | 4.2/3.1 | 4.6/3.4 | 4.4/3.3 | **4.5/3.3** | 4.4/3.2 |
| Caudal de água glicolada (l/s) | 0.20 | 0.31 | 0.47 | 0.57 | **0.63** | 0.92 |
| Caudal de aquecimento (l/s) | 0.09 | 0.13 | 0.19 | 0.22 | **0.26** | 0.4 |
| Pressão ext. água glicolada / aquecimento (kPa) | 35/50 | 31/43 | 33/39 | 32/34 | **64/48** | 56/40 |
| Optimum água glicolada / aquecimento (kPa) | * | 89/109 | 92/106 | 82/99 | **82/97** | 70/88 |
| Peso (kg) | 140 | 145 | 150 | 155 | **165** | 175 |

(RA = resistência de apoio.)

[INST p.56] tem os modelos "ES" de 230 V (R407C, imersão 1.5/3/4.5 kW exceto o ES16) e [INST p.57] os modelos "Duo D" de 230 V (R404A). Não são a unidade do utilizador.

---

## 3. Parte mecânica e hidráulica

### 3.1 Colocação e dimensões [INST p.4–8]

- Não instalar onde possa gelar; o piso tem de suportar o peso; piso estável; pés ajustáveis. Dreno de condensados da tina de recolha para o ralo do pavimento, tubo 14/10 mm, saída pelo painel inferior. [INST p.4]
- Dimensões da unidade: **600 mm de largura × 690 mm de profundidade × 1490 mm de altura** (pés na posição mais alta). [INST p.7]
- Folgas de serviço: 300 mm de cada lado, 300 mm por cima, 600 mm à frente, 10 mm atrás. [INST p.7]
- Painel frontal: abrir o painel superior articulado, retirar os parafusos, deslizar o painel para cima e retirá-lo – atenção à cablagem do sistema de controlo. [INST p.6, p.28]

### 3.2 Ligações hidráulicas [INST p.8] (`images/INST_p008_connection-dimensions.png`)

| Ligação | Dimensão |
|---|---|
| Saída de água glicolada (da BC) | cobre 28 mm |
| Entrada de água glicolada (para a BC) | cobre 28 mm |
| Linha de ida do aquecimento | cobre 28 mm |
| Linha de retorno do aquecimento | cobre 28 mm |
| Linha do depósito de AQS | 22 mm (pode ser ligada à esquerda ou à direita) |
| Saídas de cabos (alimentação/sensores) | painel superior; saída separada para o cabo de comunicação |

### 3.3 Componentes internos [INST p.13] (`images/INST_p013_heat-pump-components.png`)

1 painel frontal · 2 painel de instrumentos · 3 **válvula comutadora (desviadora)** · 4 sensor da linha de ida · 5 circulador de aquecimento · 6 resistência elétrica de apoio · 7 evaporador (isolado) · 8 válvula de expansão · 9 filtro desidratador · 10 circulador de água glicolada (sistema de arrefecimento) · 11 retorno do aquecimento Cu 28 mm · 12 ida do aquecimento Cu 28 mm · 13 saídas de cabos para alimentação e sensores · 14 sub-arrefecedor · 15 sensor da linha de retorno · 16 condensador com dreno do lado primário · 17 compressor · 18 entrada de água glicolada Cu 28 mm · 19 saída de água glicolada Cu 28 mm · 20 saída do cabo de comunicação.

### 3.4 Sistemas hidráulicos [INST p.11–12]

- **Sistema VL** (`images/INST_p011_hydraulic-system-VL.png`): bomba de calor com a sua resistência elétrica interna; radiadores/piso radiante, depósito de AQS através da válvula desviadora interna, expansão.
- **Sistema D** (`images/INST_p012_hydraulic-system-D.png`): duas configurações – "Duo com opção de shunt externo" (válvula misturadora) e "Duo em paralelo com resistência de imersão externa". (Os números de posição do desenho 4, 5, 7, 47, 50, 51, 57–62, 64, 65, 77, 87, 96–99, 115, 117 não são explicados no texto.)

### 3.5 Válvula de segurança, expansão, enchimento [INST p.9–10], [USER p.4, p.27–28]

- Um sistema de aquecimento com vaso de expansão fechado necessita de manómetro e válvula de segurança aprovados, DN 20 no mínimo, pressão máxima de abertura **1.5 bar**. A tubagem do vaso à válvula de segurança tem de subir de forma contínua.
- Encher o sistema de aquecimento até ~1 bar, purgar completamente, repor. Verificar mensalmente: 1–1.5 bar; repor abaixo de 0.8 bar (a frio). Não adicionar produtos químicos de tratamento de água. Testar ambas as válvulas de segurança (aquecimento e depósito) pelo menos 4× por ano.
- Montar o filtro de partículas conforme indicado no esquema do sistema (retorno do aquecimento).
- Linhas de água glicolada: tubos flexíveis através de mangas de borracha no painel superior, isolados com barreira de vapor. As passagens na parede têm inclinação ≥1 cm por 30 cm para baixo, em direção ao exterior; furos separados para saída e entrada. [INST p.5, p.10]

### 3.6 Enchimento de água glicolada (fluido de captação) [INST p.25–26] (`images/INST_p026_brine-filling.png`)

- Anticongelante: etilenoglicol ou etanol com inibidor de corrosão, **30 % em volume**. O tubo de captação DN40 contém ~1.0 l/m.
- Fórmula do volume: (comprimento do tubo + 5) × 0.30 = volume de anticongelante. Exemplo para 400 m: (400+5)×0.30 = 121.5 l → ponto de congelação ≈ −15 °C. Volume da unidade 5 l.
- Procedimento: modo de funcionamento OFF; misturar num recipiente externo; encher com uma bomba externa com filtro ≤1 mm através da ligação de enchimento junto à válvula de corte 62; fechar 57; abrir 62 e 64; abrir 61 com mangueira de volta à tina; arrancar a bomba externa e depois arrancar o **circulador de água glicolada a partir do menu de serviço MANUAL** (desliga após ~10 min); deixar o ar acumular-se no depósito de purga; aliviar o excesso de pressão na válvula 60; o nível do líquido não pode descer abaixo de 2/3 da altura do depósito; fechar 61 e 62; passar de OFF/manual para o modo escolhido.
- **O circulador de água glicolada tem de funcionar para encher → a instalação elétrica tem de estar primeiro concluída.**
- Verificação: o nível de água glicolada tem de estar sempre visível no vaso de expansão; uma ligeira descida no primeiro mês é normal. [USER p.27]

### 3.7 Ordem de colocação em serviço [INST p.4, p.27]

1. Tubagem → 2. encher e purgar o sistema de aquecimento → 3. instalação elétrica → 4. encher o circuito de água glicolada → 5. ajustar as definições de fábrica → 6. teste de funcionamento → 7. certificado de instalação [INST p.58].

- Não arrancar antes de o sistema de aquecimento, o depósito e o circuito de água glicolada estarem cheios (danos nos circuladores).
- Para funcionar só com aquecimento elétrico antes de o circuito de água glicolada estar pronto: selecionar o modo de funcionamento **ADD.HEATER** (resistência de apoio) para que nem o circulador de água glicolada nem o compressor possam arrancar.
- **Sequência de fases:** arrancar o compressor; rotação errada mostra **"Err. phase seq."** → trocar duas fases de entrada (por exemplo, L1 e L3). [INST p.27] (`images/INST_p027_phase-rotation-check.png`)

---

## 4. Alimentação elétrica e distribuição de energia

### 4.1 Requisitos de alimentação [INST p.15], [ELEC p.2]

- Ligação fixa (permanente). Seccionamento por um **interruptor de todos os polos (disjuntor) com abertura de contactos ≥3 mm**. O interruptor de segurança é a forma de desenergizar a unidade.
- **Carga máxima para equipamentos ligados externamente: 2 A.** [INST p.15]
- O cabo de alimentação entra pelo painel superior e liga **apenas** à régua de bornes designada.
- A potência máxima da resistência de apoio tem de ser selecionada no menu (MAX STEP). [INST p.15]
- Fusível de grupo do Duo 12: 16 / 20 / 25 A para MAX STEP 3 / 6 / 9 kW. [INST p.55]
- Os cabos de sensores de baixa tensão têm de ser mantidos afastados dos cabos de rede: **separação ≥25 cm quando em paralelo, para percursos até 100 m**; mais para percursos mais longos. [ELEC p.2]
- Antes de ligar a alimentação: sistema de aquecimento, circuito de água glicolada e depósito de AQS cheios e purgados. [ELEC p.2]

### 4.2 Régua de bornes de entrada X1 (400 V 3N) [ELEC p.41 folha 3], [INST p.16 fig. 8]

Imagens: `images/ELEC_p041_Duo12-400V_sheet3_external-connections.png`, `images/INST_p016_fig8_electrical-connections.png`.

Bornes, da esquerda para a direita: **N3 · 3L1 · PE5 · 1L1 · 1L2 · 1L3** | **2L1 · 2L2 · 2L3 · PE1**

| Borne | Alimenta | Origem |
|---|---|---|
| 1L1, 1L2, 1L3 | Compressor (via F11 → R1 → M2) e, através de pontes, 2L1–2L3 | [ELEC p.39, p.41] |
| 2L1, 2L2, 2L3 | Resistência de apoio (via relés T1 e E1) | [ELEC p.39] |
| 3L1 | Fase de comando: F0 (10 A) → unidade de controlo, válvula desviadora, pressostato; ligado a 2L1 na entrega | [ELEC p.39, p.41] **[esquema]** |
| N3 (ligado a N2, N1b) | Neutro para circuladores, válvula, comando | [ELEC p.39] |
| PE1 | Terra (PE) de proteção de entrada | [ELEC p.41] |
| PE5 | Borne de terra (desenhado como PE separado junto a 2L1–2L3; sem condutor desenhado até à EP) | [ELEC p.39] |

- Predefinição de fábrica ("Strapt at delivery", ligado na entrega): **3L1 ligado a 2L1** por ponte, e 1L1→2L1, 1L2→2L2, 1L3→2L3 com pontes, de modo que um único cabo de 5 condutores (L1, L2, L3, N, PE) alimenta tudo. [ELEC p.41] **[esquema]**
- Fig. 8 (400 V): cabo de entrada de 5 condutores PE→PE, condutor 1→**N2**, 2→**1L1**, 3→**1L2**, 4→**1L3**; pontes 1L1–2L1, 1L2–2L2, 1L3–2L3. [INST p.16]
- O desenho mostra um seccionador tripolar externo **Q1** (1-2, 3-4, 5-6) no cabo de entrada. [ELEC p.41]
- **[inferência]** Retirar as pontes permitiria alimentações separadas (compressor 1Lx, resistência 2Lx, comando 3L1) – por exemplo para controlo tarifário – mas não é dado nenhum procedimento para o Duo de 400 V. A fig. 8 mostra "cabo de entrada para a bomba de calor" e "para a resistência auxiliar" em separado apenas na versão de 230 V.

### 4.3 Disposição do quadro elétrico [INST p.17–18]

Duas versões de quadro, ambas com: K1 contactor/arrancador do compressor · F11 relé de sobrecorrente do compressor · F2 fusível do circulador · F1 fusível do circulador de água glicolada · F0 fusível da válvula comutadora · computador de controlo · T1 corte térmico da resistência elétrica · réguas de bornes para a alimentação de entrada e para os sensores de temperatura. A versão **53369-A** tem ainda (9) réguas de bornes para água quente, linha de ida e comando da resistência adicional. Imagens: `images/INST_p017_electrical-cubicle-55527-B.png`, `images/INST_p018_electrical-cubicle-53369-A.png`.

Nota: o desenho 56960 do Duo 12, de 2006, mostra um **arrancador suave R1** em vez de um contactor K1. A sua unidade pode ter qualquer um deles. [ELEC p.39]

### 4.4 Dispositivos de proteção (Duo 12, desenho 56960) [ELEC p.42]

| Ref. | Dispositivo | Valor | Protege |
|---|---|---|---|
| F0 | Merlin Gerin disjuntor 1P | C10 A | Fase de comando 3L1: alimentação da unidade de controlo (via 217), válvula desviadora M3, pressostato B1 |
| F1 | Merlin Gerin disjuntor 1P | C3 A | Circulador de água glicolada M1 |
| F2 | Merlin Gerin disjuntor 1P | C3 A | Circulador de aquecimento M4 |
| F3 | Merlin Gerin disjuntor 1P | C3 A | Saída 209 (apoio/aquecimento de topo) |
| F4 | Merlin Gerin disjuntor 1P | C3 A | Saída 210 (óleo/El) |
| F11 | Telemecanique relé térmico de sobrecarga + bloco auxiliar | 9–13 A | Compressor M2; contacto auxiliar NC 95-96 para a unidade de controlo 309/310 |
| T1 | Ego termóstato de segurança (tripolar) | 30 A 230 V | Sobretemperatura da resistência de apoio; abre as três fases da resistência |
| R1 | Kimsafe arrancador suave | 400 V 3N | Arranque do compressor (o desenho mostra tirístores em duas das três fases – não referido no texto) |

---

## 5. Circuito de potência – folha 1 (Duo 12, desenho 56960) [ELEC p.39]

Imagem: `images/ELEC_p039_Duo12-400V_sheet1_power-circuit.png`. Todos os fios são cinzentos ("gy-NNN"), salvo indicação em contrário; "bl" = neutro azul. As referências cruzadas como "/2.1B" significam folha 2, coluna 1, linha B. **[esquema]** para toda a secção.

### 5.1 Compressor M2

1L1 / 1L2 / 1L3 (gy-501/502/503) → **F11** 1/3/5 → 2/4/6 (gy-601/602/603) → **arrancador suave R1** L1/L2/L3 → U/V/W (gy-701/702/703) → **M2** T1/T2/T3 (3~), PE3.
- Bobina de comando de R1: **A1 ← borne 212 da unidade de controlo**, A2 → neutro (linha F). → O compressor funciona quando o relé 212 de E1 está ligado.
- Contactos auxiliares de F11: **95-96 (NC)** → 309/310 da unidade de controlo (entrada de disparo por sobrecarga); 97-98 (NO) não utilizado.

### 5.2 Circulador de água glicolada M1

Unidade de controlo **211** → gy-211 → **F1** (C3 A) → gy-101 → M1 L; N azul; PE3.
- Duo standard: M1 tem um contacto térmico de enrolamento **WSK** (borne "WSK" de X3) ligado em série na entrada de sobrecarga (350-351). [ELEC p.40, p.42]

### 5.3 Circulador de aquecimento M4

Unidade de controlo **213** → gy-213 → **F2** (C3 A) → gy-102 → M4 L; N azul; PE3.

### 5.4 Válvula desviadora (inversora) de AQS M3 – Honeywell, 9360-37547001

Válvula motorizada de 3 fios: **borne 3** = L permanente (3L1 → F0 → gy-103), **borne 6** = L comutada da unidade de controlo **214** (gy-214) = posição de AQS, **borne 2** = neutro (N2). [ELEC p.39] **[esquema]**

### 5.5 Resistência elétrica de apoio EP (Backer 3 kW + 6 kW, 9571-53938A00)

```
2L1 (gy-401) → T1 11-12 → gy-404 → E1 relay common "L1" (1)
2L2 (gy-402) → T1 21-22 → gy-407 → E1 relay common "L2" (2)
2L3 (gy-403) → T1 31-32 → gy-410 → EP1 L3 (6 kW) and gy-411 → EP2 L3 (3 kW)   (L3 not switched)
E1 "6KW" L1-side (5) → gy-405 → EP1 L1 ;  E1 "6KW" L2-side (6) → gy-406 → EP1 L2
E1 "3KW" L1-side (7) → gy-409 → EP2 L1 ;  E1 "3KW" L2-side (8) → gy-408 → EP2 L2
```

- Cada banco é energizado ao fechar **ambos** os contactos de relé L1 e L2 em E1; L3 está permanentemente ligada através de T1.
- Escalões: 3 kW = EP2 · 6 kW = EP1 · 9 kW = EP1 + EP2. [USER p.8], [INST p.39]
- T1 (Ego 30 A) corta as três fases em caso de sobretemperatura → alarme **ADD.HEATER** ("Thermal cut-out triggered", corte térmico disparado). [INST p.34]
- Os relés integrados da unidade de controlo comutam diretamente as fases da resistência; não existe contactor separado da resistência neste desenho. **[esquema]**

---

## 6. Unidade de controlo E1 – mapa completo de bornes (folha 2) [ELEC p.40]

Imagem: `images/ELEC_p040_Duo12-400V_sheet2_control-unit-E1.png` (Optimum: `images/ELEC_p103_Duo12-Optimum_sheet2_control-unit-E1.png`).

Conectores de E1: **Ext. COM** (placa de expansão / barramento EXT, ver [§21](#21-porta-ext--protocolo-do-barramento-i2c-comunidade-repo-t)) · **DISPLAY** (para E3) · bornes de relés/alimentação · bornes de sensores SELV (muito baixa tensão de segurança).

### 6.1 Bornes de relés e de 230 V

| Borne de E1 | Função | Ligado a | Tipo |
|---|---|---|---|
| L1 (1) | Comum do relé da resistência, fase 2L1 via T1 | gy-404 | fase do sistema de 400 V |
| 6KW (5) | 2L1 comutada → banco EP1 de 6 kW | gy-405 | saída de relé |
| 3KW (7) | 2L1 comutada → banco EP2 de 3 kW | gy-409 | saída de relé |
| L2 (2) | Comum do relé da resistência, fase 2L2 via T1 | gy-407 | fase |
| 6KW (6) | 2L2 comutada → EP1; **alimenta também o borne de campo 209 via F3** | gy-406 | saída de relé |
| 3KW (8) | 2L2 comutada → EP2; **alimenta também o borne de campo 210 via F4** | gy-408 | saída de relé |
| **211** | **Circulador de água glicolada M1** (via F1) | gy-211 | saída de 230 V |
| **212** | **Compressor em funcionamento** – bobina A1 do arrancador suave R1 | – | saída de 230 V |
| **213** | **Circulador de aquecimento M4** (via F2) | gy-213 | saída de 230 V |
| **214** | **Válvula desviadora M3 → AQS** (borne 6 da válvula) | gy-214 | saída de 230 V |
| **215** | **Motor do shunt ABRIR (+)** – borne de campo 215 | – | saída de 230 V |
| **216** | **Motor do shunt FECHAR (−)** – borne de campo 216 | – | saída de 230 V |
| **217** | **Alimentação L para E1** (de F0, gy-217b); alimenta também o borne 1 do fluxóstato | gy-217b | alimentação de 230 V |
| **218** | **Entrada: pressostato de funcionamento B1** (B1 alimentado com L de F0 via gy-104) | – | entrada de 230 V |
| **219** | **Entrada: retorno do fluxóstato FL** (acessório) | – | entrada de 230 V |
| **220** | **Neutro** (N1b) | – | N |

**[esquema]** para a atribuição 211–220. Os números dos fios gy-211, gy-213, gy-214, gy-217 coincidem com os números dos bornes, o que sustenta a leitura.

### 6.2 Bornes SELV (baixa tensão)

| Bornes | Função | Dispositivo | Cores dos fios |
|---|---|---|---|
| **301–302** | Sensor da linha de ida ("Sensor radiator out", Rad Out) | B4 NTC (Betatherm 9588-54680001) | 301 branco, 302 vermelho |
| **303–304** | **Sensor de ambiente (acessório)** | unidade de ambiente 086U6003 / emulador | – |
| **305–306** | **Sensor exterior** | NTC (tabela do exterior) | – |
| **307–308** | **Entrada EVU / temporizador** | contacto livre de potencial ou 10 kΩ | – |
| 309–310 | Entrada de disparo do relé de sobrecarga: cadeia M1 WSK (350-351, só standard) + F11 95-96 | interno | – |
| **311–312** | **Sensor de AQS** (WW TEMP) | NTC | 311 branco, 312 vermelho |
| 313–314 | Sensor da linha de retorno ("Sensor radiator in", Rad In) | B6 NTC 9588-53809001 | interno |
| 315–316 | Sensor de saída de água glicolada | B7 NTC 9588-53808001 | interno |
| 317–318 | Sensor de entrada de água glicolada | B8 NTC 9588-53807001 | interno |
| 319–320 | Pressostato de alta pressão | B2 Saginomiya 31 bar 9578-55973001 | interno |
| 321–322 | Pressostato de baixa pressão | B3 Saginomiya 0.8 bar 9578-55212001 | interno |
| 323–324 | Sensor do tubo de descarga ("TRYCKRÖR" = gás quente) | B9 NTC 9588-55322001 | interno |
| **325–326** | **Sensor de topo da AQS** ("TOPP TWS") | NTC | 325 branco, 326 vermelho |

Todas as ligações de sensores, termóstato de ambiente e EVU são **SELV**. [INST p.19–22]

### 6.3 Bornes exclusivos do Optimum (desenho 57156 folha 3) [ELEC p.104]

Imagem: `images/ELEC_p104_Duo12-Optimum_sheet3_pump-0-10V-alarm.png`.

| Bornes | Função |
|---|---|
| 327–328 | Contacto de alarme do circulador de aquecimento M4 (fios 3, 4 do circulador) |
| 329–330 | Controlo de velocidade 0–10 V de M4 (fios 1, 2 do circulador) |
| 331–332 | Contacto de alarme do circulador de água glicolada M1 (fios 3, 4 do circulador) |
| 333–334 | Controlo de velocidade 0–10 V de M1 (fios 1, 2 do circulador) |

Ambos os circuladores: Wilo 9675-57045002. No Optimum, a entrada de sobrecarga 309/310 só tem F11 95-96 (sem WSK). [ELEC p.103, p.107]

---

## 7. Ligações de campo (externas) – folha 3 [ELEC p.41], [INST p.16, p.21]

Imagens: `images/ELEC_p041_Duo12-400V_sheet3_external-connections.png`, `images/INST_p021_fig9_control-and-sensor-connections.png`.

| Bloco | Bornes | O que ligar | Notas |
|---|---|---|---|
| Alimentação de entrada | N3, 3L1, PE5, 1L1, 1L2, 1L3, 2L1, 2L2, 2L3, PE1 | 400 V 3N + PE via seccionador Q1 | ver [§4.2](#42-régua-de-bornes-de-entrada-x1-400-v-3n-elec-p41-folha-3-inst-p16-fig-8) |
| Válvula shunt / aquecimento auxiliar | **PE, N1, 215 (+), 216 (−)** | Motor de shunt de 3 pontos a 230 V (cabo PE, 1=N1, 2=215, 3=216) | Sistema D ou sub-shunt |
| Fluxóstato (acessório) | **217, 219** | Contacto NC do fluxóstato (1-2) | ativar "F" em SYSTEM |
| Sensor de ambiente (acessório) | **303, 304** | Unidade de ambiente Thermia | tracejado = acessório |
| Sensor exterior | **305, 306** | NTC exterior | standard |
| EVU (acessório) | **307, 308** | contacto livre de potencial | |
| Aquecimento de topo | **PE, N4, 209** | bobina do contactor da resistência do depósito externo | 230 V, via F3 C3 A |
| Óleo / El | **N4, 210** | comando de caldeira externa/resistência elétrica | 230 V, via F4 C3 A |
| Sensor da linha de ida | **301 (branco), 302 (vermelho)** | B4 "Rad OUT" | deslocado quando se usa aquecimento externo |
| Sensor de AQS | **311 (branco), 312 (vermelho)** | "WW TEMP" | no depósito |
| Sensor de topo da AQS | **325 (branco), 326 (vermelho)** | "TOPP TWS" | no depósito |

- Cargas externas de 230 V (209, 210, 215/216): total máx. **2 A**. [INST p.15]
- 209 e 210 são **saídas de 230 V com tensão**, não contactos secos. [ELEC p.40] **[esquema]**

---

## 8. Listas de peças

### 8.1 Duo 12 400 V 3N, desenho 56960 folha 4 (rev 2, 2006-10-18) [ELEC p.42]

| Ref. | Designação | Fabricante | Dados elétricos | N.º de peça |
|---|---|---|---|---|
| B1 | Pressostato de funcionamento | Saginomiya | 26.5 bar | 9578-37142002 |
| B1 (alt.) | Pressostato de funcionamento | Saginomiya | 28.5 bar | 9578-55974001 |
| B2 | Pressostato de alta pressão | Saginomiya | 31 bar | 9578-55973001 |
| B3 | Pressostato de baixa pressão | Saginomiya | 0.8 bar | 9578-55212001 |
| B4 | Sensor de saída do radiador (ida) | Betatherm | NTC | 9588-54680001 |
| B6 | Sensor de entrada do radiador (retorno) | Betatherm | NTC | 9588-53809001 |
| B7 | Sensor de saída de água glicolada | Betatherm | NTC | 9588-53808001 |
| B8 | Sensor de entrada de água glicolada | Betatherm | NTC | 9588-53807001 |
| B9 | Sensor do tubo de descarga | Betatherm | NTC | 9588-55322001 |
| E1 | Unidade de controlo | Kimsafe AB | – | 9588-55701001 |
| E3 | Ecrã | Kimsafe AB | – | 9588-55702001 |
| EP | Resistência elétrica de apoio | Backer | 3 kW / 6 kW | 9571-53938A00 |
| F0 | Disjuntor | Merlin Gerin | 1P C10A | 9588-51463001 |
| F1–F4 | Disjuntor | Merlin Gerin | 1P C3A | 9585-53791001 |
| F11 | Relé térmico de sobrecarga | Telemecanique | 9–13 A | 9588-38379012 |
| F11 | Bloco de contactos auxiliares | Telemecanique | – | 9575-54492001 |
| M1 | Circulador (água glicolada) | Wilo | – | 9675-54178001 |
| M2 | Compressor | Copeland | 400 V | 9686-53314001 |
| M3 | Válvula inversora | Honeywell | – | 9360-37547001 |
| M4 | Circulador (aquecimento) | Wilo | – | 9675-53865002 |
| R1 | Arrancador suave | Kimsafe AB | 400 V 3N | 9588-56851001 |
| T1 | Termóstato de segurança | Ego | 30 A 230 V | 9579-54513001 |
| X1 | Régua de bornes | Phoenix | 400 V 3N | 9583-56893001 |
| X2 | Régua de bornes | Phoenix | Duo | 9583-55837001 |
| X3 | Borne | Phoenix | WSK | 9583-56967001 |

### 8.2 Duo Optimum 12, desenho 57156 folha 5 (rev 1, 2006-08-21) [ELEC p.107]

Igual a 8.1, exceto: E1 **9588-56464001**, E3 **9588-56562001**, M1 e M4 **Wilo 9675-57045002** (velocidade regulada, contacto de alarme), sem borne X3 WSK; referência de folha de B4 /4.6B.

---

## 9. Sensores de temperatura

### 9.1 Tabelas de resistência [INST p.14] (`images/INST_p014_outdoor-sensor_NTC-tables.png`)

Medir com os cabos dos sensores desligados do equipamento de controlo: primeiro sensor + cabo, depois só o sensor.

**Sensor exterior (Ω)**

| °C | −30 | −25 | −20 | −15 | −10 | −5 | 0 | 5 | 10 | 15 | 20 | 25 | 30 | 35 | 40 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Ω | 1884 | 1443 | 1115 | 868 | 681 | 538 | 428 | 343 | 276 | 224 | 183 | 150 | 124 | 103 | 86 |

**Sensores de ida / retorno / AQS / água glicolada ("coolant out", saída do fluido) (kΩ)**

| °C | 0 | 5 | 10 | 15 | 20 | 25 | 30 | 35 | 40 | 45 | 50 | 55 | 60 | 65 | 70 | 75 | 80 | 85 | 90 | 95 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| kΩ | 66.3 | 52.4 | 41.8 | 33.5 | 27.1 | 22.0 | 18.0 | 14.8 | 12.2 | 10.1 | 8.5 | 7.1 | 6.0 | 5.0 | 4.2 | 3.7 | 3.1 | 2.7 | 2.3 | 2.0 |

### 9.2 Ajustes de curva para firmware (cálculo meu a partir das tabelas)

Steinhart–Hart, 1/T = A + B·ln(R) + C·ln(R)³, T em K, R em Ω:

| Sensor | A | B | C | Erro máx. vs tabela |
|---|---|---|---|---|
| Exterior | 1.964301e-03 | 2.712476e-04 | 2.395526e-07 | 0.04 °C |
| Ida/retorno/AQS/água glicolada | 8.741949e-04 | 2.347277e-04 | 1.325708e-07 | 0.55 °C (arredondamento da tabela a temperaturas elevadas) |

Aproximações beta: exterior ≈ **150 Ω @ 25 °C, B ≈ 3416** (0–25 °C); os restantes ≈ **22 kΩ @ 25 °C, B ≈ 3665** (25–50 °C).

Use-as apenas para sensores **seus** do mesmo tipo. Não leia os sensores da própria bomba em paralelo com o controlador – uma carga/polarização adicional altera o que E1 mede.

### 9.3 Colocação e manuseamento

- Sensor exterior: em edifícios até 3 pisos, a 2/3 da altura da parede; em edifícios mais altos, entre o 2.º e o 3.º piso; não abrigado do vento nem exposto diretamente ao vento; não sobre metal refletor; ≥1 m de aberturas que deixem sair ar quente; vedar qualquer conduta. [INST p.14]
- Colocação do sensor da linha de ida: **depois** da resistência interna; se existir aquecimento externo, depois do shunt desse aquecimento. Bornes 301-302. [INST p.20–22]
- Desvios de calibração −5…+5 °C por sensor em SERVICE → INSTALLATION → CALIBRATION SENSOR (OUTDOOR, SUPPLYLINE, RETURNLINE, WARMWATER, BRINE OUT, BRINE IN). [INST p.41, p.53]

### 9.4 Comportamento em caso de falha de sensor [INST p.34, p.50]

| Sensor | Comportamento em caso de falha |
|---|---|
| Exterior | Usa-se 0 °C (mostrado a piscar) |
| Ida | Controlo passa a OFF; funciona apenas o circulador de aquecimento |
| Retorno | Retorno = ida − 5 °C (−15 °C dois minutos após o início da produção de AQS); ida máxima estimada 45 °C |
| AQS | Sem produção de AQS |
| Ambiente | Temperatura ambiente real não é mostrada; usa-se 20 °C para o cálculo |

---

## 10. Pressostatos e cadeia de segurança

| Dispositivo | Definição | Função | Efeito |
|---|---|---|---|
| B1 pressostato de funcionamento ("control pressostat") | 26.5 bar (alt. 28.5 bar) | Termina o carregamento de AQS; tem de estar fechado (=1) para arranques do compressor e da resistência de apoio | Entrada 218 [ELEC p.40, p.42], [INST p.29–30] |
| B2 pressostato de alta pressão | 31 bar | Disparo → **HIGHPRESS ERROR** | 319–320 |
| B3 pressostato de baixa pressão | 0.8 bar | Disparo → **LOWPRESS ERROR** | 321–322 |
| F11 sobrecarga (+ WSK no standard) | 9–13 A | Disparo → **MOTOR P ERROR** | 309–310 |
| T1 termóstato da resistência | 30 A | Disparo → alarme **ADD.HEATER** | fases da resistência |
| Fluxóstato FL (opção) | – | Não ativo na tentativa de arranque → **BRINEFLOW** | 217/219 |
| Sequência de fases | – | **ERR. PHASE SEQ.** (apenas no ecrã, primeiros 10 min) | – |

A AQS produzida pelo compressor pára à pressão de B1, equivalente a **≈50–55 °C** de água no depósito; não é ajustável. [USER p.9]

---

## 11. Aquecimento auxiliar e tipos de sistema de aquecimento

### 11.1 Escalões [USER p.8], [INST p.39]

MAX STEP: 0 = sem resistência de apoio, **1 = 3 kW, 2 = 6 kW (fábrica), 3 = 9 kW**. Contadores de funcionamento: ADD.HEATER = escalão de 3 kW, ADD.HEATER 2 = escalão de 6 kW. [INST p.37]

### 11.2 Sistema VL (predefinição de fábrica) [INST p.20–22]

- Resistência interna ligada; potência limitada a 3 / 6 / 9 kW (400 V).
- **VL + aquecimento externo sem shunt, >9 kW:** comando do aquecimento externo em **N + 210**; SYSTEM = VL; **deslocar o sensor de ida para depois do aquecimento externo**.
- MAX STEP definido para o valor "raio" (lightning).

### 11.3 Sistema D [INST p.20–23] (`images/INST_p023_system-D_external-heaters.png`)

- **D com outros aquecimentos externos (caldeira elétrica ou a gasóleo com shunt):** válvula shunt em **N, 215 (+), 216 (−)**; comando do aquecimento externo em **210**; sensor de ida deslocado para depois do shunt; MAX STEP = **1H** (atraso de desligação de 1 h).
- **D só com resistência elétrica externa:** desligar a resistência interna retirando as fichas de alimentação e isolando-as; comando da resistência externa em **210**; MAX STEP = "raio" (lightning).
- **Aquecimento de topo (legionella) em D:** resistência elétrica separada no depósito final em **209** via contactor K + termóstato + corte térmico; um termóstato separado define a temperatura de paragem; intervalo no menu WARMWATER; duração TOPH. TIME D (1–10 h).
- A fig. da p.23 mostra bornes externos identificados como "901 — 510" no bloco da BC junto a 209/210/215/216 (significado não explicado).

### 11.4 Resistência de apoio para AQS [INST p.30]

Normalmente não é usada para AQS, exceto (VL): resistência já ligada quando a produção de AQS começa; durante o aquecimento de topo (resistência ligada 2 min após o início do aquecimento de topo); apenas no modo ADD.HEATER. A resistência VL pára em TOPH. STOP, ou no modo ADD.HEATER em WW STOP.

---

## 12. Entrada EVU e de redução de ambiente (307–308) [INST p.24]

Imagem: `images/INST_p024_EVU-and-room-reduction.png`.

| Estado de 307–308 | Função | Ecrã |
|---|---|---|
| Aberto | Normal | – |
| **Curto-circuito (contacto fechado)** | **Bloqueio EVU** – bomba de calor, resistência de apoio **e circulador** parados enquanto fechado | **"EVU STOP"** |
| **Resistência de 10 kΩ** | **ROOM REDUCTION** (redução de ambiente) – a temperatura ambiente definida desce o valor de REDUCTION (fábrica 3 °C, 1–10 °C) | símbolo de relógio |

A entrada é SELV. **[inferência]** Um ESP32 pode comandá-la com um relé/photoMOS (contacto seco) para EVU, e com um segundo contacto em série com uma resistência de 10 kΩ para o abaixamento noturno. Nunca aplicar tensão a estes bornes.

---

## 13. Sensor de ambiente (303–304)

- Unidade de ambiente Thermia opcional (086U6003 segundo o REPO-R), SELV. Mostra o valor definido (p. ex. 20.0); +/− ajustam; ambos os botões = temperatura exterior durante 10 s; "A" em caso de alarme. [USER p.9], [INST p.19]
- ROOM FACTOR (0–4) só é mostrado quando uma unidade de ambiente está ligada; recomendação: piso radiante 1–3, radiadores 2–4. [INST p.46]
- **[comunidade]** A porta **não** é uma entrada resistiva: em repouso está a **~27 V DC** com ~1.7 kΩ em série e transporta um protocolo digital codificado por impulsos. Detalhes e um emulador em [§22](#22-protocolo-da-porta-do-sensor-de-ambiente-303304-comunidade-repo-r).

---

## 14. Fluxóstato (217–219)

Monitor opcional do caudal de água glicolada, contacto NC entre 217 (L) e 219 (entrada). Ativar com SYSTEM = VL+F / D+F. Se não estiver ativo numa tentativa de arranque → alarme **BRINEFLOW**, compressor desligado, sem AQS. O ecrã mostra "F" junto ao símbolo da BC quando instalado. [INST p.32–34, p.41], [ELEC p.40–41]

---

## 15. Lógica de controlo

### 15.1 Curva de aquecimento [INST p.36, p.44–46], [USER p.13–22]

- **CURVE** = temperatura de ida a 0 °C exterior (fábrica 40 °C, piso radiante 30 °C; gama 22–56 °C). Valor mais alto = curva mais inclinada.
- **ROOM** desloca toda a curva **3 °C de ida por 1 °C de ROOM** (deslocamento paralelo). Fábrica 20 °C (10–30). Alterações temporárias → ROOM; a longo prazo → CURVE.
- **CURVE 5 / CURVE 0 / CURVE −5:** correções locais de ±5 °C a +5, 0, −5 °C exterior; a correção de −5 atua progressivamente entre 0 e −10 °C.
- Limites **MIN / MAX** da ida. Piso radiante com parquet: ida máxima 45 °C. Piso radiante com piso de pedra: MIN 22–25 °C mesmo no verão (aumentar também HEATSTOP).
- **HEATSTOP**: aquecimento desligado quando a temperatura exterior ≥ definição (fábrica 17 °C). O circulador fica então desligado, exceto durante a produção de AQS; ciclo anti-gripagem de **1 min/dia**. [USER p.23]
- **Integral** ("graus-minuto"): (ida real − ida calculada) × tempo. Mostrado no menu TEMPERATURE (valores de exemplo −40, −660). [USER p.31]

### 15.2 Arranque / paragem do compressor [INST p.29]

Arranca quando **todas** se verificam: integral < "Integral HP" (A1) · ≥5 min desde a última paragem · STARTINTERVAL decorrido desde o último arranque · pressostato de comando fechado (=1) · exterior < heat stop.

Pára quando **qualquer** se verifica: integral > 0 °C·min · retorno ≥ MAX RETURN · exterior > heat stop.

O circulador de água glicolada arranca 30 s antes do compressor (mensagem "START"). [USER p.11] BRINETIME ON/OFF por omissão 30 s. [INST p.53]

### 15.3 Arranque / paragem da resistência de apoio [INST p.29]

Arranca quando todas: integral < Integral HP + Integral TS (A1 + A2) · ida >3 °C abaixo do valor definido · pressostato de comando fechado.
Pára quando qualquer: integral > Integral HP · ida >3 °C acima do valor definido.

### 15.4 Água quente sanitária [INST p.30, p.33, p.46–47]

- Arranque (compressor): temperatura de AQS ≤ START (fábrica 44 °C), ou até 2 °C acima de START quando o aquecimento está desligado ("reforço").
- Paragem: pressostato de comando aberto >5 s (40 s nos primeiros 2 min); ou alternância com o aquecimento segundo TIME HEAT / TIME WARMWATER (20/20 min); ou após no máx. **45 min** (depois, verificação de 5 min da necessidade de aquecimento).
- "Aquecimento de topo" anti-legionella a 65 °C a cada TOPH. INTERVAL dias (fábrica 14). [USER p.9]
- Símbolo do depósito: vazio = temperatura de arranque; cheio = temperatura no último enchimento (51 °C no arranque, máx. 54, mín. 49).

### 15.5 Modos de funcionamento [INST p.35, p.43]

OFF (alarmes repostos; drenar o aquecimento no inverno se ficar desligado) · AUTO · HEATPUMP (apenas compressor) · ADD.HEATER (apenas resistência, para colocação em serviço) · WARMWATER (apenas AQS, resistência para aquecimento de topo) · MANUAL TEST.

---

## 16. Menus, ecrã e parâmetros

### 16.1 Navegação [USER p.11–13], [INST p.31–32]

- Ecrã normal: ROOM, texto de necessidade, OPERATION. Direita/esquerda → INFORMATION (OPERATION, HEAT CURVE, [HEAT CURVE 2], TEMPERATURE, OPERATING TIME). Cima/baixo selecionam; direita abre; esquerda recua. Volta ao normal após 10 s.
- **Menu SERVICE: manter direita + esquerda durante 5 s.** [INST p.38]
- Histórico: últimos 60 min (LOGGTIME 1 min), mostrado como gráfico; não é registado durante 1 semana em caso de alarme. [INST p.37]

### 16.2 Mensagens do ecrã (vista normal) [INST p.32–33]

| Mensagem | Significado |
|---|---|
| ROOM | Temperatura desejada (definida e real com unidade de ambiente) |
| ERR. PHASE SEQ. | Sequência de fases errada (apenas nos primeiros 10 min) |
| HIGH RETURN | Retorno demasiado alto para a BC |
| HEATPUMP | Necessidade da BC |
| START | Necessidade da BC, sem atraso (pré-funcionamento de 30 s da água glicolada) |
| START_MIN | Atraso de arranque (minutos) |
| ADD.HEATER | Necessidade da resistência de apoio |
| EVU STOP | Entrada EVU fechada, tudo desligado |
| COOLING / COOLING A | Arrefecimento passivo / ativo em curso |

Símbolos: HP (F = monitor de caudal instalado, 0 = pressostato de funcionamento ativado) · raio + número de escalões · casa · arrefecimento (A = ativo) · torneira (AQS ligada) · SYSTEM (VL / D / VL+F / D+F) · relógio (redução) · depósito (+ raio = aquecimento de topo).

### 16.3 Alarmes [INST p.34, p.48–50], [USER p.29–30]

Os alarmes 1–5 repõem-se com OPERATION = OFF ou ciclo de alimentação.

| Alarme | Significado / efeito | Causas típicas |
|---|---|---|
| HIGHPRESS ERROR | Compressor desligado, sem AQS | Termóstatos do aquecimento fechados, ar no aquecimento, filtro entupido no retorno da BC, excesso de fluido frigorigéneo, circulador de aquecimento parado/lento |
| LOWPRESS ERROR | Compressor desligado, sem AQS | Pouco anticongelante/ar na água glicolada, filtro de água glicolada entupido, circulador de água glicolada parado/lento (ΔT entrada/saída deve ser 3–5 °C), gelo na água glicolada, fuga de fluido frigorigéneo, filtro desidratador entupido (ΔT máx. 2 °C) |
| MOTOR P ERROR | F11 disparou; compressor desligado | Fase ou fusível em falta, ligações soltas, tensão de rede baixa |
| BRINE OUT | Saída de água glicolada abaixo de ALARM BRINE; compressor desligado (repõe-se automaticamente quando a água glicolada aquece) | Normalmente inativo |
| BRINEFLOW | Monitor de caudal não ativo no último arranque | Caudal de água glicolada baixo |
| ADD.HEATER | T1 disparou, sem aquecimento de apoio | – |
| SENSOR OUTDOOR / SUPPLY / RETURN / WARMWATER / ROOM | Ver [§9.4](#94-comportamento-em-caso-de-falha-de-sensor-inst-p34-p50) | Cablagem/sensor |
| CIRC. PUMP* / BRINE PUMP* | Apenas Optimum: alarme integrado do circulador; repor mantendo premido o botão vermelho do circulador ≥1 s | – |
| ERR PHASE SEQ. | Compressor em sentido inverso; aquecimento só pela resistência de apoio | Trocar duas fases |
| HIGH RETURN | Retorno demasiado alto | Abrir todas as válvulas termostáticas |

### 16.4 INFORMATION → HEAT CURVE / HEAT CURVE 2 [INST p.36]

CURVE · MIN · MAX · CURVE5 · CURVE0 · CURVE-5 · HEATSTOP · REDUCTION · ROOM FACTOR (com unidade de ambiente). HEAT CURVE 2 (sensor de sub-shunt/placa de expansão): CURVE2 · MIN · MAX.

### 16.5 INFORMATION → TEMPERATURE [INST p.37]

OUTDOOR · ROOM · SUPPLYLINE real(definido) · RETURNLINE real(máx.) · WARMWATER real(arranque) · INTEGRAL · BRINE OUT · BRINE IN · COOLING real(definido) (placa de exp.) · SUBSHUNT real(definido) (placa de exp.) · CURRENT real(definido pelo fusível principal) (placa de exp.).

### 16.6 INFORMATION → OPERATING TIME [INST p.37]

HEATPUMP · ADD.HEATER (3 kW) · ADD.HEATER 2 (6 kW) · WARMWATER · COOLING (total, se houver sensor de arrefecimento) · COOLING A (se NODE > 19).

### 16.7 Menus SERVICE [INST p.38–41]

- **WARMWATER:** START (OFF = sem alarme de sensor), TIME WARMWATER, TIME HEAT, TOPH. INTERVAL (1 = constante), TOPH. STOP (VL).
- **HEATPUMP:** INTEGRAL A1, HYSTERESIS (arranque forçado), MAX RETURN, STARTINTERVAL, ALARM BRINE, SHUNT COOLING (placa de exp.; proteção contra condensação), LIQUID LINE (sensor de teste).
- **ADD.HEATER:** INTEGRAL A2, HYSTERESIS, MAX STEP, MAX CURRENT (requer placa de medição de corrente), SHUNTTIME (todos os sub-shunts), WW STOP (VL).
- **MANUAL TEST:** 0 = mostrar saídas, 1 = manual, 2 = manual com temperaturas. Saídas: HEATPUMP (arranca também o circulador de água glicolada; bloqueado durante alarme), BRINEPUMP, CIRC.PUMP, VXV WARMWATER, ADD.HEATER 3, ADD.HEATER 6, ADD.HEATER (óleo, D), SHUNT 1 (D), TOPH. WARMWATER (D), ALARM, SHUNT COOLING, SUBSHUNT, COOLING P, COOLING A, 0–10 V (as últimas seis = placa de expansão).
- **INSTALLATION 1A** (placa de controlo v1, ecrã vA): idioma, SERVICETIME (1 = integral e atrasos ×60 mais rápidos), FACTORY SET (R = radiador, G = piso), RESET OPERATE TIME, CALIBRATION SENSOR, SYSTEM (VL / D, + F), LOGGTIME, NODE (mostrado se houver interface ligada), BRINETIME ON/OFF, TOPH.TIME (3 h de aquecimento de topo ON, VL), TOPH.TIME D.

### 16.8 Definições de fábrica (completo) [INST p.51–53]

| Parâmetro | Fábrica | Mín. | Máx. |
|---|---|---|---|
| ROOM | 20 °C | 10 | 30 |
| OPERATION | AUTO (OFF na entrega) | | |
| CURVE | 40 °C (piso = 30) | 22 | 56 |
| MIN | 10 °C | 10 | 50 |
| MAX | 55 °C (piso = 45) | 40 | 70 |
| CURVE 5 / 0 / −5 | 0 °C | −5 | 5 |
| HEATSTOP | 17 °C | 0 | 40, OFF |
| REDUCTION | 3 °C | 1 | 10 |
| ROOM FACTOR | 2 | 0 | 4 |
| CURVE2 (placa de exp.) | 40 °C | 22 | 56 |
| MIN2 | 10 °C | 10 | 40 |
| MAX2 | 55 °C | 30 | 70 |
| WW START | 44 °C | OFF, 30 (placa) | 46 (placa) |
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
| CALIBRATION (cada sensor) | 0 °C | −5 | 5 |
| SYSTEM | VL | | |
| LOGGTIME | 1 min | 1 | 60 |
| NODE | 1 | 0 | 30 |
| BRINETIME ON | 30 s | 10 | 600 |
| BRINETIME OFF | 30 s | 10 | 600 |
| TOPH. TIME | OFF | OFF | ON |
| TOPH. TIME D | 1 h | 1 | 10 |

**Regra de MAX RETURN** [INST p.46]: com o sistema em aquecimento estável, retorno máximo = 55 − (ida definida − retorno definido). Exemplo: 36 − 30 = 6 → 55 − 6 = 49 °C.

### 16.9 Menu exclusivo do Optimum [INST p.42]

CIRC. DIFF (ΔT desejado do aquecimento) · BRINE DIFF (ΔT desejado da água glicolada) · FLOW RAD AUTO / 3–10 (velocidade manual) · FLOW BRINE AUTO / 3–10 · MAX HW / MIN HW (limites da ida durante a produção de AQS). Não são indicados valores de fábrica.

---

## 17. Placa de expansão Diplomat (901 515)

Imagens: `images/EXPCARD-EN_p007_wiring-901515.png`, `images/EXPCARD-086U6715_p005_EN-wiring.png`.

### 17.1 Funções [EXP1 p.3], [EXP2 p.4]

1. **Proteção de sobrecarga / limitação de potência:** 3 transformadores de corrente nas fases do grupo de fusíveis protegido; a resistência de apoio reduz escalões quando a corrente > MAX CURRENT; margem 5 A; o aumento de escalão é atrasado 1 min quando dentro da margem; o limite é reduzido 5 A temporariamente durante o arranque da BC.
2. **Arrefecimento:** passivo (furo geotérmico) ou passivo + ativo (compressor), com o módulo de arrefecimento ([§18](#18-módulo-de-arrefecimento-086u7815)).
3. **Sub-shunt / grupo de shunt:** segundo nível de temperatura com CURVE 2 (p. ex. radiadores + piso radiante). Temperatura constante: MIN = MAX.
4. **Piscina:** sensor separado; o caudal tem de passar sempre pelo sensor da piscina. Não com grupo de shunt nem com arrefecimento ativo.
5. **Alarme coletivo:** saída em qualquer alarme (EXP1: sinal de saída de 230 V, máx. 5 A; EXP2: NC/C/NO livre de potencial, máx. 230 V / 5 A).
6. **Saída 0–10 V:** para futuro controlo de frequência do compressor; não utilizada.

Montagem: placa na ranhura do compartimento elétrico, ligada com o cabo fornecido entre **Ext.COM** na unidade de controlo e Ext.COM na placa (a placa tem duas fichas Ext.COM). [EXP1 p.4], [EXP2 p.4]

### 17.2 Bornes [EXP1 p.7 desenho 54201], [EXP2 p.5]

| Borne | Função | Nível |
|---|---|---|
| 251 / 252 | Alimentação da placa 230 V – **de N1 da BC e de 217** | 230 VAC |
| 253–256 | Bloco de relés do arrefecimento passivo (253 = saída comutada, 254 N, 255 L, 256 N) | 230 VAC |
| 257 (L) / 258 (N) | Circulador de arrefecimento | 230 VAC |
| 259 (L) / 260 (N) | L / N permanentes para o módulo de arrefecimento | 230 VAC |
| 261 / 262 (N) / 263 (L) / 264 (N) | Válvula inversora do arrefecimento ativo / piscina (261 = comutado → pino 6 da válvula, 262 → pino 2, 263 → pino 3) | 230 VAC |
| 351, 352, 353 / 354 | Transformadores de corrente T1, T2, T3 / comum | – |
| 355 (−) / 356 (com) / 357 (+) / 358 (com) | Motor do shunt de arrefecimento | 24 VAC |
| 359 / 360 | Sensor do shunt de arrefecimento (branco/vermelho) | – |
| 361 (−) / 362 (com) / 363 (+) / 364 (com) | Motor do grupo de shunt 2 | 24 VAC |
| 365 / 366 | Sensor do grupo de shunt 2 / piscina (branco/vermelho) | – |
| 369 / 370 | Saída 0–10 V | – |
| NC / C / NO | Relé de alarme | ≤230 V 5 A |

**Discrepância:** EXP1 (desenho 54201) identifica **251 = N, 252 = L**, e o desenho do módulo de arrefecimento [COOL p.28–29] liga 251 (azul) → N1 e 252 (preto) → 217, o que concorda. EXP2 [p.5] identifica 251 = L, 252 = N. Verifique na própria placa antes de ligar.

### 17.3 Configuração no Duo (controlador mais antigo, baseado em NODE) [EXP1 p.5–6]

| NODE | Modo |
|---|---|
| 2–18 | Arrefecimento passivo **com** sensor de ambiente: arranque ambiente +2 °C acima do definido, paragem +0.9 °C |
| 19 | Arrefecimento passivo **sem** sensor de ambiente: sempre que exterior > HEATSTOP |
| 20 | Ativo/passivo **sem** sensor de ambiente: passivo quando exterior > HEATSTOP; ativo quando BRINE IN > valor de consigna de COOLING durante 2 min |
| 21–30 | Ativo/passivo **com** sensor de ambiente: passivo arranque +2 / paragem +0.9 °C; ativo arranque +4 / paragem +1.9 °C |
| 11 | Função piscina (temperatura da piscina e "histerese da piscina" no menu HEAT CURVE; <5 °C = desligado). Nota: 11 também cai dentro da gama 2–18 de arrefecimento passivo – o EXP1 não explica a sobreposição |

Valor de consigna do arrefecimento: SERVICE → HEATPUMP → SHUNT COOLING (fábrica 16 °C, anticondensação).

### 17.4 Menus do controlador mais recente (EXP2, para referência) [EXP2 p.4–5]

SERVICE → AUX.HEATER → MAX CURRENT; SERVICE → INSTALLATION → SYSTEM → COOLING → PASSIVE COOLING (EXTERNAL / INTEGRATED IN HP – apenas Comfort), ACT COOLING (EXTERNAL), ROOM SENSOR (OFF/ON; com sensor de ambiente arranque +2 / paragem +1, ativo +4 / +2); SYSTEM → SHUNT GROUP = ON; SYSTEM → POOL = ON. Aquecimento e arrefecimento nunca em simultâneo: arrefecimento apenas em HEAT STOP. Piscina/AQS/casa alternam a cada 20 min (AQS–Piscina–AQS–Casa–…). Estes caminhos de menu podem não existir no ecrã mais antigo do Duo; no Duo use NODE ([§17.3](#173-configuração-no-duo-controlador-mais-antigo-baseado-em-node-exp1-p56)).

---

## 18. Módulo de arrefecimento 086U7815

Imagens: `images/COOLMOD_p0*.png`.

### 18.1 Generalidades [COOL p.5]

- Duas versões: **P** (passiva) e **P/A** (passiva/ativa). P/A para necessidades de arrefecimento até **20 kW**. Montagem mural, na vertical; distância entre furos de fixação **530 mm**. Caixa ≈ 599 × 475 mm, altura 722 mm + 60 mm de tubos de ligação em cima e em baixo [COOL p.14, p.16].
- Distribuição: radiadores/ventiloconvectores ou piso radiante. O arrefecimento começa quando exterior > HEATSTOP.
- **Fase 1 passiva:** exterior > heat stop; ambiente acima do definido em ≥ ROOM FACTOR °C; ambas as condições em 5 min → o circulador de água glicolada da BC faz circular a água glicolada pelo módulo até ao furo geotérmico; o shunt do módulo mistura até à temperatura de arrefecimento definida.
- **Fase 2 ativa (apenas P/A):** condições passivas + ambiente acima do definido em 2 × room factor durante 1 min; ou entrada de água glicolada > valor definido de arrefecimento durante o passivo → ativo forçado após **120 s**. O compressor arranca; o excesso de calor vai primeiro para a AQS e depois para o furo geotérmico.

### 18.2 Ligações hidráulicas, todas Ø 28 [COOL p.14–17]

P: A saída de água glicolada · B entrada de água glicolada · H ida de arrefecimento · J retorno de arrefecimento.
P/A: A saída de água glicolada 1 · B entrada de água glicolada 1 · C saída de água glicolada 2 · D entrada de água glicolada 2 · E ida de aquecimento (para radiadores/ventiloconvectores de calor) · F ida de aquecimento vinda da BC · G retorno de aquecimento · H ida de arrefecimento · J retorno de arrefecimento.
Pressão externa disponível H–J (curva P/A, lida do gráfico): ≈51 kPa @ 0.2 l/s, 45 @ 0.3, 41 @ 0.4, ≈30 @ 0.6, ≈18 @ 0.8 l/s [COOL p.19]. Curva passiva na p.18.

### 18.3 Ligações elétricas [COOL p.28–29] **[esquema]**

Placa de expansão da BC (E2) → régua de bornes do módulo (1–9 a 230 V, 10–14 a <24 V):

| Placa | Fio | Módulo | Função |
|---|---|---|---|
| 251 | bl | N1 da BC | N da alimentação da placa |
| 252 | bk | 217 da BC | L da alimentação da placa |
| 257 | gy-257 | 8 | comando de arrefecimento passivo (circulador M1 + válvula V2 pino 6 no P) |
| 259 | gy-259 | 7 | L permanente (pinos 3 das válvulas) |
| 260 | bl-260 | 5 | N |
| 261 | gy-261 | 6 | comando de arrefecimento ativo (P/A: V2 + V3 pino 6, circulador M2 do excesso de calor) |
| PE | – | 9 | terra (PE) |
| 355 (−) | rd-355 | 13 | shunt V1 pino 3 |
| 356 (com) | wh-356 | 12 | shunt V1 pino 2 (azul) |
| 357 (+) | rd-357 | 14 | shunt V1 pino 6 |
| 359 | rd-359 | 10 | sensor de arrefecimento B1 |
| 360 | wh-360 | 11 | sensor de arrefecimento B1 |

No interior do P/A: V2 válvula inversora passivo/ativo (2 → 4, 3 → 7, 6 → 6), V3 válvula inversora de arrefecimento ativo (2 → 3, 3 → 7, 6 → 6), M1 circulador (1 → 8, 2 → 5), M2 circulador do excesso de calor (1 → 6, 2 → 5), V1 shunt 24 V (pino 2 → 12, pino 3 → 13, pino 6 → 14), sensor B1 (10/11). Os neutros das válvulas terminam em 3/4 enquanto o neutro da BC termina em 5 – a ligação 3/4/5 não está desenhada; verificar no local.

---

## 19. Ventiloconvectores (catálogo Zantia) [FAN]

Catálogo genérico, não da Thermia. Relevante para emissores de arrefecimento/aquecimento com o módulo de arrefecimento.

### 19.1 Famílias [FAN p.2]

| Tipo | Tubos | Aquecimento kW | Arrefecimento kW | Ar m³/h | Ruído dB(A) | Água arrefecimento / aquecimento |
|---|---|---|---|---|---|---|
| Centrífugo | 2 / 4 | 1.4–10.1 / 1.3–6.1 | 1.1–7.5 / 1.1–6.3 | 190–1400 | 31–54 / 31–57 | 7/12 °C / +50 (2T), +70/+60 (4T) |
| Tangencial | 2 / 4 | 1.46–6.9 / 1.2–4.4 | 1.04–5.3 / 1.04–4.2 | 190–1000 | 25–47 / 25–45 | 7/12 / +50, +70/+60 |
| Vertical | 2 | 1.6–8.8 | 0.89–6.51 | 185–1360 | 33–40 | 7/12 / 70/60 |
| Mural | 2 | 1.93–5.82 | 1.45–4.45 | 327–1020 | 23–38 | 7/12 / 70/60 |
| Cassete 4 vias | 2 / 4 | 2.67–13.20 / 2.27–7.75 | 1.84–12.89 / 2.50–10.58 | 300–2550 / 300–1330 | 39–49 / 28–47 | 7/12 / 70/60; 4T 5/27?, 50/20 (conforme impresso) |

Código do modelo (centrífugo/tangencial): `C V 1.3 2T` = tipo de ventilador (C centrífugo, T tangencial) · posição (V vertical, H horizontal – requer kit 2199.0403 –, N embutido) · modelo 1–7 (6–7 apenas centrífugo) · filas da bateria 3/4 · tubos 2T/4T. 2 tubos = aquecimento no inverno / arrefecimento no verão; 4 tubos = em simultâneo. [FAN p.2]

### 19.2 Centrífugo – elétrico e desempenho [FAN p.4–7]

- Motor monofásico de 230 V ~ 50 Hz, 4 velocidades das quais 3 ligadas, rolamentos estanques, IP21. Bateria de cobre/alumínio, ligações 1/2" (+1/8" purga/dreno), ambas à esquerda (vistas de frente). Saída da tina de condensados Ø 15 mm. Filtro lavável, 73 %.
- Potência / corrente do motor por tamanho: 1 = 53 W / 0.23 A · 2 = 64 W / 0.28 A · 3 = 79 W / 0.36 A · 4 = 98 W / 0.44 A · 5 = 170 W / 0.74 A · 6 = 190 W / 0.84 A · 7 = 310 W / 1.4 A.
- Condições de ensaio: arrefecimento ar 27 °C DB (bolbo seco) / 19 °C WB (bolbo húmido), água 7/12 °C; aquecimento ar 20 °C, água de entrada +50 °C (2T).

Desempenho a 2 tubos (velocidades 1/2/3):

| Modelo | Ar m³/h | Arrefecimento kW | Aquecimento kW | Ventilador W |
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

Limites de caudal de água, bateria de 3 filas (l/h): modelos 1–7 mín. 100/150/150/200/250/300/400, máx. 500/750/1000/1000/1500/2000/2000. Pesos 14–42 kg. [FAN p.7]

### 19.3 Comandos e válvulas [FAN p.3, p.15–20, p.31]

| Controlador | Para | ON/OFF | Velocidade | Verão/inverno | Termóstato | Corte por baixa temp. | Válvula de 3 vias |
|---|---|---|---|---|---|---|---|
| MV-3V (2199.0101) | CV (embutido) | sim | 3 manual | não | não | TMM | não |
| TMV-T (2199.0102) | CV | sim | 3 | sim | sim | TME | sim |
| MO-3V (2199.0103) | CH/NC (parede) | sim | 3 | não | não | TMM | não |
| TMO-T (2199.0104) | CH/NC | sim | 3 | sim | sim | TME | sim |
| TMO-DI (2199.0109) | CV/CH/NC | sim | manual/auto | manual/central | termóstatos do ventilador + da válvula | TME | sim |
| TMO 503-SV2 (2199.0110) | CV/CH/NC | sim | manual/auto | manual | termóstato da válvula | TME | sim |

- O TMV-T no verão, com o seletor do ventilador em OFF, faz funcionar o ventilador 2 min em cada 15 min.
- Repetidor (2199.0106 CV / 2199.0107 CH/NC): até 8 ventiloconvectores a partir de um termóstato TMO-T.
- **TMM** (2199.0202): pára o ventilador abaixo de 32 °C de água primária, rearranca acima de 42 °C (MV-3V/MO-3V). **TME** (2199.0201): pára abaixo de 38 °C, rearranca acima de 42 °C (TMV-T/TMO-T). Change-over 15-25 (2199.0204): verão/inverno automático pela entrada de água (2 tubos, TMO-T/TMO-DI).
- Válvulas: VBP 1-3 (1/2", DN15, 2199.0401), VBP 4-7 (3/4", DN20, 2199.0402) para 2 tubos; VBA 1-7 (2199.0404) para 4 tubos; apenas com TMV-T/TMO-T.
- Válvula de zona de 3 vias série 22C (1605.0211, 3/4", 16 bar, 4–110 °C) + **cabeça eletrotérmica 230 V NC (1906.0306)**: atuador de cera, 140 N, abertura/fecho 90/180 s, 2.5 W, contacto auxiliar 700 W.
- Zantia vertical (2101.0301–0308): 230 V ~ 50 Hz, centrífugo de 3 velocidades com proteção térmica; termóstato digital 2199.0203: aquecer/arrefecer/ventilador, 3 velocidades, 17–32 °C, comanda uma válvula de 3 vias opcional, funções anti-ar frio (o ventilador pára quando a bateria <35 °C) e anti-ar quente (impresso "bateria >20 °C"). Dreno de condensados necessário apenas para arrefecimento. [FAN p.22–24]
- Unidades murais (2102.0401–0405): válvula de 3 vias, telecomando IV e ecrã incluídos. Cassetes: grelha, telecomando e bomba de condensados (elevação de 0.75 m) incluídos; opcionais: telecomando com fios CZFI 1, central CZFC 1 (64 unidades), módulos de rede, módulo de contacto seco. [FAN p.25–32]

**[inferência]** Integração: as potências de arrefecimento do catálogo são para água a 7/12 °C. Com o módulo de arrefecimento da Thermia, a ida é misturada (shunt) até SHUNT COOLING (fábrica 16 °C, para evitar condensação), pelo que a capacidade real é muito inferior. Ventiladores, válvulas e change-over podem ser comutados por relés do ESP32 (230 V, usar relés/contactores dimensionados), usando o estado de arrefecimento ativo da bomba (bits de r11, [§21.5](#215-mapa-de-registos)) como intertravamento.

---

## 20. Visão geral da integração com o ESP32

| Via | Bornes / conector | Sentido | O que fornece | Risco |
|---|---|---|---|---|
| **A. Barramento EXT (escravo I2C 0x2E)** | Conector EXT em E1 (GND, SDA, SCL, 5 V) | leitura + escrita | Todas as temperaturas, estados, alarmes, contadores; escrita de valores de consigna, modo, curva, AQS, MAX STEP, … | baixo com conversor de nível; escritas sem confirmação |
| **B. Emulação do sensor de ambiente** | 303 / 304 | ESP → bomba | Temperatura ambiente real + valor de consigna de ambiente (0.5 °C) | requer photoMOS; nunca ligar diretamente |
| **C. EVU / redução** | 307 / 308 | ESP → bomba | Bloqueio (EVU STOP) ou abaixamento noturno (10 kΩ) | apenas contacto seco |
| **D. Medição de corrente** | TC nas fases | ESP | Potência/energia (também r0C da placa de expansão) | instalação no lado da rede por eletricista |
| **E. Deteção de estado das saídas de 230 V** | 211, 212, 213, 214, 209, 210, 215, 216 | ESP lê | Redundante com os bits de r10/r11 | apenas detetores de 230 V isolados |
| **F. Sensores próprios** | NTC/DS18B20 separados | ESP | Temperaturas adicionais (depósito, circuitos de piso radiante) | – |

Evitar: comandar diretamente os relés ou saídas da bomba, contornar B1/B2/B3/F11/T1, ligar em paralelo às linhas dos sensores, ou comutar o compressor/resistência a partir do exterior do controlador.

---

## 21. Porta EXT – protocolo do barramento I2C [comunidade, REPO-T]

### 21.1 Hardware

- Conector EXT de 4 pinos, da esquerda para a direita **GND, SDA, SCL, 5 V** (verificar na sua placa). Junto à ficha RJ45 do ecrã, na aresta superior da placa do Duo. (`images/REPO_esphome-thermia_ext-port-pinout.jpg`)
- **Barramento de 5 V** com as resistências pull-up da própria bomba → usar um conversor de nível bidirecional (tipo BSS138). Ligar apenas GND, SDA, SCL; alimentar o ESP em separado. Ligar com a bomba desligada.
- ESP32: apenas GPIO0–31, evitar os pinos de strapping (0, 2, 5, 12, 15) e os pinos de flash; GPIO21/22 funcionam bem. O REPO-T foi testado numa **Thermia Duo 400 V 10 kW** com um Wemos D1 mini e um ESP32-S3 (o exemplo combinado do REPO-R usa SDA GPIO12 / SCL GPIO11).
- **Não** declarar um bloco `i2c:` do ESPHome: a bomba é o master.
- **[inferência]** O "Ext. COM" de E1 (desenho) e o conector EXT são muito provavelmente a mesma porta usada pela placa de expansão (a bomba também interroga os endereços 0x32 e 0x37). Se instalar uma placa de expansão, o barramento é partilhado.

### 21.2 Protocolo

- Bomba = master I2C, ~20 kHz; acessório = escravo no endereço de 7 bits **0x2E**.
- A bomba escreve um **ping** `0xFE` (`0xFD` após o seu próprio arranque).
- A bomba lê depois **um byte** do escravo: `0xFF` = nada; `0x00–0x7F` = "envia-me o registo N"; ou 3 bytes `[reg | 0x80, lo, hi]` = **escrever** valor no registo.
- Após um pedido de registo, a bomba escreve uma trama de dados `[reg, lo, hi]` – **int16 com sinal, little-endian**.
- Exemplo: `S 5C FE P` (ping) → `S 5D [06] P` (pede r06) → `S 5C 06 18 00 P` (r06 = 24 °C).
- Sem confirmação de escrita: ler o registo depois de escrever. Alguns registos (r00, r01, r32, r34) respondem apenas raramente (até minutos); r10 não é respondido enquanto o compressor está parado.
- Implementação do REPO-T: interrupção GPIO na transição descendente de SDA, busy-poll em IRAM até STOP; tempos-limite de 1.5 ms por transição e 8 ms por transação; disjuntor lógico (circuit breaker) após 50 transações falhadas; plausibilidade −60…200 °C; bus gate (ligar 5 s depois de o Wi-Fi estar ativo). O escravo I2C por hardware do ESP32 não é usado porque a resposta depende do ping anterior.

### 21.3 Configuração do esphome-thermia

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

Opções: `debug_frames`, `sniff` (formas de onda em bruto, desativa o protocolo), `selftest`, `link`, `card_map`, `registers:` genérico (leitura 0x00–0x7F, escala, com sinal) e `set_registers:` (escrita; mín./máx. obrigatórios).

### 21.4 Diagnóstico [REPO-T]

`pings=0, isr=0` → não ligado · `isr` cresce, `pings=0` → SDA/SCL trocados · `pings` cresce, `data=0` → a bomba não envia registos · `err` cresce com os pings → ISR demasiado lenta · `unanswered` cresce → normal para alguns registos · `foreign` cresce → normal (0x32, 0x37).

### 21.5 Mapa de registos

Fonte: mapa TIQ, usado pelo REPO-T. ✅ = confirmado num Duo real pelo REPO-T; os restantes provêm do mapa ThermIQ. A coluna "Menu" = o meu mapeamento para o parâmetro do menu do Duo **[inferência]**, com base no nome, unidade e gama.

**Medições (só de leitura)**

| Reg | Nome (TIQ) | Unidade | Significado | Menu / hardware |
|---|---|---|---|---|
| r00 | outdoor_t | °C | Exterior | TEMPERATURE→OUTDOOR (305/306) |
| r01 / r02 | indoor_t / indoor_dec_t | °C / 0.1 | Interior (virtual ou unidade de ambiente), inteiro + décimas | ROOM |
| r03 / r04 | indoor_target_t / dec | °C / 0.1 | Valor de consigna interior em uso | – |
| r05 | supplyline_t | °C | Ida (T1) | B4 301/302 |
| r06 | returnline_t | °C | Retorno (T2) | B6 |
| r07 | boiler_t | °C | Depósito de AQS (T3) | 311/312 |
| r08 | brine_out_t | °C | Saída de água glicolada | B7 |
| r09 | brine_in_t | °C | Entrada de água glicolada | B8 |
| r0A | cooling_t | °C | Arrefecimento | placa de exp. 359/360 |
| r0B | supply_shunt_t | °C | Ida do sub-shunt | placa de exp. 365/366 |
| r0C | current_consumed_a | A | Corrente medida | TC da placa de exp. |
| r0D bit 0x01 / 0x02 | boiler_3kw_on / boiler_6kw_on | – | Relé de apoio 3 kW / 6 kW | E1 3KW / 6KW |
| r0E | supplyline_target_t | °C | Valor de consigna da ida | SUPPLYLINE (definido) |
| r0F | supplyline_shunt_target_t | °C | Valor de consigna do sub-shunt | – |
| r10 bits | 0x01 circulador de água glicolada · 0x02 compressor · 0x04 circulador de ida · 0x08 produção de AQS · 0x10 apoio2 · 0x20 shunt1 − · 0x40 shunt1 + · 0x80 apoio1 | – | Estados das saídas | 211 · 212 · 213 · 214 · – · 216 · 215 · – |
| r11 bits | 0x01 shunt2 − · 0x02 shunt2 + · 0x04 shunt de arrefecimento − · 0x08 shunt de arrefecimento + · 0x10 arrefecimento ativo · 0x20 arrefecimento passivo · 0x40 alarme | – | Saídas da placa de exp. + alarme coletivo | 361/363 · 355/357 · 261 · 253/257 |
| r12 | pwm_out_period | % | Saída PWM | – |
| r13 bits | 0x01 alta pressão · 0x02 baixa pressão · 0x04 disjuntor do motor · 0x08 caudal de água glicolada · 0x10 temperatura da água glicolada | – | Alarmes | B2 · B3 · F11 · FL · ALARM BRINE |
| r14 bits | 0x01 exterior · 0x02 ida · 0x04 retorno · 0x08 AQS · 0x10 sensor interior · 0x20 ordem das fases · 0x40 sobreaquecimento | – | Alarmes | sensores · ERR PHASE · T1 |
| r15 / r16 | demand1 / demand2 | – | Necessidade | – |
| r17 | pressurepipe_t | °C | Descarga (gás quente) | B9 323/324 |
| r18 | hgw_water_t | °C | Linha de ida da AQS | (opção HGW) |
| r19 | integral1 | °C·min | Integral A1 | TEMPERATURE→INTEGRAL |
| r1A | integral1_a_step | – | Integral, limite A atingido | – |
| r1B | defrost_time_m | ×10 s | Descongelação | (n/a para água glicolada) |
| r1C | time_to_start_min_m | min | Tempo mínimo até ao arranque | START_MIN |
| r1D | sw_version | – | Versão do programa | – |
| r1E / r1F | supply / brine pump speed | % | Velocidades dos circuladores | Optimum 0–10 V |
| r20 | status3_m | – | Estado | – |
| r68 / r6A / r6C / r6E / r70 / r72 | runtimes | h | Compressor / 3 kW / AQS / arrefecimento passivo / arrefecimento ativo / 6 kW | OPERATING TIME |
| r69 / r6B / r6D / r6F / r71 / r73 | msd1_* | – | Contadores de funcionamento alternativos (s) | – |
| r74 | graph_display_offset | – | – | – |

**Definições (leitura/escrita)**

| Reg | Nome (TIQ) | Gama TIQ | Menu do Duo (fábrica, mín.–máx.) | REPO-T |
|---|---|---|---|---|
| r32 | indoor_requested_t | 0–50 °C | ROOM (20, 10–30) | ✅ |
| r33 | main_mode | 0–16 | OPERATION: 0 Off, 1 Auto, 2 Heatpump only, 3 Heater only, 4 Hot water only (5–16 não documentados) | ✅ |
| r34 | integral1_curve_slope | 0–200 | CURVE (40, 22–56) | gama do menu |
| r35 / r36 | curve min / max | 0–200 °C | MIN (10, 10–50) / MAX (55, 40–70) | |
| r37 / r38 / r39 | curve +5 / 0 / −5 | −5…5 | CURVE 5 / 0 / −5 | |
| r3A | heating_stop_t | 0–200 | HEATSTOP (17, 0–40) | |
| r3B | reduction_t | 0–100 | REDUCTION (3, 1–10) | |
| r3C | room_factor | 0–4 | ROOM FACTOR (2) | |
| r3D / r3E / r3F | curve 2 slope / min / max | 0–200 | CURVE2 / MIN2 / MAX2 | |
| r40 / r41 | curve 2 target / actual | 0–200 | SUBSHUNT definido / real | |
| r42 | outdoor_stop_t | 0–100 | "(20 = −20 °C)", sinal invertido? – omitido pelo REPO-T | |
| r43 | pressure_pipe_limit_t | 0–200 | limite da temperatura de descarga (não consta do manual do Duo) | |
| r44 | hotwater_start_t | 0–100 | WW START (44) | |
| r45 | hotwater_runtime_m | min | TIME WARMWATER (20, 5–40) | |
| r46 | heatpump_runtime_m | min | TIME HEAT (20, 5–40) | |
| r47 | legionella_interval_d | dias | TOPH. INTERVAL (14) | |
| r48 | legionella_stop_t | 0–100 | TOPH. STOP (65) | |
| r49 | integral1_a_limit | °C·min | INTEGRAL A1 (60, 5–99) – escala por verificar | |
| r4A | integral1_hysteresis_t | 0–100 | HYSTERESIS HP (7) | |
| r4B | returnline_max_t | 0–100 | MAX RETURN (48) | |
| r4C | start_interval_min_m | min | STARTINTERVAL (20) | |
| r4D | brine_min_t | −25…100 (−15 = OFF) | ALARM BRINE (OFF, −14…10) | |
| r4E | cooling_target_t | 0–50 | SHUNT COOLING (16) | |
| r4F | integral2_a_limit | ×10 °C·min | INTEGRAL A2 (600) – o registo é provavelmente 60 | |
| r50 | integral2_hysteresis_t | 0–100 | HYSTERESIS AH (15) | |
| r51 | elect_boiler_steps_max | 0–3 | MAX STEP (2) | |
| r52 | current_consumption_max_a | A | MAX CURRENT (20) | |
| r53 | shunt_time_s | s | SHUNTTIME (60) | |
| r54 | hotwater_stop_t | 0–100 | WW STOP (65) | |
| r55 | manual_test_mode_on | – | MANUAL TEST | leitura |
| r56 / r58 | status7 (DT_LARMOFF) / status8 (SERVFAS) | – | – | leitura |
| r57 | language | 0–255 | idioma | |
| r59 / r5A | factory reset / reset runtime counters | – | FACTORY SET / RESET OPERATE TIME | não exposto (perigoso) |
| r5B…r60 | desvios de sensor: exterior, ida, retorno, AQS, entrada de água glicolada, saída de água glicolada | −5…5 | CALIBRATION SENSOR (o TIQ identifica r5F/r60 como "brine out"/"brine in" – provavelmente trocados) | |
| r61 | heatingsystem_type | 0 = VL, 4 = D | SYSTEM | |
| r62 bits | 0x01 phase-measure · 0x02 opt2 · 0x04 HGW · 0x08/0x10/0x20 opt4–6 · 0x40 Optimum · 0x80 fluxóstato | – | opções instaladas | leitura |
| r63 | internal_logging_t | min | LOGGTIME (1) | |
| r64 / r65 | brine run-out / run-in | ×10 s | BRINETIME OFF / ON (30 s = 3) | |
| r66 | legionella_run_on | 0/1 | TOPH. TIME (OFF) | |
| r67 | legionella_run_length_h | h | TOPH. TIME D (1) | |

O REPO-T expõe: r32, r33 (select), r34–r39, r3A, r3C, r44, r54, r51, r52; tudo o resto através de `registers:` / `set_registers:` com os seus próprios mín./máx. **A escrita em r01 (temperatura interior) é ignorada pela bomba.** Alterar uma definição de cada vez, com o ecrã à mão.

---

## 22. Protocolo da porta do sensor de ambiente (303–304) [comunidade, REPO-R]

- A linha está em repouso a **~27 V DC**, ~1.7 kΩ em série do lado da bomba. Um impulso = carga na linha (1.1 kΩ 1 W puxa-a para ~10 V).
- Circuito de referência: GPIO do ESP32 → 220 Ω → **photoMOS Toshiba TLP241A** (DIP-4, 40 V, isolado) → 1.1 kΩ 1 W entre 303/304; TVS P6KE33CA opcional. O ESP mantém a sua própria alimentação. (`images/REPO_esphome-thermia-room_wiring.svg`)
- **Codificação por distância entre impulsos:** cada bit = intervalo em repouso + impulso de **60 ms**; intervalo ≈ **82 ms → raw 1**, ≈ **388 ms → raw 0**. Bit lógico = NOT do bit raw; campos com LSB primeiro.
- **Trama (29 bits, 6–9 s):** start(1) | valor de consigna × 2 (8 bits, 0.5 °C) | °C inteiros (8) | décimas (4) | checksum (5) | cauda `011` (3). Tramas separadas por **2–4 s** de repouso (a bomba sincroniza-se por aí).
- **Checksum** = (inteiro XOR décimas XOR valor de consigna×2) AND 31. As tramas inválidas são descartadas em silêncio.
- Gamas: ambiente 0.0–31.9 °C; trama de valor de consigna 5–35 °C; a bomba gera alarme de sensor de ambiente abaixo de 16 °C.
- Comportamento da bomba: com tramas válidas e ROOM FACTOR 1–4, usa o valor de consigna (r03/r04) e a temperatura ambiente (r01/r02). Sem tramas → alarme do sensor de ambiente (bit 0x10 de r14) → recorre a r32. ROOM FACTOR 0 → sensor de ambiente ignorado, usa-se r32, sem alarme.
- Família compatível: Diplomat, Diplomat Optimum, Duo, Legend; Danfoss DHP-H/C/L. Requer um ESP32 (periférico RMT).

Exemplos: ambiente 20.5 / consigna 21.0 → raw `1|10101011|11010111|0101|00100|011`; ambiente 22.4 / consigna 21.5 → `1|00101011|10010111|1101|01100|011`.

---

## 23. Esboço de hardware ESP32 recomendado **[inferência]**

1. **Barramento EXT:** conversor de nível BSS138 (lado de 5 V a partir da referência de 5 V da bomba, lado de 3.3 V a partir do ESP), SDA/SCL em GPIO0–31, cabo curto blindado, apenas GND comum.
2. **Sensor de ambiente:** TLP241A + 1.1 kΩ 1 W + TVS em 303/304, como em [§22](#22-protocolo-da-porta-do-sensor-de-ambiente-303304-comunidade-repo-r).
3. **EVU / redução:** dois pequenos relés ou photoMOS: o contacto 1 curto-circuita 307-308 (EVU), o contacto 2 coloca 10 kΩ entre 307-308 (redução). Intertravamento no firmware para que nunca estejam ambos ligados em simultâneo.
4. **Monitorização de potência:** 3 TC de núcleo bipartido nas fases de entrada ou um contador de energia externo (Modbus); trabalhos na rede por um eletricista.
5. **Alimentação:** fonte de 5 V para calha DIN separada para o ESP. Manter a cablagem de baixa tensão a ≥25 cm dos cabos de rede ([§4.1](#41-requisitos-de-alimentação-inst-p15-elec-p2)).
6. **Falha segura:** se o ESP falhar, a bomba tem de funcionar normalmente → a perda da emulação do sensor de ambiente faz a bomba usar r32 (manter r32 com um valor sensato); o contacto EVU tem de ser normalmente aberto.

---

## 24. Pontos em aberto a verificar na sua unidade

1. Standard (desenho 56960) ou Optimum (57156)? Verificar os circuladores (ligação 0–10 V em 327–334) e a placa de características.
2. Arrancador suave R1 ou contactor K1 (quadro 53369-A / 55527-B)?
3. Pontes em X1: 3L1–2L1 e 1Lx–2Lx presentes?
4. Placa de expansão instalada? Se sim, Ext.COM/EXT já está em uso – planear uma ligação partilhada; verificar a identificação de 251/252.
5. Ordem dos pinos do conector EXT (GND, SDA, SCL, 5 V) com um multímetro antes de ligar.
6. Escala dos registos de INTEGRAL A1/A2 (r49, r4F) – lê-los e comparar com o ecrã antes de escrever.
7. Ligação do neutro nos bornes 3/4/5 do módulo de arrefecimento.
8. Valores atuais de MAX STEP, SYSTEM (VL/D) e NODE no ecrã.

---

## 25. Glossário

| Termo | Significado |
|---|---|
| VL | Sistema com resistência elétrica interna (de fábrica) |
| D | Sistema com aquecimento/caldeira externa (shunt) |
| F | Fluxóstato instalado (VL+F, D+F) |
| EVU | Elektrizitäts-Versorgungs-Unternehmen (empresa distribuidora de eletricidade) – entrada de bloqueio da distribuidora |
| VXV | Växelventil (sueco) – válvula desviadora (AQS) |
| TRYCKRÖR | Sueco "tubo de pressão" = sensor de descarga do compressor |
| TOPP TWS | Sensor de topo da AQS |
| WSK | Wicklungsschutzkontakt (alemão) – contacto térmico de proteção do enrolamento do circulador |
| HGW | Hot gas water (água de gás quente) (opção) |
| A1 / A2 | Limites do integral para o compressor / resistência de apoio |
| Aquecimento de topo (TOPH) | Aquecimento anti-legionella do depósito |
| Sub-shunt / grupo de shunt | Segundo circuito de mistura com curva própria (CURVE 2) |
| NODE | Número de endereço/modo; no Duo seleciona também o modo de arrefecimento e a piscina |
| HUONE | Finlandês "divisão/ambiente" – o valor de consigna de ambiente da própria bomba (r32) na documentação da comunidade |
| Salmoura / fluido de captação / água refrigerada | O mesmo circuito (água glicolada do circuito enterrado), traduções diferentes |

---

## 26. Conflitos e peculiaridades nos documentos

- A identificação N/L de 251/252 da placa de expansão difere entre EXP1 e EXP2 ([§17.2](#172-bornes-exp1-p7-desenho-54201-exp2-p5)).
- EXP1 diz que o alarme coletivo "envia uma saída de 230 V", EXP2 descreve um contacto livre de potencial; os desenhos mostram um relé NC/C/NO.
- Histerese de paragem do sensor de ambiente: EXP1 0.9 / 1.9 °C, EXP2 1 / 2 °C.
- [INST p.20] (texto de 230 V) indica escalões da resistência de 1.5/3/4.5 kW; [INST p.21–22] (texto de 400 V) indica 3/6/9 kW – o segundo aplica-se ao Duo 12 de 400 V.
- [INST p.37] fala de histórico num "selected time interval" (intervalo de tempo selecionado); [USER p.15] diz últimos 60 minutos (LOGGTIME 1 min × tamanho do buffer).
- O exemplo de curva de aquecimento do USER mostra "MIN 22 °C, MAX 70 °C" no ecrã, enquanto MIN de fábrica é 10 °C e MAX 55 °C [USER p.14 vs INST p.51].
- O TIQ identifica r5F/r60 como brine out/in embora as chaves digam brine_in/brine_out.
- Neutro de entrada: o ELEC p.41 liga-o ao **N3**, o INST p.16 fig. 8 ao **N2**. N2/N3/N1b estão ligados internamente [ELEC p.39], pelo que ambos funcionam eletricamente.
- O NODE 11 (piscina) sobrepõe-se à gama NODE 2–18 de arrefecimento passivo no EXP1 [§17.3](#173-configuração-no-duo-controlador-mais-antigo-baseado-em-node-exp1-p56).

---

## 27. Índice de imagens

| Ficheiro | Origem | Conteúdo |
|---|---|---|
| `ELEC_p002_reference-explanation.png` | ELEC p.2 | Como ler as referências cruzadas folha/linha/coluna; regras gerais |
| `ELEC_p039_Duo12-400V_sheet1_power-circuit.png` | ELEC p.39 (impressa 37) | Circuito de potência: X1, compressor, circuladores, válvula, resistência |
| `ELEC_p040_Duo12-400V_sheet2_control-unit-E1.png` | ELEC p.40 (impressa 38) | Bornes de E1 1–8, 209–220, 301–326 |
| `ELEC_p041_Duo12-400V_sheet3_external-connections.png` | ELEC p.41 (impressa 39) | Bornes de campo |
| `ELEC_p042_Duo12-400V_sheet4_parts-list.png` | ELEC p.42 (impressa 40) | Lista de peças |
| `ELEC_p102…p107_Duo12-Optimum_*.png` | ELEC p.102–107 (impressas 100–105) | Folhas 1–5 do Optimum (p.105 e p.106 são duas versões da folha de ligações externas) |
| `INST_p008_connection-dimensions.png` | INST p.8 | Ligações hidráulicas |
| `INST_p011/p012_hydraulic-system-*.png` | INST p.11–12 | Sistema VL / D |
| `INST_p013_heat-pump-components.png` | INST p.13 | Componentes |
| `INST_p014_outdoor-sensor_NTC-tables.png` | INST p.14 | Tabelas de sensores |
| `INST_p016_fig8_electrical-connections.png` | INST p.16 | Fig. 8 |
| `INST_p017/p018_electrical-cubicle-*.png` | INST p.17–18 | Disposição dos quadros |
| `INST_p021_fig9_control-and-sensor-connections.png` | INST p.21 | Fig. 9 |
| `INST_p023_system-D_external-heaters.png` | INST p.23 | Ligações do sistema D |
| `INST_p024_EVU-and-room-reduction.png` | INST p.24 | EVU / 10 kΩ |
| `INST_p026_brine-filling.png` | INST p.26 | Enchimento de água glicolada |
| `INST_p027_phase-rotation-check.png` | INST p.27 | Verificação de fases |
| `INST_p055_tech-specs-400V.png` | INST p.55 | Especificações |
| `EXPCARD-EN_p004_connection-overload.png` | EXP1 p.4 | Montagem da placa, sobrecarga |
| `EXPCARD-EN_p007_wiring-901515.png` | EXP1 p.7 | Ligações da placa 54201 EN |
| `EXPCARD-086U6715_p004_EN-text-fig1.png`, `…p005_EN-wiring.png` | EXP2 p.4–5 | Instruções da placa mais recente, ligações |
| `COOLMOD_p014/p016_*` | COOL p.14, 16 | Dimensões do módulo, ligações hidráulicas |
| `COOLMOD_p018/p019_*` | COOL p.18–19 | Curvas de pressão |
| `COOLMOD_p020/p022/p024_*` | COOL p.20, 22, 24 | Modos de aquecimento / passivo / ativo |
| `COOLMOD_p028/p029_*` | COOL p.28–29 | Ligações elétricas do módulo |
| `FANCOIL_p006–p008_*` | FAN p.6–8 | Dimensões e instalação do ventiloconvector |
| `REPO_esphome-thermia_ext-port-pinout.jpg` | REPO-T | Fotografia do conector EXT |
| `REPO_esphome-thermia-room_*.svg` | REPO-R | Ligações do sensor de ambiente, temporização, estrutura da trama |
