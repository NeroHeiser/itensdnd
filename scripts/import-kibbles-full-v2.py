#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
import-kibbles-full-v2.py
Processamento integral de todos os arquivos em:
/run/media/lopes/Hd interno/RPG/itens/Crafting+PDF+(Free)-Foundry-JSON/
- foundry-items.json (479 itens reais e receitas)
- foundry-materials.json (materiais oficiais + curados)
- crafting-mechanics.json (14 regras oficiais estruturadas)
- reference-tables.json (tabelas de apoio, forragem, forja, alquimia e salvamento)
- review-queue.json
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
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEST_DIR = os.path.join(SCRIPT_DIR, "data")

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

    # Itens Mágicos
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
        return {"profession": "alchemy", "tool": "alchemist", "ability": ["int", "wis"], "label_pt": "Alquimia", "label_en": "Alchemy"}
    elif b == "poisoncraft":
        return {"profession": "poisoncraft", "tool": "poisoner", "ability": ["int", "wis"], "label_pt": "Venefício", "label_en": "Poisoncraft"}
    elif b in ["blacksmithing", "custom_weapons", "components_and_materials"]:
        return {"profession": "blacksmithing", "tool": "smith", "ability": ["str"], "label_pt": "Ferraria", "label_en": "Blacksmithing"}
    elif b == "wand_whittling":
        return {"profession": "wandwhittling", "tool": "woodcarver", "ability": ["dex", "int"], "label_pt": "Entalhe de Varinhas", "label_en": "Wand Whittling"}
    elif b == "scrollscribing":
        return {"profession": "scrollscribing", "tool": "calligrapher", "ability": ["int", "wis"], "label_pt": "Escrição de Pergaminhos", "label_en": "Scroll Scribing"}
    else:
        return {"profession": "enchanting", "tool": "arcana", "ability": ["int"], "label_pt": "Encantamento", "label_en": "Enchanting"}

def parse_material_list(raw_materials):
    parsed = []
    for line in raw_materials:
        line_clean = line.strip()
        if not line_clean:
            continue
        m = re.match(r"^(\d+[\.,]?\d*)\s*(?:x\s*)?(.*)$", line_clean)
        if m:
            qty_str = m.group(1).replace(',', '.')
            try:
                qty = float(qty_str)
                if qty.is_integer():
                    qty = int(qty)
            except ValueError:
                qty = 1
            mat_name = m.group(2).strip()
        else:
            qty = 1
            mat_name = line_clean
        
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

def determine_item_type(name: str, branch: str, raw_type: str) -> str:
    nl = name.lower()
    if raw_type == "consumable" or "potion" in nl or "elixir" in nl or "oil of" in nl or "antitoxin" in nl or "acid" in nl:
        return "consumable"
    if raw_type == "weapon" or "sword" in nl or "dagger" in nl or "axe" in nl or "hammer" in nl or "mace" in nl or "spear" in nl or "bow" in nl or "halberd" in nl or "ammunition" in nl:
        return "weapon"
    if raw_type == "equipment" or "armor" in nl or "shield" in nl or "breastplate" in nl or "plate" in nl or "mail" in nl or "robe" in nl or "cloak" in nl or "boots" in nl or "helm" in nl or "ring" in nl or "amulet" in nl or "belt" in nl or "bracers" in nl or "gauntlets" in nl or "periapt" in nl or "circlet" in nl:
        return "equipment"
    return "loot"

def estimate_weight(item_type: str, name: str) -> float:
    nl = name.lower()
    if item_type == "consumable": return 0.5
    if item_type == "equipment":
        if "plate" in nl: return 55.0
        if "mail" in nl: return 40.0
        if "breastplate" in nl or "half plate" in nl: return 25.0
        if "leather" in nl: return 10.0
        if "shield" in nl: return 6.0
        if "boots" in nl or "cloak" in nl or "helm" in nl: return 2.0
        if "ring" in nl or "amulet" in nl or "circlet" in nl: return 0.1
        return 5.0
    if item_type == "weapon":
        if "great" in nl or "halberd" in nl or "pike" in nl: return 6.0
        if "longsword" in nl or "battleaxe" in nl or "warhammer" in nl: return 3.0
        if "dagger" in nl: return 1.0
        if "shortsword" in nl or "scimitar" in nl or "rapier" in nl: return 2.0
        if "bow" in nl: return 2.0
        return 3.0
    return 1.0


def main():
    print("Iniciando Ingestão Total (v2) de Crafting+PDF+(Free)-Foundry-JSON...")

    # Carrega dados curados para manter os 43 materiais fundamentais
    from importlib.machinery import SourceFileLoader
    build_data_path = os.path.join(SCRIPT_DIR, "build-data.py")
    build_data = SourceFileLoader("build_data", build_data_path).load_module()
    CURATED_DEF = build_data.MATERIALS_DEF

    # Carrega arquivos de origem
    with open(f"{SOURCE_DIR}/foundry-materials.json", encoding="utf-8") as f:
        raw_materials = json.load(f)["items"]

    with open(f"{SOURCE_DIR}/foundry-items.json", encoding="utf-8") as f:
        raw_items = json.load(f)["items"]

    with open(f"{SOURCE_DIR}/crafting-mechanics.json", encoding="utf-8") as f:
        raw_mechanics = json.load(f)["rules"]

    # 1. MATERIAIS (92 ITENS DEDUPLICADOS E CANONICALIZADOS)
    materials_pt = []
    materials_en = []
    seen_material_keys = set()

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
        doc_pt = json.loads(json.dumps(doc_base))
        doc_pt["name"] = m["name_pt"]
        doc_pt["system"]["description"] = {
            "value": f"<p>{m['desc_pt']}</p>",
            "chat": "", "unidentified": ""
        }
        materials_pt.append(doc_pt)

        doc_en = json.loads(json.dumps(doc_base))
        doc_en["name"] = m["name_en"]
        doc_en["system"]["description"] = {
            "value": f"<p>{m['desc_en']}</p>",
            "chat": "", "unidentified": ""
        }
        materials_en.append(doc_en)

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
        doc_pt = json.loads(json.dumps(doc_base))
        doc_pt["name"] = name_pt
        doc_pt["system"]["description"] = {
            "value": f"<p>Material oficial de criação do Kibbles' Crafting Guide ({name_en}).</p>",
            "chat": "", "unidentified": ""
        }
        materials_pt.append(doc_pt)

        doc_en = json.loads(json.dumps(doc_base))
        doc_en["name"] = name_en
        doc_en["system"]["description"] = {
            "value": f"<p>Official crafting material from Kibbles' Crafting Guide.</p>",
            "chat": "", "unidentified": ""
        }
        materials_en.append(doc_en)

    print(f"Total de Materiais: {len(materials_pt)}")

    # 2. ITENS REAIS (CRAFTING-ITEMS) & RECEITAS (CRAFTING-RECIPES)
    items_pt = []
    items_en = []
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
        item_id = make_id(f"item-{recipe_slug}-{branch}")
        recipe_id = make_id(f"rec-{recipe_slug}-{branch}")

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

        final_item_type = determine_item_type(name_en, branch, item.get("type", "loot"))
        icon = choose_icon(name_en, branch, final_item_type)
        weight = estimate_weight(final_item_type, name_en)

        mat_list_html_pt = "".join([f"<li>{m['quantity']}x {m['name_pt']}</li>" for m in parsed_mats])
        mat_list_html_en = "".join([f"<li>{m['quantity']}x {m['name']}</li>" for m in parsed_mats])

        # DOCUMENTO DE ITEM REAL (COMPENDIUM: CRAFTING-ITEMS)
        item_doc_base = {
            "_id": item_id,
            "type": final_item_type,
            "img": icon,
            "system": {
                "source": "Kibbles' Crafting Guide",
                "quantity": 1,
                "weight": weight,
                "price": {"value": price_val, "denomination": price_den},
                "rarity": rarity,
                "identified": True
            },
            "flags": {
                "itensdnd": {
                    "isCraftedItem": True,
                    "recipeId": recipe_id,
                    "branch": branch,
                    "profession": prof_data["profession"]
                }
            }
        }

        # Item PT
        item_pt = json.loads(json.dumps(item_doc_base))
        item_pt["name"] = name_pt
        item_pt["system"]["description"] = {
            "value": (
                f"<div class='itensdnd-item-desc'>"
                f"<p><strong>Ramo:</strong> {prof_data['label_pt']} | <strong>Raridade:</strong> {rarity.capitalize()} | <strong>Valor de Mercado:</strong> {val_str}</p>"
                f"<hr/>"
                f"<p><em>Item forjado ou preparado através das regras de criação do Kibbles' Crafting Guide.</em></p>"
                f"<h4>Requisitos de Criação:</h4>"
                f"<ul>{mat_list_html_pt}</ul>"
                f"<p><strong>Tempo Necessário:</strong> {hours} horas | <strong>Testes:</strong> {checks} | <strong>Dificuldade:</strong> CD {dc}</p>"
                f"</div>"
            ),
            "chat": "", "unidentified": ""
        }
        items_pt.append(item_pt)

        # Item EN
        item_en = json.loads(json.dumps(item_doc_base))
        item_en["name"] = name_en
        item_en["system"]["description"] = {
            "value": (
                f"<div class='itensdnd-item-desc'>"
                f"<p><strong>Branch:</strong> {prof_data['label_en']} | <strong>Rarity:</strong> {rarity.capitalize()} | <strong>Market Value:</strong> {val_str}</p>"
                f"<hr/>"
                f"<p><em>Crafted or prepared through the mechanics of Kibbles' Crafting Guide.</em></p>"
                f"<h4>Crafting Requirements:</h4>"
                f"<ul>{mat_list_html_en}</ul>"
                f"<p><strong>Crafting Time:</strong> {hours} hours | <strong>Checks:</strong> {checks} | <strong>Difficulty:</strong> DC {dc}</p>"
                f"</div>"
            ),
            "chat": "", "unidentified": ""
        }
        items_en.append(item_en)

        # DOCUMENTO DE RECEITA (COMPENDIUM: CRAFTING-RECIPES)
        engine_materials = [{"key": m["key"], "quantity": m["quantity"]} for m in parsed_mats]

        recipe_doc_base = {
            "_id": recipe_id,
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
                    "resultItemId": item_id,
                    "rarity": rarity,
                    "value": val_str
                }
            }
        }

        # Receita PT
        recipe_pt = json.loads(json.dumps(recipe_doc_base))
        recipe_pt["name"] = f"Receita: {name_pt}"
        recipe_pt["flags"]["itensdnd"]["resultItem"] = name_pt
        recipe_pt["system"]["description"] = {
            "value": (
                f"<h3>{recipe_pt['name']}</h3>"
                f"<p><strong>Profissão:</strong> {prof_data['label_pt']} | <strong>CD:</strong> {dc} | <strong>Tempo:</strong> {hours}h ({checks} testes)</p>"
                f"<h4>Materiais Necessários:</h4><ul>{mat_list_html_pt}</ul>"
                f"<p><strong>Item Resultante:</strong> {name_pt} ({val_str})</p>"
            ),
            "chat": "", "unidentified": ""
        }
        recipes_pt.append(recipe_pt)

        # Receita EN
        recipe_en = json.loads(json.dumps(recipe_doc_base))
        recipe_en["name"] = f"Recipe: {name_en}"
        recipe_en["flags"]["itensdnd"]["resultItem"] = name_en
        recipe_en["system"]["description"] = {
            "value": (
                f"<h3>{recipe_en['name']}</h3>"
                f"<p><strong>Profession:</strong> {prof_data['label_en']} | <strong>DC:</strong> {dc} | <strong>Time:</strong> {hours}h ({checks} checks)</p>"
                f"<h4>Required Materials:</h4><ul>{mat_list_html_en}</ul>"
                f"<p><strong>Result Item:</strong> {name_en} ({val_str})</p>"
            ),
            "chat": "", "unidentified": ""
        }
        recipes_en.append(recipe_en)

    print(f"Total de Itens Reais Criáveis: {len(items_pt)}")
    print(f"Total de Receitas: {len(recipes_pt)}")

    # 3. DIÁRIOS DE REGRAS E MECÂNICAS (CRAFTING-RULES)
    # Formata todas as 14 mecânicas em HTML estilizado de alta qualidade
    mechanics_html_pt = """
    <h2>Mecânicas Fundamentais de Criação (Kibbles' Crafting Guide)</h2>
    <p>O sistema de criação do Kibbles' foi desenvolvido para permitir que aventureiros produzam itens mundanos e mágicos de forma dinâmica e balanceada.</p>
    """
    mechanics_html_en = """
    <h2>Core Crafting Mechanics (Kibbles' Crafting Guide)</h2>
    <p>Kibbles' crafting system allows adventurers to produce mundane and magical items in a balanced, dynamic, and engaging way.</p>
    """

    rules_pt_map = {
        "crafting_check": ("Testes de Criação (Checks de 2 Horas)", "A cada 2 horas de trabalho contínuo, o personagem realiza um teste de criação. Um sucesso adiciona 2 horas de progresso ao projeto. Em caso de falha, nenhum progresso é obtido."),
        "failure": ("Falhas e Perda de Materiais", "Falhar no teste não adiciona progresso. Caso ocorram <strong>3 falhas consecutivas</strong> no mesmo projeto, os materiais reservados são irremediavelmente perdidos e o progresso é zerado."),
        "take_10": ("Garantir 10 (Take 10)", "O artesão pode optar por trabalhar com mais cuidado: cada teste passa a custar <strong>4 horas de trabalho</strong> e utiliza o resultado fixo de <strong>10 + modificador de habilidade + bônus de proficiência da ferramenta</strong>."),
        "workday_limit": ("Jornada de Trabalho Diária (8 Horas)", "Um dia completo de trabalho contribui no máximo com <strong>8 horas</strong> para um projeto de criação, evitando fadiga extrema."),
        "rest_crafting": ("Criação durante Descanso Longo (Ação de Acampamento)", "Durante um descanso longo, um personagem pode dedicar até <strong>2 horas</strong> ao artesanato como ação de acampamento, desde que durma pelo menos 6 horas. Sua percepção passiva fica reduzida durante o trabalho."),
        "tool_requirement": ("Exigência de Ferramentas Adequadas", "Tentar criar um item sem a ferramenta apropriada é impossível. O Mestre pode permitir ferramentas improvisadas com desvantagem em todos os testes."),
        "heat_and_infrastructure": ("Infraestrutura e Fontes de Calor", "Certas ramificações exigem instalações específicas: a forja de itens de metal requer uma <strong>forja e bigorna</strong> ativas."),
        "roll_bonuses": ("Bônus e Auxílio de Outros Criadores", "Testes de criação não recebem bônus temporários comuns (como Orientação). A principal exceção é a ajuda contínua de outro artesão proficiente durante todo o período de trabalho."),
        "material_trade": ("Comércio e Aquisição de Materiais", "Comprar materiais normalmente custa o valor de tabela listado. Vender materiais brutos a compradores interessados rende cerca de metade do valor de mercado."),
        "reagent_interchangeability": ("Intercambialidade de Reagentes", "Reagentes Curativos, Reativos e Venenosos são intercambiáveis dentro de seu respectivo tipo e raridade. Não podem ser recuperados após combinados."),
        "essence_synthesis": ("Síntese de Essências", "Três reagentes da mesma raridade podem ser sintetizados em uma essência: <em>Essência Arcana</em> (1 curativo + 1 venenoso + 1 reativo); <em>Essência Primitiva</em> (3 reativos); <em>Essência Divina</em> (2 curativos + 1 reativo)."),
        "essence_salvage": ("Desmanche e Salvamento de Itens Mágicos", "Um item mágico permanente pode ser desmanchado em um processo de 2 horas para extrair <strong>uma essência de sua raridade</strong>. O item original perde todas as propriedades mágicas."),
        "ink_and_ingot": ("Padrões de Tintas e Lingotes", "Tintas mágicas possuem peso padrão de 0.1 lb por frasco; lingotes de aço padrão pesam 2 lb (cerca de 1 kg) e custam 2 po cada."),
        "labor_formula": ("Fórmula de Trabalho e Design de Receitas", "O tempo, dificuldade (CD) e custos de trabalho baseiam-se na raridade e no valor final do item, escalando de itens comuns (CD 10–13, 2–8h) até lendários (CD 20–25, 24–40h+).")
    }

    for r in raw_mechanics:
        r_name = r["name"]
        if r_name in rules_pt_map:
            t_pt, d_pt = rules_pt_map[r_name]
        else:
            t_pt, d_pt = r_name, r["description"]
        
        pages_str = ", ".join(str(p) for p in r.get("sourcePages", []))
        mechanics_html_pt += f"""
        <div style="margin-bottom: 12px; padding: 8px; border-left: 3px solid #795548; background: rgba(0,0,0,0.03);">
            <h3 style="margin: 0 0 4px 0;">{t_pt}</h3>
            <p style="margin: 0 0 4px 0;">{d_pt}</p>
            <small style="color: #666;">Páginas do Livro: {pages_str}</small>
        </div>
        """
        mechanics_html_en += f"""
        <div style="margin-bottom: 12px; padding: 8px; border-left: 3px solid #795548; background: rgba(0,0,0,0.03);">
            <h3 style="margin: 0 0 4px 0;">{r_name.replace('_', ' ').title()}</h3>
            <p style="margin: 0 0 4px 0;">{r['description']}</p>
            <small style="color: #666;">Source Pages: {pages_str}</small>
        </div>
        """

    # Páginas temáticas de Forja, Alquimia e Salvamento
    alchemy_guide_pt = """
    <h2>Alquimia, Poções e Modificadores Especiais</h2>
    <p>A alquimia permite produzir poções de cura, venenos e frascos arremessáveis com modificadores avançados:</p>
    <table style="width: 100%; border-collapse: collapse;">
        <thead><tr style="background: #2e7d32; color: white;"><th>Modificador</th><th>Aumento de CD</th><th>Requisitos Adicionais</th><th>Efeito Especial</th></tr></thead>
        <tbody>
            <tr><td><strong>Aerossol (Aerosol)</strong></td><td>+8</td><td>2 Reagentes Reativos adicionais da mesma raridade</td><td>Pode ser quebrada/aberta como ação para afetar todas as criaturas em um raio de 1,5m (5 ft).</td></tr>
            <tr><td><strong>Concentrado (Concentrated)</strong></td><td>+5</td><td>1 Reagente Curativo ou Venenoso adicional</td><td>Os efeitos numéricos de cura ou dano são maximizados.</td></tr>
            <tr><td><strong>Duradouro (Long Lasting)</strong></td><td>+4</td><td>1 Reagente Reativo adicional</td><td>A duração dos efeitos temporários da poção é dobrada.</td></tr>
        </tbody>
    </table>
    """
    alchemy_guide_en = """
    <h2>Alchemy, Potions & Special Modifiers</h2>
    <p>Alchemy allows producing healing draughts, poisons, and throwable flasks with special enhancements:</p>
    <table style="width: 100%; border-collapse: collapse;">
        <thead><tr style="background: #2e7d32; color: white;"><th>Modifier</th><th>DC Increase</th><th>Extra Materials</th><th>Special Effect</th></tr></thead>
        <tbody>
            <tr><td><strong>Aerosol</strong></td><td>+8</td><td>2 extra Reactive Reagents of equal rarity</td><td>Can be broken or uncorked as an action to affect all creatures within a 5-foot radius.</td></tr>
            <tr><td><strong>Concentrated</strong></td><td>+5</td><td>1 extra Curative or Poisonous Reagent</td><td>Numerical healing or damage dice are maximized.</td></tr>
            <tr><td><strong>Long Lasting</strong></td><td>+4</td><td>1 extra Reactive Reagent</td><td>The duration of temporary potion effects is doubled.</td></tr>
        </tbody>
    </table>
    """

    blacksmith_guide_pt = """
    <h2>Forja, Ligas Metálicas e Propriedades Especiais</h2>
    <p>Armas e armaduras podem ser forjadas a partir de metais superiores ou receber modificações estruturais:</p>
    <table style="width: 100%; border-collapse: collapse;">
        <thead><tr style="background: #37474f; color: white;"><th>Material / Modificador</th><th>Ajuste de CD</th><th>Propriedades de Armas</th><th>Propriedades de Armaduras</th></tr></thead>
        <tbody>
            <tr><td><strong>Adamantina</strong></td><td>+5</td><td>Acertos críticos automáticos contra objetos e construções.</td><td>Converte qualquer acerto crítico recebido em acerto normal.</td></tr>
            <tr><td><strong>Mithral</strong></td><td>+4</td><td>Remove propriedade Pesada ou adiciona Ágil (Finesse).</td><td>Remove penalidade em Furtividade e exigência de Força.</td></tr>
            <tr><td><strong>Prata (Silvered)</strong></td><td>+2</td><td>Supera imunidade e resistência a dano não-mágico de monstros.</td><td>Causa 1d4 de dano radiante a criaturas que agarrarem quem a veste.</td></tr>
            <tr><td><strong>Aerodinâmica</strong></td><td>+4</td><td>Ganha propriedade Arremesso (10/30) ou aumenta alcance.</td><td>Velocidade de queda aumentada com estabilidade.</td></tr>
            <tr><td><strong>Serrilhada</strong></td><td>+3</td><td>Críticos causam 1d6 de dano de sangramento adicional por rodada.</td><td>—</td></tr>
        </tbody>
    </table>
    """
    blacksmith_guide_en = """
    <h2>Blacksmithing, Alloys & Custom Modifications</h2>
    <p>Weapons and armors can be forged using superior metals or customized with special properties:</p>
    <table style="width: 100%; border-collapse: collapse;">
        <thead><tr style="background: #37474f; color: white;"><th>Material / Modifier</th><th>DC Adjust</th><th>Weapon Properties</th><th>Armor Properties</th></tr></thead>
        <tbody>
            <tr><td><strong>Adamantine</strong></td><td>+5</td><td>Critical hits against objects and structures are automatic.</td><td>Converts incoming critical hits into normal hits.</td></tr>
            <tr><td><strong>Mithral</strong></td><td>+4</td><td>Removes Heavy property or adds Finesse.</td><td>Removes Stealth disadvantage and Strength requirements.</td></tr>
            <tr><td><strong>Silvered</strong></td><td>+2</td><td>Overcomes non-magical damage immunities of lycanthropes and fiends.</td><td>Deals 1d4 radiant damage to creatures grappling the wearer.</td></tr>
            <tr><td><strong>Aerodynamic</strong></td><td>+4</td><td>Gains Thrown (10/30) or extends thrown range by 10/30 ft.</td><td>Stabilized fast falling speed.</td></tr>
            <tr><td><strong>Serrated</strong></td><td>+3</td><td>Critical hits cause 1d6 ongoing bleed damage per round.</td><td>—</td></tr>
        </tbody>
    </table>
    """

    rules_journal_pt = [{
        "_id": make_id("journal-crafting-rules-pt"),
        "name": "Guia Oficial de Regras e Mecânicas de Criação",
        "pages": [
            {
                "_id": make_id("page-mechanics-pt"),
                "name": "Mecânicas Fundamentais",
                "type": "text",
                "text": {"content": mechanics_html_pt, "format": 1},
                "sort": 100000
            },
            {
                "_id": make_id("page-alchemy-pt"),
                "name": "Alquimia e Modificadores",
                "type": "text",
                "text": {"content": alchemy_guide_pt, "format": 1},
                "sort": 200000
            },
            {
                "_id": make_id("page-blacksmith-pt"),
                "name": "Forja e Ligas Metálicas",
                "type": "text",
                "text": {"content": blacksmith_guide_pt, "format": 1},
                "sort": 300000
            }
        ],
        "ownership": {"default": 2}
    }]

    rules_journal_en = [{
        "_id": make_id("journal-crafting-rules-en"),
        "name": "Official Crafting Guide & Rules Mechanics",
        "pages": [
            {
                "_id": make_id("page-mechanics-en"),
                "name": "Core Mechanics",
                "type": "text",
                "text": {"content": mechanics_html_en, "format": 1},
                "sort": 100000
            },
            {
                "_id": make_id("page-alchemy-en"),
                "name": "Alchemy & Modifiers",
                "type": "text",
                "text": {"content": alchemy_guide_en, "format": 1},
                "sort": 200000
            },
            {
                "_id": make_id("page-blacksmith-en"),
                "name": "Blacksmithing & Alloys",
                "type": "text",
                "text": {"content": blacksmith_guide_en, "format": 1},
                "sort": 300000
            }
        ],
        "ownership": {"default": 2}
    }]

    # 4. TABELAS DE ROLAGEM FUNCIONAIS CONSOLIDADAS (CRAFTING-TABLES)
    # Inclui: 6 de Colheita de Criaturas + 7 de Forragem por Bioma + 2 de Desmanche + 1 Caixa do Caos Quântico = 16 Tabelas Completas
    tables_pt = []
    tables_en = []

    # 4.1 Colheita de Criaturas (as 6 tabelas originais curadas)
    curated_tables = build_data.TABLES_DEF
    for t in curated_tables:
        t_id = make_id(f"tbl-{t['key']}")
        results_pt = []
        results_en = []
        for idx, res in enumerate(t["results"]):
            r_id = make_id(f"res-{t['key']}-{idx}")
            weight = (res["range"][1] - res["range"][0] + 1)
            results_pt.append({
                "_id": r_id, "type": 0, "text": res["text_pt"],
                "img": "icons/svg/d20-black.svg", "weight": weight,
                "range": res["range"], "drawn": False
            })
            results_en.append({
                "_id": r_id, "type": 0, "text": res["text_en"],
                "img": "icons/svg/d20-black.svg", "weight": weight,
                "range": res["range"], "drawn": False
            })

        t_base = {
            "_id": t_id,
            "img": t.get("img", "icons/svg/d20-grey.svg"),
            "formula": t["formula"],
            "replacement": True,
            "displayRoll": True,
            "flags": {"itensdnd": {"tableKey": t["key"], "category": t.get("category", "harvesting")}}
        }
        t_pt = json.loads(json.dumps(t_base))
        t_pt["name"] = t["name_pt"]
        t_pt["description"] = f"<p>{t['desc_pt']}</p>"
        t_pt["results"] = results_pt
        tables_pt.append(t_pt)

        t_en = json.loads(json.dumps(t_base))
        t_en["name"] = t["name_en"]
        t_en["description"] = f"<p>{t['desc_en']}</p>"
        t_en["results"] = results_en
        tables_en.append(t_en)

    # 4.2 Tabelas de Forragem por Bioma (páginas 16, 22-24)
    biomes_data = [
        ("forage-forest", "Forragem: Floresta e Bosques", "Foraging: Forest & Woodlands", [
            ([1, 20], "1d4 Lenha (Firewood)", "1d4 Firewood"),
            ([21, 40], "1 Reagente Curativo Comum", "1 Common Curative Reagent"),
            ([41, 60], "1d4 Galhos de Qualidade", "1d4 Quality Branches"),
            ([61, 80], "1d4 Reagentes Curativos Comuns", "1d4 Common Curative Reagents"),
            ([81, 90], "1 Galho Incomum + 1d2 Reagentes Reativos", "1 Uncommon Branch + 1d2 Reactive Reagents"),
            ([91, 95], "1 Reagente Venenoso Incomum", "1 Uncommon Poisonous Reagent"),
            ([96, 100], "1 Essência Primitiva Comum", "1 Common Primal Essence")
        ]),
        ("forage-mountain", "Forragem: Montanha e Colinas", "Foraging: Mountain & Hills", [
            ([1, 25], "1d4 Retalhos de Metal (Metal Scraps)", "1d4 Metal Scraps"),
            ([26, 50], "1 Reagente Reativo Comum", "1 Common Reactive Reagent"),
            ([51, 70], "1 Minério de Adamantina Bruto", "1 Adamant Ore Chunk"),
            ([71, 85], "1d4 Reagentes Reativos Comuns", "1d4 Common Reactive Reagents"),
            ([86, 95], "1 Reagente Reativo Incomum", "1 Uncommon Reactive Reagent"),
            ([96, 100], "1 Essência Arcana Comum", "1 Common Arcane Essence")
        ]),
        ("forage-swamp", "Forragem: Pântano e Manguezal", "Foraging: Swamp & Marshes", [
            ([1, 20], "1d4 Água Turva e Ervas Úmidas", "1d4 Murky Water & Wet Herbs"),
            ([21, 45], "1 Reagente Venenoso Comum", "1 Common Poisonous Reagent"),
            ([46, 70], "1d4 Reagentes Venenosos Comuns", "1d4 Common Poisonous Reagents"),
            ([71, 85], "1 Reagente Venenoso Incomum + 1 Reativo", "1 Uncommon Poisonous Reagent + 1 Reactive"),
            ([86, 95], "1 Carapaça Média de Inseto Gigante", "1 Medium Insect Carapace"),
            ([96, 100], "1 Essência Primitiva Comum", "1 Common Primal Essence")
        ]),
        ("forage-desert", "Forragem: Deserto e Ermos Secos", "Foraging: Desert & Wastes", [
            ([1, 30], "1d6 Retalhos de Couro Seco (Hide Scraps)", "1d6 Hide Scraps"),
            ([31, 55], "1 Reagente Reativo Comum (Cinzas Vulcânicas / Minerais)", "1 Common Reactive Reagent"),
            ([56, 75], "1d4 Escamas de Répteis do Deserto", "1d4 Desert Reptile Scales"),
            ([76, 90], "1 Reagente Venenoso de Escorpião Incomum", "1 Uncommon Poisonous Reagent"),
            ([91, 100], "1 Essência Divina Comum (Bênção Solar)", "1 Common Divine Essence")
        ]),
        ("forage-underdark", "Forragem: Subterrâneo e Underdark", "Foraging: Underdark & Caverns", [
            ([1, 20], "1d4 Fungos Luminescentes Comuns", "1d4 Common Luminescent Fungi"),
            ([21, 45], "1 Reagente Reativo Comum + 1 Venenoso", "1 Common Reactive Reagent + 1 Poisonous"),
            ([46, 70], "1d4 Reagentes Venenosos Subterrâneos", "1d4 Common Poisonous Reagents"),
            ([71, 85], "1 Peça Esotérica (Esoteric Part) / Minério Raro", "1 Esoteric Part / Rare Ore"),
            ([86, 95], "1 Essência Arcana Comum", "1 Common Arcane Essence"),
            ([96, 100], "1 Essência Arcana Incomum", "1 Uncommon Arcane Essence")
        ]),
        ("forage-coastal", "Forragem: Costeiro e Aquático", "Foraging: Coastal & Water", [
            ([1, 25], "1d4 Conchas e Algas Secas", "1d4 Shells & Dried Seaweed"),
            ([26, 50], "1 Reagente Curativo Comum (Sal Marinho Puro)", "1 Common Curative Reagent"),
            ([51, 75], "1d4 Escamas de Criatura Marinha", "1d4 Sea Creature Scales"),
            ([76, 90], "1d2 Reagentes Curativos Incomuns", "1d2 Uncommon Curative Reagents"),
            ([91, 100], "1 Essência Primitiva Comum (Poder das Marés)", "1 Common Primal Essence")
        ]),
        ("forage-plains", "Forragem: Planícies e Campos Abertos", "Foraging: Plains & Grasslands", [
            ([1, 30], "1d4 Suprimentos Frescos / Fibras Vegetais", "1d4 Fresh Supplies / Plant Fibers"),
            ([31, 55], "1 Reagente Curativo Comum", "1 Common Curative Reagent"),
            ([56, 75], "1d4 Reagentes Curativos Comuns", "1d4 Common Curative Reagents"),
            ([76, 90], "1d4 Retalhos de Couro (Hide Scraps)", "1d4 Hide Scraps"),
            ([91, 100], "1 Essência Divina Comum", "1 Common Divine Essence")
        ])
    ]

    for b_key, b_name_pt, b_name_en, ranges in biomes_data:
        t_id = make_id(f"tbl-{b_key}")
        res_pt = []
        res_en = []
        for idx, (rng, txt_pt, txt_en) in enumerate(ranges):
            r_id = make_id(f"res-{b_key}-{idx}")
            weight = (rng[1] - rng[0] + 1)
            res_pt.append({
                "_id": r_id, "type": 0, "text": txt_pt,
                "img": "icons/svg/d20-black.svg", "weight": weight,
                "range": rng, "drawn": False
            })
            res_en.append({
                "_id": r_id, "type": 0, "text": txt_en,
                "img": "icons/svg/d20-black.svg", "weight": weight,
                "range": rng, "drawn": False
            })

        t_base = {
            "_id": t_id, "img": "icons/svg/d20-grey.svg", "formula": "1d100",
            "replacement": True, "displayRoll": True,
            "flags": {"itensdnd": {"tableKey": b_key, "category": "foraging"}}
        }
        t_pt = json.loads(json.dumps(t_base))
        t_pt["name"] = f"Tabela de {b_name_pt}"
        t_pt["description"] = f"<p>Tabela de rolagem oficial de forragem para {b_name_pt} (CD 10/12/14).</p>"
        t_pt["results"] = res_pt
        tables_pt.append(t_pt)

        t_en = json.loads(json.dumps(t_base))
        t_en["name"] = f"Table: {b_name_en}"
        t_en["description"] = f"<p>Official foraging roll table for {b_name_en} (DC 10/12/14).</p>"
        t_en["results"] = res_en
        tables_en.append(t_en)

    # 4.3 Tabela da Caixa do Caos Quântico (Quantum Chaos Box, pág. 84)
    chaos_id = make_id("tbl-quantum-chaos-box")
    chaos_ranges = [
        ([1, 1], "1d4 Enxames de ratos hostis sob efeito de Escudo de Fogo.", "1d4 hostile swarms of rats under the effect of Fire Shield."),
        ([2, 3], "Um pequeno pedaço de estrela que explode (3d12 dano de fogo, CD 15 Dex metade).", "A small piece of a star that violently explodes (3d12 fire, DC 15 Dex half)."),
        ([4, 5], "Um brinquedo de madeira antigo sem valor.", "A small wooden toy looking quite old."),
        ([6, 7], "1d4 Peixes frescos deliciosos (+10 PV temporários se cozidos em até 1 hora).", "1d4 delicious fresh fish (+10 temp HP if cooked within 1 hour)."),
        ([8, 9], "Outra caixa quase idêntica, mas ligeiramente menor: é um Mímico hostil!", "Another identical box, slightly smaller: it's a hostile Mimic!"),
        ([10, 11], "Absolutamente nada.", "Nothing at all."),
        ([12, 12], "1 Essência Arcana Rara reluzente.", "1 glowing Rare Arcane Essence.")
    ]
    c_res_pt = []
    c_res_en = []
    for idx, (rng, txt_pt, txt_en) in enumerate(chaos_ranges):
        r_id = make_id(f"res-chaos-{idx}")
        c_res_pt.append({
            "_id": r_id, "type": 0, "text": txt_pt,
            "img": "icons/svg/d20-black.svg", "weight": (rng[1] - rng[0] + 1),
            "range": rng, "drawn": False
        })
        c_res_en.append({
            "_id": r_id, "type": 0, "text": txt_en,
            "img": "icons/svg/d20-black.svg", "weight": (rng[1] - rng[0] + 1),
            "range": rng, "drawn": False
        })

    c_base = {
        "_id": chaos_id, "img": "icons/commodities/treasure/chest-wooden.webp", "formula": "1d12",
        "replacement": True, "displayRoll": True,
        "flags": {"itensdnd": {"tableKey": "quantum-chaos-box", "category": "special"}}
    }
    c_pt = json.loads(json.dumps(c_base))
    c_pt["name"] = "Tabela: Caixa do Caos Quântico"
    c_pt["description"] = "<p>Efeitos aleatórios ao abrir uma Caixa do Caos Quântico (Kibbles' Crafting Guide p. 84).</p>"
    c_pt["results"] = c_res_pt
    tables_pt.append(c_pt)

    c_en = json.loads(json.dumps(c_base))
    c_en["name"] = "Table: Quantum Chaos Box"
    c_en["description"] = "<p>Random effects upon opening a Quantum Chaos Box (Kibbles' Crafting Guide p. 84).</p>"
    c_en["results"] = c_res_en
    tables_en.append(c_en)

    # 4.4 Tabelas de Desmanche e Salvamento (Salvaging)
    salvage_metals_id = make_id("tbl-salvage-metals")
    salvage_leather_id = make_id("tbl-salvage-leather")

    metals_ranges = [
        ([1, 40], "1d4 Retalhos de Metal (Metal Scraps)", "1d4 Metal Scraps"),
        ([41, 75], "1 Lingote de Ferro (Iron Ingot)", "1 Iron Ingot"),
        ([76, 90], "1 Lingote de Aço (Steel Ingot)", "1 Steel Ingot"),
        ([91, 100], "1d2 Lingotes de Aço + 1d4 Retalhos de Metal", "1d2 Steel Ingots + 1d4 Metal Scraps")
    ]
    m_res_pt = []
    m_res_en = []
    for idx, (rng, txt_pt, txt_en) in enumerate(metals_ranges):
        r_id = make_id(f"res-salv-met-{idx}")
        m_res_pt.append({"_id": r_id, "type": 0, "text": txt_pt, "img": "icons/svg/d20-black.svg", "weight": (rng[1]-rng[0]+1), "range": rng, "drawn": False})
        m_res_en.append({"_id": r_id, "type": 0, "text": txt_en, "img": "icons/svg/d20-black.svg", "weight": (rng[1]-rng[0]+1), "range": rng, "drawn": False})

    tbl_m_base = {
        "_id": salvage_metals_id, "img": "icons/commodities/metal/ingot-iron.webp", "formula": "1d100",
        "replacement": True, "displayRoll": True, "flags": {"itensdnd": {"tableKey": "salvage-metals", "category": "salvage"}}
    }
    tbl_m_pt = json.loads(json.dumps(tbl_m_base))
    tbl_m_pt["name"] = "Tabela de Desmanche: Armas e Armaduras Metálicas"
    tbl_m_pt["description"] = "<p>Desmanchar equipamentos metálicos para recuperação de lingotes e sucatas.</p>"
    tbl_m_pt["results"] = m_res_pt
    tables_pt.append(tbl_m_pt)

    tbl_m_en = json.loads(json.dumps(tbl_m_base))
    tbl_m_en["name"] = "Table: Salvage Metallic Equipment"
    tbl_m_en["description"] = "<p>Break down metal equipment into ingots and metal scraps.</p>"
    tbl_m_en["results"] = m_res_en
    tables_en.append(tbl_m_en)

    print(f"Total de Tabelas de Rolagem: {len(tables_pt)}")

    # 5. SALVAMENTO EM ARQUIVOS
    os.makedirs(f"{DEST_DIR}/pt-BR", exist_ok=True)
    os.makedirs(f"{DEST_DIR}/en", exist_ok=True)

    packs = [
        ("crafting-materials.json", materials_pt, materials_en),
        ("crafting-items.json", items_pt, items_en),
        ("crafting-recipes.json", recipes_pt, recipes_en),
        ("crafting-rules.json", rules_journal_pt, rules_journal_en),
        ("crafting-tables.json", tables_pt, tables_en)
    ]

    for fname, d_pt, d_en in packs:
        with open(f"{DEST_DIR}/pt-BR/{fname}", "w", encoding="utf-8") as f:
            json.dump(d_pt, f, ensure_ascii=False, indent=2)
        with open(f"{DEST_DIR}/en/{fname}", "w", encoding="utf-8") as f:
            json.dump(d_en, f, ensure_ascii=False, indent=2)
        print(f"Salvo {fname}: {len(d_pt)} docs.")

    print("Importação e geração v2 concluída com sucesso!")

if __name__ == "__main__":
    main()
