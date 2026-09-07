#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
import-kibbles-full.py
Processa e integra os arquivos completos da extração do Kibbles' Crafting Guide:
- foundry-materials.json (70 materiais)
- foundry-items.json (479 receitas)
Normaliza IDs para formato Foundry (16 caracteres alfanuméricos determinísticos),
atribui ícones temáticos, mapeia materiais canônicos e cria os compêndios bilíngues (pt-BR e en).
"""

import json
import hashlib
import os
import re
import sys

def make_id(key: str) -> str:
    """Gera um ID alfanumérico determinístico de 16 caracteres compatível com Foundry VTT."""
    h = hashlib.md5(key.encode('utf-8')).hexdigest()
    return h[:16]

SOURCE_DIR = "/run/media/lopes/Hd interno/RPG/itens/Crafting+PDF+(Free)-Foundry-JSON"
DEST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# Mapeamento canônico de ingredientes
CANONICAL_KEYS = {
    "common curative reagent": "reagent-curative-common",
    "uncommon curative reagent": "reagent-curative-uncommon",
    "rare curative reagent": "reagent-curative-rare",
    "very rare curative reagent": "reagent-curative-very-rare",
    "legendary curative reagent": "reagent-curative-legendary",
    "common poisonous reagent": "reagent-poisonous-common",
    "uncommon poisonous reagent": "reagent-poisonous-uncommon",
    "rare poisonous reagent": "reagent-poisonous-rare",
    "very rare poisonous reagent": "reagent-poisonous-very-rare",
    "legendary poisonous reagent": "reagent-poisonous-legendary",
    "common reactive reagent": "reagent-reactive-common",
    "uncommon reactive reagent": "reagent-reactive-uncommon",
    "rare reactive reagent": "reagent-reactive-rare",
    "very rare reactive reagent": "reagent-reactive-very-rare",
    "legendary reactive reagent": "reagent-reactive-legendary",
    "common arcane essence": "essence-arcane-common",
    "uncommon arcane essence": "essence-arcane-uncommon",
    "rare arcane essence": "essence-arcane-rare",
    "very rare arcane essence": "essence-arcane-very-rare",
    "legendary arcane essence": "essence-arcane-legendary",
    "common divine essence": "essence-divine-common",
    "uncommon divine essence": "essence-divine-uncommon",
    "rare divine essence": "essence-divine-rare",
    "very rare divine essence": "essence-divine-very-rare",
    "legendary divine essence": "essence-divine-legendary",
    "common primal essence": "essence-primal-common",
    "uncommon primal essence": "essence-primal-uncommon",
    "rare primal essence": "essence-primal-rare",
    "very rare primal essence": "essence-primal-very-rare",
    "legendary primal essence": "essence-primal-legendary",
    "steel ingot": "ingot-steel",
    "ingot of steel": "ingot-steel",
    "iron ingot": "ingot-iron",
    "ingot of iron": "ingot-iron",
    "silver ingot": "ingot-silver",
    "ingot of silver": "ingot-silver",
    "gold ingot": "ingot-gold",
    "ingot of gold": "ingot-gold",
    "mithril ingot": "ingot-mithral",
    "mithral ingot": "ingot-mithral",
    "adamantine ingot": "ingot-adamantine",
    "glass vial": "glass-vial",
    "glass flask": "glass-vial",
    "leather scraps": "leather-scraps",
    "common leather": "leather-common",
    "thick hide": "hide-thick",
    "scaled hide": "hide-scaled",
    "dragon scale": "hide-dragon-scale",
    "simple parts": "parts-simple",
    "fancy parts": "parts-fancy",
    "esoteric parts": "parts-esoteric"
}

TRANSLATION_DICT = {
    # Poções e Elixires
    "Antitoxin": "Antídoto / Antitoxina",
    "Potion of Climbing": "Poção de Escalar",
    "Potion of Healing": "Poção de Cura",
    "Potion of Animal Friendship": "Poção de Amizade Animal",
    "Potion of Firebreath": "Poção de Sopro de Fogo",
    "Potion of Growth": "Poção de Crescimento",
    "Potion of Greater Healing": "Poção de Cura Maior",
    "Potion of Poison": "Poção de Veneno",
    "Potion of Resistance": "Poção de Resistência",
    "Potion of Water Breathing": "Poção de Respirar na Água",
    "Potion of Hill Giant Strength": "Poção de Força do Gigante da Colina",
    "Potion of Clairvoyance": "Poção de Clarividência",
    "Potion of Gaseous Form": "Poção de Forma Gasosa",
    "Potion of Diminution": "Poção de Diminuição",
    "Potion of Heroism": "Poção de Heroísmo",
    "Potion of Mind Reading": "Poção de Ler Mentes",
    "Potion of Superior Healing": "Poção de Cura Superior",
    "Potion of Supreme Healing": "Poção de Cura Suprema",
    "Potion of Flying": "Poção de Voo",
    "Potion of Invisibility": "Poção de Invisibilidade",
    "Potion of Speed": "Poção de Velocidade",
    "Potion of Stone Giant Strength": "Poção de Força do Gigante de Pedra",
    "Potion of Frost Giant Strength": "Poção de Força do Gigante do Gelo",
    "Potion of Fire Giant Strength": "Poção de Força do Gigante do Fogo",
    "Potion of Cloud Giant Strength": "Poção de Força do Gigante das Nuvens",
    "Potion of Storm Giant Strength": "Poção de Força do Gigante da Tempestade",
    "Potion of Longevity": "Poção de Longevidade",
    "Potion of Vitality": "Poção de Vitalidade",
    "Potion of Invulnerability": "Poção de Invulnerabilidade",
    "Oil of Slipperiness": "Óleo de Escorregamento",
    "Oil of Etherealness": "Óleo de Eterealidade",
    "Oil of Sharpness": "Óleo de Afiação",
    "Philter of Love": "Filtro de Amor",
    "Elixir of Health": "Elixir de Saúde",
    "Alchemist's Fire": "Fogo Alquímico",
    "Acid": "Ácido (Frasco)",
    "Acid Vial": "Frasco de Ácido",

    # Itens Maravilhosos e Mágicos
    "Bag of Holding": "Bolsa Espaçosa",
    "Boots of Elvenkind": "Botas Élficas",
    "Cloak of Elvenkind": "Manto Élfico",
    "Cloak of Protection": "Manto de Proteção",
    "Ring of Protection": "Anel de Proteção",
    "Ring of Feather Falling": "Anel de Queda Suave",
    "Ring of Warmth": "Anel do Calor",
    "Ring of Water Walking": "Anel de Andar sobre as Águas",
    "Ring of Jumping": "Anel do Salto",
    "Ring of Mind Shielding": "Anel de Escudo Mental",
    "Ring of Free Action": "Anel de Ação Livre",
    "Ring of Invisibility": "Anel de Invisibilidade",
    "Ring of Spell Storing": "Anel de Armazenar Magias",
    "Ring of Regeneration": "Anel de Regeneração",
    "Ring of Telekinesis": "Anel de Telecinesia",
    "Wand of Magic Missiles": "Varinha de Mísseis Mágicos",
    "Wand of the War Mage": "Varinha do Mago de Guerra",
    "Wand of the War Mage +1": "Varinha do Mago de Guerra +1",
    "Wand of the War Mage +2": "Varinha do Mago de Guerra +2",
    "Wand of the War Mage +3": "Varinha do Mago de Guerra +3",
    "Wand of Web": "Varinha de Teia",
    "Wand of Secrets": "Varinha dos Segredos",
    "Wand of Lightning Bolts": "Varinha de Relâmpagos",
    "Wand of Fireballs": "Varinha de Bolas de Fogo",
    "Wand of Paralysis": "Varinha de Paralisia",
    "Wand of Polymorph": "Varinha de Metamorfose",
    "Staff of Healing": "Cajado da Cura",
    "Staff of Power": "Cajado do Poder",
    "Staff of the Magi": "Cajado dos Magos",
    "Staff of the Woodlands": "Cajado das Florestas",
    "Staff of Withering": "Cajado do Ressecamento",
    "Staff of Swarming Insects": "Cajado dos Enxames",
    "Pearl of Power": "Pérola do Poder",
    "Amulet of Health": "Amuleto da Saúde",
    "Periapt of Wound Closure": "Periáptico da Cicatrização",
    "Brooch of Shielding": "Broche de Escudo",
    "Circlet of Blasting": "Diadema da Explosão",
    "Eyes of Minute Seeing": "Olhos de Vidência Menor",
    "Goggles of Night": "Óculos da Noite",
    "Headband of Intellect": "Tiara do Intelecto",
    "Gauntlets of Ogre Power": "Manoplas da Força do Ogro",
    "Belt of Hill Giant Strength": "Cinto da Força do Gigante da Colina",
    "Bracers of Archery": "Braçadeiras do Arqueiro",
    "Bracers of Defense": "Braçadeiras de Defesa",
    "Decanter of Endless Water": "Decantador de Água Infinita",
    "Driftglobe": "Globo Flutuante",
    "Eversmoking Bottle": "Garrafa de Fumaça Eterna",
    "Immovable Rod": "Bastão Imóvel",
    "Rope of Climbing": "Corda de Escalar",
    "Winged Boots": "Botas Aladas",
    "Broom of Flying": "Vassoura Voadora",
    "Cloak of the Manta Ray": "Manto da Arraia",
    "Cloak of the Bat": "Manto do Morcego",
    "Helm of Telepathy": "Elmo da Telepatia",
    "Lantern of Revealing": "Lanterna da Revelação",
    "Medallion of Thoughts": "Medalhão dos Pensamentos",

    # Armas e Armaduras
    "Dagger": "Adaga",
    "Shortsword": "Espada Curta",
    "Longsword": "Espada Longa",
    "Greatsword": "Espadão",
    "Scimitar": "Cimitarra",
    "Rapier": "Rapieira",
    "Mace": "Maça",
    "Warhammer": "Martelo de Guerra",
    "Battleaxe": "Machado de Batalha",
    "Greataxe": "Machado Grande",
    "Halberd": "Alabarda",
    "Pike": "Pique",
    "Shield": "Escudo",
    "Leather Armor": "Armadura de Couro",
    "Studded Leather Armor": "Armadura de Couro Batido",
    "Chain Shirt": "Camisa de Cota de Malha",
    "Scale Mail": "Cota de Escamas",
    "Breastplate": "Peitoral de Aço",
    "Half Plate": "Meia-Placa",
    "Plate Armor": "Armadura de Placas",

    # Materiais
    "Hide Scraps": "Retalhos de Couro",
    "Boiled Leather": "Couro Fervido",
    "Rawhide Leather": "Couro Cru",
    "Tanned Leather": "Couro Curtido",
    "Large Carapace": "Carapaça Grande",
    "Medium Carapace": "Carapaça Média",
    "Resistant Hide": "Pele Resistente",
    "Resistant Leather": "Couro Resistente",
    "Tough Leather": "Couro Reforçado",
    "Metal Scraps": "Retalhos de Metal",
    "Gold Scraps": "Retalhos de Ouro",
    "Steel Chain (2 ft)": "Corrente de Aço (60 cm)",
    "Mithril Ingot": "Lingote de Mithral",
    "Adamantine Ingot": "Lingote de Adamantina",
    "Firewood": "Lenha",
    "Common Branch": "Galho Comum",
    "Quality Branch": "Galho de Qualidade",
    "Rare Branch": "Galho Raro",
    "Very Rare Branch": "Galho Muito Raro",
    "Legendary Branch": "Galho Lendário",
    "Uncommon Branch": "Galho Incomum",
    "Common Reagent": "Reagente Comum",
    "Uncommon Reagent": "Reagente Incomum",
    "Rare Reagent": "Reagente Raro",
    "Very Rare Reagent": "Reagente Muito Raro",
    "Legendary Reagent": "Reagente Lendário",
    "Common Essence": "Essência Comum",
    "Rare Essence": "Essência Rara",
    "Very Rare Essence": "Essência Muito Rara",
    "Legendary Essence": "Essência Lendária",
    "Glass Flask": "Frasco de Vidro",
    "Normal Ink": "Tinta Comum",
    "Uncommon Magical Ink": "Tinta Mágica Incomum",
    "Rare Magical Ink": "Tinta Mágica Rara",
    "Very Rare Magical Ink": "Tinta Mágica Muito Rara",
    "Legendary Magical Ink": "Tinta Mágica Lendária",
    "Uncommon Parchment": "Pergaminho Incomum",
    "Legendary Parchment": "Pergaminho Lendário",
    "Parts": "Peças Mecânicas",
    "Fancy Parts": "Peças Refinadas",
    "Esoteric Parts": "Peças Esotéricas",
    "Short Haft": "Cabo Curto",
    "Wooden Stock": "Coronha de Madeira",
    "Length of String": "Pedaço de Corda / Fio",
    "Buckle": "Fivela de Metal",
    "Fletching": "Penas de Flecha",
    "Supplies (Salt, Staples, etc)": "Suprimentos Básicos (Sal, Temperos)",
    "Rare Supplies (Hard to luxury goods)": "Suprimentos Raros (Especiarias Finas)"
}

WORD_TRANSLATIONS = [
    ("Potion of ", "Poção de "),
    ("Elixir of ", "Elixir de "),
    ("Oil of ", "Óleo de "),
    ("Ring of ", "Anel de "),
    ("Wand of ", "Varinha de "),
    ("Staff of ", "Cajado de "),
    ("Rod of ", "Bastão de "),
    ("Cloak of ", "Manto de "),
    ("Boots of ", "Botas de "),
    ("Belt of ", "Cinto de "),
    ("Amulet of ", "Amuleto de "),
    ("Armor of ", "Armadura de "),
    ("Shield of ", "Escudo de "),
    ("Sword of ", "Espada de "),
    ("Bow of ", "Arco de "),
    ("Manual of ", "Manual de "),
    ("Tome of ", "Tomo de "),
    ("Robe of ", "Vestes de "),
    ("Helm of ", "Elmo de "),
    ("Gauntlets of ", "Manoplas de "),
    ("Bracers of ", "Braçadeiras de "),
    ("Dust of ", "Pó de "),
    ("Scroll of ", "Pergaminho de "),
    ("Circlet of ", "Diadema de "),
    ("Brooch of ", "Broche de "),
    ("Figurine of Wondrous Power: ", "Estatueta de Poder Maravilhoso: "),
    ("Horn of ", "Berrante de "),
    ("Eyes of ", "Olhos de ")
]

def translate_name_pt(name: str) -> str:
    clean = name.strip()
    if clean in TRANSLATION_DICT:
        return TRANSLATION_DICT[clean]
    for eng, pt in WORD_TRANSLATIONS:
        if clean.startswith(eng):
            suffix = clean[len(eng):]
            return f"{pt}{suffix}"
    return clean

def choose_icon(name: str, branch: str, item_type: str) -> str:
    nl = name.lower()
    if "potion" in nl or "elixir" in nl:
        if "healing" in nl: return "icons/consumables/potions/potion-tube-corked-red.webp"
        if "poison" in nl or "toxic" in nl: return "icons/consumables/potions/potion-tube-corked-purple.webp"
        if "climb" in nl or "growth" in nl: return "icons/consumables/potions/potion-tube-corked-green.webp"
        if "fire" in nl or "flame" in nl: return "icons/consumables/potions/bottle-bulb-corked-fire-orange.webp"
        if "fly" in nl or "speed" in nl: return "icons/consumables/potions/potion-tube-corked-blue.webp"
        return "icons/consumables/potions/potion-tube-corked-red.webp"
    if "oil" in nl or "acid" in nl or "alchemist" in nl:
        return "icons/consumables/potions/bottle-bulb-corked-green.webp"
    if "sword" in nl or "blade" in nl or "scimitar" in nl or "rapier" in nl or "dagger" in nl:
        return "icons/weapons/swords/sword-broad-steel.webp"
    if "axe" in nl:
        return "icons/weapons/axes/axe-battle-double.webp"
    if "hammer" in nl or "mace" in nl:
        return "icons/weapons/hammers/warhammer-steel.webp"
    if "bow" in nl or "arrow" in nl:
        return "icons/weapons/bows/shortbow-recurve.webp"
    if "shield" in nl:
        return "icons/equipment/shield/heater-steel.webp"
    if "armor" in nl or "plate" in nl or "mail" in nl or "breastplate" in nl:
        return "icons/equipment/chest/breastplate-steel.webp"
    if "ring" in nl:
        return "icons/equipment/finger/ring-band-gold.webp"
    if "wand" in nl:
        return "icons/weapons/wands/wand-carved-gold.webp"
    if "staff" in nl or "quarterstaff" in nl:
        return "icons/weapons/staves/staff-simple.webp"
    if "scroll" in nl or "tome" in nl or "manual" in nl or "book" in nl:
        return "icons/sundries/scrolls/scroll-bound-ribbon-blue.webp"
    if "boots" in nl or "shoes" in nl or "slippers" in nl:
        return "icons/equipment/feet/boots-leather-simple.webp"
    if "cloak" in nl or "robe" in nl or "cape" in nl:
        return "icons/equipment/back/cloak-simple-brown.webp"
    if "amulet" in nl or "necklace" in nl or "pendant" in nl or "periapt" in nl:
        return "icons/equipment/neck/amulet-round-gold.webp"
    if "helm" in nl or "hat" in nl or "cap" in nl or "circlet" in nl:
        return "icons/equipment/head/helm-steel.webp"
    if "belt" in nl:
        return "icons/equipment/waist/belt-simple-leather.webp"
    if "gauntlets" in nl or "bracers" in nl or "gloves" in nl:
        return "icons/equipment/hand/gauntlet-steel.webp"
    if "bag" in nl or "quiver" in nl or "bottle" in nl or "sack" in nl:
        return "icons/containers/bags/sack-leather-brown.webp"
    if "gem" in nl or "pearl" in nl or "crystal" in nl:
        return "icons/commodities/gems/gem-faceted-round-blue.webp"
    
    if branch == "alchemy": return "icons/consumables/potions/bottle-empty.webp"
    if branch == "poisoncraft": return "icons/consumables/potions/potion-tube-corked-purple.webp"
    if branch in ["blacksmithing", "custom_weapons", "components_and_materials"]: return "icons/weapons/swords/sword-broad-steel.webp"
    if branch in ["wand_whittling"]: return "icons/weapons/wands/wand-carved-gold.webp"
    if branch in ["scrollscribing"]: return "icons/sundries/scrolls/scroll-bound-ribbon-blue.webp"
    return "icons/commodities/treasure/chest-wooden.webp"

def map_branch_to_profession(branch: str) -> dict:
    b = (branch or "alchemy").lower()
    if b == "alchemy":
        return {"profession": "alchemy", "tool": "alchemist", "ability": ["int", "wis"]}
    elif b == "poisoncraft":
        return {"profession": "poisoncraft", "tool": "poisoner", "ability": ["int", "wis"]}
    elif b in ["blacksmithing", "custom_weapons", "components_and_materials"]:
        return {"profession": "blacksmithing", "tool": "smith", "ability": ["str"]}
    elif b == "wand_whittling":
        return {"profession": "wandwhittling", "tool": "woodcarver", "ability": ["dex", "int"]}
    elif b == "scrollscribing":
        return {"profession": "scrollscribing", "tool": "calligrapher", "ability": ["int", "wis"]}
    elif b in ["weapon_enchanting", "magic_armor", "wondrous_item_crafting", "rings_talismans",
               "staff_crafting", "rods_manuals_tomes", "other_magic_items", "psionic_items"]:
        return {"profession": "enchanting", "tool": "arcana", "ability": ["int"]}
    else:
        return {"profession": "enchanting", "tool": "arcana", "ability": ["int"]}

def parse_material_list(raw_materials):
    parsed = []
    for line in raw_materials:
        line_clean = line.strip()
        if not line_clean:
            continue
        m = re.match(r"^(\d+)\s+(.+)$", line_clean)
        if m:
            qty = int(m.group(1))
            mat_name = m.group(2).strip()
        else:
            qty = 1
            mat_name = line_clean
        
        # Checa se existe mapeamento canônico
        clean_name_lower = mat_name.lower()
        if clean_name_lower in CANONICAL_KEYS:
            key = CANONICAL_KEYS[clean_name_lower]
        else:
            key = re.sub(r"[^a-zA-Z0-9]+", "-", clean_name_lower).strip("-")
            
        parsed.append({
            "raw": line_clean,
            "key": key,
            "name": mat_name,
            "name_pt": translate_name_pt(mat_name),
            "quantity": qty
        })
    return parsed

def main():
    print("Iniciando importação e fusão do acervo completo...")

    # Carrega módulo build-data original para manter as 43 matérias primas fundamentais
    from importlib.machinery import SourceFileLoader
    build_data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "build-data.py")
    build_data = SourceFileLoader("build_data", build_data_path).load_module()
    CURATED_DEF = build_data.MATERIALS_DEF
    build_tables_json = build_data.build_tables_json
    build_rules_json = build_data.build_rules_json

    with open(f"{SOURCE_DIR}/foundry-materials.json", encoding="utf-8") as f:
        raw_materials = json.load(f)["items"]

    with open(f"{SOURCE_DIR}/foundry-items.json", encoding="utf-8") as f:
        raw_items = json.load(f)["items"]

    # 1. MONTAR MATERIAIS (CURADOS + OFICIAIS DEDUP)
    materials_pt = []
    materials_en = []
    seen_material_keys = set()

    # Adiciona materiais fundamentais primeiro
    for m in CURATED_DEF:
        key = m["key"]
        seen_material_keys.add(key)
        doc_id = make_id(f"mat-{key}")

        doc_base = {
            "_id": doc_id,
            "type": "loot",
            "img": m["img"],
            "system": {
                "source": "Kibbles' Crafting Guide",
                "quantity": 1,
                "weight": m["weight"],
                "price": {
                    "value": m["price"],
                    "denomination": "gp" if m["price"] >= 1 else "sp"
                },
                "rarity": m["rarity"],
                "identified": True
            },
            "flags": {
                "itensdnd": {
                    "materialKey": key,
                    "isMaterial": True,
                    "category": m.get("category", "general"),
                    "rarity": m["rarity"]
                }
            }
        }

        # PT
        doc_pt = json.loads(json.dumps(doc_base))
        doc_pt["name"] = m["name_pt"]
        doc_pt["system"]["description"] = {
            "value": f"<p>{m['desc_pt']}</p>",
            "chat": "", "unidentified": ""
        }
        materials_pt.append(doc_pt)

        # EN
        doc_en = json.loads(json.dumps(doc_base))
        doc_en["name"] = m["name_en"]
        doc_en["system"]["description"] = {
            "value": f"<p>{m['desc_en']}</p>",
            "chat": "", "unidentified": ""
        }
        materials_en.append(doc_en)

    # Agora funde materiais adicionais de foundry-materials.json
    for m in raw_materials:
        name_en = m["name"].strip()
        mat_slug = re.sub(r"[^a-zA-Z0-9]+", "-", name_en.lower()).strip("-")
        if mat_slug in seen_material_keys:
            continue
        seen_material_keys.add(mat_slug)

        name_pt = translate_name_pt(name_en)
        doc_id = make_id(f"kibbles-mat-{mat_slug}")

        price_val = m.get("system", {}).get("price", {}).get("value", 1)
        price_den = m.get("system", {}).get("price", {}).get("denomination", "gp")
        rarity = m.get("system", {}).get("rarity", "common").lower()
        if rarity == "trivial": rarity = "common"

        icon = choose_icon(name_en, "material", "loot")

        doc_base = {
            "_id": doc_id,
            "type": "loot",
            "img": icon,
            "system": {
                "source": "Kibbles' Crafting Guide",
                "quantity": 1,
                "weight": 0.5,
                "price": {"value": price_val, "denomination": price_den},
                "rarity": rarity,
                "identified": True
            },
            "flags": {
                "itensdnd": {
                    "materialKey": mat_slug,
                    "isMaterial": True,
                    "rarity": rarity
                }
            }
        }

        # PT
        doc_pt = json.loads(json.dumps(doc_base))
        doc_pt["name"] = name_pt
        doc_pt["system"]["description"] = {
            "value": f"<p>Material oficial de criação do Kibbles' Crafting Guide ({name_en}).</p>",
            "chat": "", "unidentified": ""
        }
        materials_pt.append(doc_pt)

        # EN
        doc_en = json.loads(json.dumps(doc_base))
        doc_en["name"] = name_en
        doc_en["system"]["description"] = {
            "value": f"<p>Official crafting material from Kibbles' Crafting Guide.</p>",
            "chat": "", "unidentified": ""
        }
        materials_en.append(doc_en)

    print(f"Total de materiais unificados e estruturados: {len(materials_pt)}")

    # 2. MONTAR RECEITAS (TODAS AS 479)
    recipes_pt = []
    recipes_en = []
    seen_recipes = set()

    for item in raw_items:
        name_en = item["name"].strip()
        craft_info = item.get("system", {}).get("crafting", {})
        branch = craft_info.get("branch", "alchemy")
        recipe_unique_key = f"{name_en}-{branch}"

        if recipe_unique_key in seen_recipes:
            continue
        seen_recipes.add(recipe_unique_key)

        name_pt = translate_name_pt(name_en)
        prof_data = map_branch_to_profession(branch)
        recipe_slug = re.sub(r"[^a-zA-Z0-9]+", "-", name_en.lower()).strip("-")
        doc_id = make_id(f"rec-{recipe_slug}-{branch}")

        dc = craft_info.get("difficulty", 13)
        hours = craft_info.get("craftingTime", {}).get("hours", 2.0)
        checks = craft_info.get("checks", max(1, int(hours // 2)))
        rarity = item.get("system", {}).get("rarity", "common").lower()
        if rarity == "trivial": rarity = "common"

        raw_mats = craft_info.get("materials", [])
        parsed_mats = parse_material_list(raw_mats)

        price_data = item.get("system", {}).get("price", {})
        price_val = price_data.get("value", 50)
        price_den = price_data.get("denomination", "gp")
        val_str = f"{price_val} {price_den}"

        icon = choose_icon(name_en, branch, item.get("type", "consumable"))

        engine_materials = [{"key": m["key"], "quantity": m["quantity"]} for m in parsed_mats]
        mat_list_html_pt = "".join([f"<li>{m['quantity']}x {m['name_pt']}</li>" for m in parsed_mats])
        mat_list_html_en = "".join([f"<li>{m['quantity']}x {m['name']}</li>" for m in parsed_mats])

        doc_base = {
            "_id": doc_id,
            "type": "loot",
            "img": icon,
            "system": {
                "source": "Kibbles' Crafting Guide",
                "quantity": 1,
                "weight": 0.1,
                "price": {"value": price_val, "denomination": price_den},
                "rarity": rarity,
                "identified": True
            },
            "flags": {
                "itensdnd": {
                    "isRecipe": True,
                    "recipeKey": recipe_slug,
                    "branch": branch,
                    "profession": prof_data["profession"],
                    "tool": prof_data["tool"],
                    "ability": prof_data["ability"],
                    "materials": engine_materials,
                    "time": int(hours) if hours >= 1 else 1,
                    "checks": checks,
                    "dc": dc,
                    "resultItem": name_en,
                    "rarity": rarity,
                    "value": val_str
                }
            }
        }

        # PT
        doc_pt = json.loads(json.dumps(doc_base))
        doc_pt["name"] = f"Receita: {name_pt}"
        doc_pt["flags"]["itensdnd"]["resultItem"] = name_pt
        doc_pt["system"]["description"] = {
            "value": f"""<h3>Receita: {name_pt}</h3>
<p><strong>Profissão:</strong> {prof_data['profession'].capitalize()} | <strong>CD:</strong> {dc} | <strong>Tempo:</strong> {hours}h ({checks} testes)</p>
<p><strong>Materiais Necessários:</strong></p>
<ul>{mat_list_html_pt or '<li>Materiais especiais descritos no livro</li>'}</ul>
<p><strong>Resultado:</strong> {name_pt} ({val_str})</p>""",
            "chat": "", "unidentified": ""
        }
        recipes_pt.append(doc_pt)

        # EN
        doc_en = json.loads(json.dumps(doc_base))
        doc_en["name"] = f"Recipe: {name_en}"
        doc_en["system"]["description"] = {
            "value": f"""<h3>Recipe: {name_en}</h3>
<p><strong>Profession:</strong> {prof_data['profession'].capitalize()} | <strong>DC:</strong> {dc} | <strong>Time:</strong> {hours}h ({checks} checks)</p>
<p><strong>Required Materials:</strong></p>
<ul>{mat_list_html_en or '<li>Special materials described in source</li>'}</ul>
<p><strong>Result:</strong> {name_en} ({val_str})</p>""",
            "chat": "", "unidentified": ""
        }
        recipes_en.append(doc_en)

    print(f"Total de receitas processadas: {len(recipes_pt)}")

    # 3. SALVAR ARQUIVOS FINAIS
    for lang, m_list, r_list in [("pt-BR", materials_pt, recipes_pt), ("en", materials_en, recipes_en)]:
        target_dir = os.path.join(DEST_DIR, lang)
        os.makedirs(target_dir, exist_ok=True)

        with open(os.path.join(target_dir, "crafting-materials.json"), "w", encoding="utf-8") as f:
            json.dump(m_list, f, ensure_ascii=False, indent=2)

        with open(os.path.join(target_dir, "crafting-recipes.json"), "w", encoding="utf-8") as f:
            json.dump(r_list, f, ensure_ascii=False, indent=2)

        # Mantém tabelas de rolagem e diários de regras atualizados
        tbls = build_tables_json(lang)
        with open(os.path.join(target_dir, "crafting-tables.json"), "w", encoding="utf-8") as f:
            json.dump(tbls, f, ensure_ascii=False, indent=2)

        rules = build_rules_json(lang)
        with open(os.path.join(target_dir, "crafting-rules.json"), "w", encoding="utf-8") as f:
            json.dump(rules, f, ensure_ascii=False, indent=2)

        print(f"Gerado com sucesso para {lang}: {len(m_list)} materiais, {len(r_list)} receitas, {len(tbls)} tabelas, {len(rules)} regras.")

if __name__ == "__main__":
    main()
