# Items & Crafting System (D&D 5e)

[English](README.md) | [Português (Brasil)](README.pt-BR.md)

[![Foundry VTT](https://img.shields.io/badge/Foundry%20VTT-v12%20|%20v14-orange.svg)](https://foundryvtt.com/)
[![System](https://img.shields.io/badge/System-dnd5e%20v3.0%2B-blue.svg)](https://github.com/foundryvtt/dnd5e)
[![Version](https://img.shields.io/badge/version-v1.2.0-blue.svg)](module.json)
[![Tests](https://img.shields.io/badge/tests-26%20passed-brightgreen.svg)](tests/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A complete crafting, alchemy, enchanting, foraging, and creature harvesting module for **Foundry Virtual Tabletop (V12 to V14+)** and **D&D 5e (v3.0+ and v4.0+)**, faithfully implementing the mechanics of the acclaimed **Kibbles' Crafting Guide** with interactive ApplicationV2 sheets and bilingual compendiums.

---

## Highlights

- **Interactive Crafting Workshop (ApplicationV2):** Modern, reactive interface accessible from character sheets or toolbars with real-time recipe search and focus preservation.
- **Automated Creature Harvesting:** Automatic Challenge Rating (CR) detection and creature type mapping (Dragons, Beasts, Constructs, Aberrations, Undead, Celestials) with skill-based salvage checks.
- **Foraging and Scavenging Hub:** Biome foraging tables (Forest, Mountain, Swamp, Desert, Underdark, Coastal, Plains), item breakdown tables, and Quantum Chaos Box integration.
- **Bilingual Compendium Parity:** Full dual-language data (`en` and `pt-BR`) covering 478 recipes, 478 final items, 92 materials, 15 roll tables, and comprehensive rule journals.
- **Foundry V12-V14 Modernized:** Native `ChatMessage` construction using modern `style` flags with backwards-compatible fallbacks and zero console deprecation warnings.
- **Automated Test Suite:** Robust unit testing suite with 26 automated tests verifying domain calculations, UI state handling, icon validity, and pack integrity.

---

## Domain and Feature Tables

### Crafting Professions

| Profession | Associated Tool / Skill | Key Abilities | Primary Output |
| :--- | :--- | :--- | :--- |
| **Alchemy** | Alchemist's Supplies / Herbalism Kit | INT / WIS | Potions, elixirs, acids, alchemical fire, and draughts |
| **Blacksmithing** | Smith's Tools | STR / CON | Metal weapons, heavy armors, shields, and reinforced gear |
| **Enchanting** | Arcana Skill | INT / CHA | Magic item attunements, essences infusion, and arcane relics |
| **Leatherworking** | Leatherworker's Tools | DEX / STR | Leather and hide armors, quivers, boots, and reinforced hides |
| **Poisoncraft** | Poisoner's Kit | INT / DEX | Contact, ingested, inhaled, and injury toxins |
| **Scroll Scribing** | Calligrapher's Supplies | INT / WIS | Spell scrolls, ritual sheets, and magical parchment |
| **Tinkering** | Tinker's Tools | INT / DEX | Clockwork devices, traps, mechanical contraptions, and gadgets |
| **Wand Whittling** | Woodcarver's Tools | INT / WIS | Spellcasting wands, staves, and wooden foci |
| **Cooking** | Cook's Utensils | WIS / CON | Rations, hearty feasts, and temporary vitality meals |

### Bilingual Compendiums

| Pack Key | Document Type | Entries | Description |
| :--- | :--- | :---: | :--- |
| `crafting-items` | `Item` | 478 | Final craftable items with mechanical D&D 5e attributes and values |
| `crafting-materials` | `Item` | 92 | Fundamental reagents, metal ingots, beast essences, hides, and parts |
| `crafting-recipes` | `Item` | 478 | Structured recipes with required materials, tool DCs, and crafting times |
| `crafting-tables` | `RollTable` | 15 | Harvesting tables by creature type/CR, biome foraging, and salvaging |
| `crafting-rules` | `JournalEntry` | 14 | Official guide chapters covering resting, metallurgy alloys, and mechanics |

---

## Architecture and Interfaces

- **`CraftingWorkshopApp` (`ApplicationV2`):** Tabbed interface handling active profession switches, reactive recipe filtering by search query (`filterRecipesBySearch`), inventory material reconciliation (`checkMaterials`), and 2-hour crafting progress progression.
- **`HarvestingApp` (`ApplicationV2`):** Creature harvesting dialog providing automatic target token inspection, CR-to-DC table lookup (`getTableAndDC`), and direct ingredient distribution to player inventory.
- **`CraftingEngine` & `HarvestingEngine`:** Pure domain logic layer computing tool proficiencies, ability modifiers, roll bonuses, and chat payload assembly (`buildChatMessageData`).

---

## Installation

Install directly within the Foundry VTT Setup menu using the manifest link:

```text
https://raw.githubusercontent.com/NeroHeiser/itensdnd/main/module.json
```

Or extract the zip package into your Foundry user data directory:
```text
<FoundryData>/Data/modules/itensdnd
```

---

## Automated Testing and Quality

The module features native unit tests powered by the Node.js test runner:

```bash
# Run the complete test suite
npm test
```

Validation guarantees:
- **Domain calculations:** Verifies material aggregation, modifier calculation, and CR-to-DC tables.
- **Data integrity:** Asserts physical existence of all 5 pack directories, valid 16-character IDs, and symmetric `en`/`pt-BR` key structures.
- **Compatibility:** Verifies modern Foundry V12-V14 `ChatMessage` styling and FontAwesome Free icon compatibility.

---

## Compatibility and License

- **Foundry VTT:** Verified for v12 and v14.
- **System:** `dnd5e` v3.0+ and v4.0+.
- **Game Design:** Based on the **Kibbles' Crafting Guide** by KibblesTasty.
- **Module Author:** [André Luiz (Lopes / NeroHeiser)](https://github.com/NeroHeiser).
- **License:** [MIT](LICENSE).
