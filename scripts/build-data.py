#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build-data.py
Script gerador de dados para os compêndios do módulo itensdnd.
Gera os arquivos JSON bilíngues (pt-BR e en) para:
- crafting-materials.json
- crafting-recipes.json
- crafting-tables.json
- crafting-rules.json
"""

import json
import hashlib
import os

def make_id(key: str) -> str:
    """Gera um ID alfanumérico determinístico de 16 caracteres compatível com Foundry VTT."""
    h = hashlib.md5(key.encode('utf-8')).hexdigest()
    # Garantir que começa com letra ou número e tem 16 chars
    return h[:16]

# --- 1. MATERIAIS (CRAFTING MATERIALS) ---
MATERIALS_DEF = [
    # Reagentes Curativos
    {
        "key": "reagent-curative-common",
        "name_pt": "Reagente Curativo Comum",
        "name_en": "Common Curative Reagent",
        "desc_pt": "Ingrediente herbáceo ou biológico com propriedades curativas simples. Usado principalmente em poções de cura e bálsamos.",
        "desc_en": "An herbal or biological ingredient with simple healing properties. Used primarily in healing potions and balms.",
        "rarity": "common", "price": 5, "weight": 0.1,
        "img": "icons/consumables/potions/potion-tube-corked-green.webp",
        "category": "reagent", "reagentType": "curative"
    },
    {
        "key": "reagent-curative-uncommon",
        "name_pt": "Reagente Curativo Incomum",
        "name_en": "Uncommon Curative Reagent",
        "desc_pt": "Ingrediente restaurador potente colhido em ambientes mágicos ou de feras raras. Usado em Poções de Cura Maior e antídotos.",
        "desc_en": "Potent restorative ingredient harvested from magical environments or rare beasts. Used in Greater Healing Potions and antidotes.",
        "rarity": "uncommon", "price": 20, "weight": 0.1,
        "img": "icons/consumables/potions/potion-tube-corked-green.webp",
        "category": "reagent", "reagentType": "curative"
    },
    {
        "key": "reagent-curative-rare",
        "name_pt": "Reagente Curativo Raro",
        "name_en": "Rare Curative Reagent",
        "desc_pt": "Ingrediente com vitalidade mágica condensada, colhido de seres veneráveis ou plantas ancestrais.",
        "desc_en": "Ingredient containing condensed magical vitality, harvested from ancient beings or primeval plants.",
        "rarity": "rare", "price": 100, "weight": 0.1,
        "img": "icons/consumables/potions/potion-tube-corked-green.webp",
        "category": "reagent", "reagentType": "curative"
    },
    {
        "key": "reagent-curative-very-rare",
        "name_pt": "Reagente Curativo Muito Raro",
        "name_en": "Very Rare Curative Reagent",
        "desc_pt": "Substância regenerativa lendária capaz de restaurar órgãos e desfazer as piores aflições.",
        "desc_en": "Legendary regenerative substance capable of restoring organs and lifting dire afflictions.",
        "rarity": "veryRare", "price": 500, "weight": 0.1,
        "img": "icons/consumables/potions/potion-tube-corked-green.webp",
        "category": "reagent", "reagentType": "curative"
    },
    {
        "key": "reagent-curative-legendary",
        "name_pt": "Reagente Curativo Lendário",
        "name_en": "Legendary Curative Reagent",
        "desc_pt": "Gota mítica de essência de fênix ou lótus astral; capaz de desafiar a própria morte.",
        "desc_en": "Mythical drop of phoenix tear or astral lotus; capable of defying death itself.",
        "rarity": "legendary", "price": 2500, "weight": 0.1,
        "img": "icons/consumables/potions/potion-tube-corked-green.webp",
        "category": "reagent", "reagentType": "curative"
    },

    # Reagentes Venenosos
    {
        "key": "reagent-poisonous-common",
        "name_pt": "Reagente Venenoso Comum",
        "name_en": "Common Poisonous Reagent",
        "desc_pt": "Toxina comum extraída de fungos, cobras ou folhas tóxicas.",
        "desc_en": "Common toxin extracted from fungi, serpents, or poisonous plants.",
        "rarity": "common", "price": 5, "weight": 0.1,
        "img": "icons/consumables/potions/potion-tube-corked-purple.webp",
        "category": "reagent", "reagentType": "poisonous"
    },
    {
        "key": "reagent-poisonous-uncommon",
        "name_pt": "Reagente Venenoso Incomum",
        "name_en": "Uncommon Poisonous Reagent",
        "desc_pt": "Peçonha corrosiva ou neurotóxica colhida de escorpiões gigantes ou plantas carnívoras.",
        "desc_en": "Corrosive or neurotoxic venom harvested from giant scorpions or predatory plants.",
        "rarity": "uncommon", "price": 20, "weight": 0.1,
        "img": "icons/consumables/potions/potion-tube-corked-purple.webp",
        "category": "reagent", "reagentType": "poisonous"
    },
    {
        "key": "reagent-poisonous-rare",
        "name_pt": "Reagente Venenoso Raro",
        "name_en": "Rare Poisonous Reagent",
        "desc_pt": "Veneno altamente letal de criaturas como manticoras, hidras e wyverns.",
        "desc_en": "Highly lethal poison from creatures such as manticores, hydras, and wyverns.",
        "rarity": "rare", "price": 100, "weight": 0.1,
        "img": "icons/consumables/potions/potion-tube-corked-purple.webp",
        "category": "reagent", "reagentType": "poisonous"
    },
    {
        "key": "reagent-poisonous-very-rare",
        "name_pt": "Reagente Venenoso Muito Raro",
        "name_en": "Very Rare Poisonous Reagent",
        "desc_pt": "Toxina sobrenatural colhida de demônios venenosos, dragões verdes anciãos ou abominações.",
        "desc_en": "Supernatural toxin harvested from venomous fiends, ancient green dragons, or horrors.",
        "rarity": "veryRare", "price": 500, "weight": 0.1,
        "img": "icons/consumables/potions/potion-tube-corked-purple.webp",
        "category": "reagent", "reagentType": "poisonous"
    },
    {
        "key": "reagent-poisonous-legendary",
        "name_pt": "Reagente Venenoso Lendário",
        "name_en": "Legendary Poisonous Reagent",
        "desc_pt": "Veneno supremo capaz de corromper alma, matéria e carne imortal.",
        "desc_en": "Supreme venom capable of corrupting soul, matter, and immortal flesh.",
        "rarity": "legendary", "price": 2500, "weight": 0.1,
        "img": "icons/consumables/potions/potion-tube-corked-purple.webp",
        "category": "reagent", "reagentType": "poisonous"
    },

    # Reagentes Reativos
    {
        "key": "reagent-reactive-common",
        "name_pt": "Reagente Reativo Comum",
        "name_en": "Common Reactive Reagent",
        "desc_pt": "Substância volátil básica, enxofre ou sais que catalisam reações alquímicas e explosivas.",
        "desc_en": "Volatile basic substance, sulfur, or mineral salts that catalyze chemical reactions.",
        "rarity": "common", "price": 5, "weight": 0.1,
        "img": "icons/consumables/potions/potion-tube-corked-red.webp",
        "category": "reagent", "reagentType": "reactive"
    },
    {
        "key": "reagent-reactive-uncommon",
        "name_pt": "Reagente Reativo Incomum",
        "name_en": "Uncommon Reactive Reagent",
        "desc_pt": "Composto altamente instável extraído de glândulas de fogo ou gelo de monstros.",
        "desc_en": "Highly unstable compound extracted from fire or frost glands of monsters.",
        "rarity": "uncommon", "price": 20, "weight": 0.1,
        "img": "icons/consumables/potions/potion-tube-corked-red.webp",
        "category": "reagent", "reagentType": "reactive"
    },
    {
        "key": "reagent-reactive-rare",
        "name_pt": "Reagente Reativo Raro",
        "name_en": "Rare Reactive Reagent",
        "desc_pt": "Catalisador energético concentrado encontrado em resíduos elementais puros.",
        "desc_en": "Concentrated energetic catalyst found in pure elemental remnants.",
        "rarity": "rare", "price": 100, "weight": 0.1,
        "img": "icons/consumables/potions/potion-tube-corked-red.webp",
        "category": "reagent", "reagentType": "reactive"
    },
    {
        "key": "reagent-reactive-very-rare",
        "name_pt": "Reagente Reativo Muito Raro",
        "name_en": "Very Rare Reactive Reagent",
        "desc_pt": "Substância elemental primordial com tremendo poder cinético e térmico.",
        "desc_en": "Primordial elemental substance bearing tremendous kinetic and thermal power.",
        "rarity": "veryRare", "price": 500, "weight": 0.1,
        "img": "icons/consumables/potions/potion-tube-corked-red.webp",
        "category": "reagent", "reagentType": "reactive"
    },
    {
        "key": "reagent-reactive-legendary",
        "name_pt": "Reagente Reativo Lendário",
        "name_en": "Legendary Reactive Reagent",
        "desc_pt": "Célula primordial pura de caos e calor concentrado, extraída de tempestades astrais.",
        "desc_en": "Pure primordial spark of concentrated chaos and heat from astral storms.",
        "rarity": "legendary", "price": 2500, "weight": 0.1,
        "img": "icons/consumables/potions/potion-tube-corked-red.webp",
        "category": "reagent", "reagentType": "reactive"
    },

    # Essências Mágicas
    {
        "key": "essence-arcane-common",
        "name_pt": "Essência Arcana Comum",
        "name_en": "Common Arcane Essence",
        "desc_pt": "Centelha de pura magia formulada ou destilada. Usada em encantamentos e pergaminhos.",
        "desc_en": "Spark of pure formulated or distilled magic. Used in enchantments and scrolls.",
        "rarity": "common", "price": 15, "weight": 1.0,
        "img": "icons/magic/symbols/runes-star-blue.webp",
        "category": "essence", "essenceType": "arcane"
    },
    {
        "key": "essence-arcane-uncommon",
        "name_pt": "Essência Arcana Incomum",
        "name_en": "Uncommon Arcane Essence",
        "desc_pt": "Globo translúcido de poder arcano condensado de monstros mágicos de ND 5–10.",
        "desc_en": "Translucent orb of condensed arcane power from CR 5–10 magical creatures.",
        "rarity": "uncommon", "price": 60, "weight": 1.0,
        "img": "icons/magic/symbols/runes-star-blue.webp",
        "category": "essence", "essenceType": "arcane"
    },
    {
        "key": "essence-arcane-rare",
        "name_pt": "Essência Arcana Rara",
        "name_en": "Rare Arcane Essence",
        "desc_pt": "Poder arcano denso pulsando com energia espectral de alto nível.",
        "desc_en": "Dense arcane power pulsing with high-level spectral energy.",
        "rarity": "rare", "price": 300, "weight": 1.0,
        "img": "icons/magic/symbols/runes-star-blue.webp",
        "category": "essence", "essenceType": "arcane"
    },
    {
        "key": "essence-arcane-very-rare",
        "name_pt": "Essência Arcana Muito Rara",
        "name_en": "Very Rare Arcane Essence",
        "desc_pt": "Poder arcano puro retirado de arquimagos ou monstros cósmicos.",
        "desc_en": "Pure arcane power gathered from archmages or cosmic horrors.",
        "rarity": "veryRare", "price": 1500, "weight": 1.0,
        "img": "icons/magic/symbols/runes-star-blue.webp",
        "category": "essence", "essenceType": "arcane"
    },
    {
        "key": "essence-arcane-legendary",
        "name_pt": "Essência Arcana Lendária",
        "name_en": "Legendary Arcane Essence",
        "desc_pt": "Essência capaz de distorcer a urdidura e sustentar artefatos permanentes.",
        "desc_en": "Essence capable of bending the weave to sustain permanent artifacts.",
        "rarity": "legendary", "price": 7500, "weight": 1.0,
        "img": "icons/magic/symbols/runes-star-blue.webp",
        "category": "essence", "essenceType": "arcane"
    },

    # Essências Divinas
    {
        "key": "essence-divine-common",
        "name_pt": "Essência Divina Comum",
        "name_en": "Common Divine Essence",
        "desc_pt": "Fragmento de graça e radiância sagrada.",
        "desc_en": "Shard of grace and sacred radiance.",
        "rarity": "common", "price": 15, "weight": 1.0,
        "img": "icons/magic/holy/aura-light-teal.webp",
        "category": "essence", "essenceType": "divine"
    },
    {
        "key": "essence-divine-uncommon",
        "name_pt": "Essência Divina Incomum",
        "name_en": "Uncommon Divine Essence",
        "desc_pt": "Poder espiritual abençoado de celestiais menores ou servos devotos.",
        "desc_en": "Blessed spiritual power from lesser celestials or devoted servants.",
        "rarity": "uncommon", "price": 60, "weight": 1.0,
        "img": "icons/magic/holy/aura-light-teal.webp",
        "category": "essence", "essenceType": "divine"
    },
    {
        "key": "essence-divine-rare",
        "name_pt": "Essência Divina Rara",
        "name_en": "Rare Divine Essence",
        "desc_pt": "Luz celeste viva ou resíduo profano potente de planar venerável.",
        "desc_en": "Living celestial light or potent unholy remnant from a venerable planar entity.",
        "rarity": "rare", "price": 300, "weight": 1.0,
        "img": "icons/magic/holy/aura-light-teal.webp",
        "category": "essence", "essenceType": "divine"
    },

    # Essências Primitivas (Primal)
    {
        "key": "essence-primal-common",
        "name_pt": "Essência Primitiva Comum",
        "name_en": "Common Primal Essence",
        "desc_pt": "Poder cru da natureza, espíritos animais e elementos terrestres.",
        "desc_en": "Raw power of nature, animal spirits, and earthly elements.",
        "rarity": "common", "price": 15, "weight": 1.0,
        "img": "icons/magic/nature/crystal-green.webp",
        "category": "essence", "essenceType": "primal"
    },
    {
        "key": "essence-primal-uncommon",
        "name_pt": "Essência Primitiva Incomum",
        "name_en": "Uncommon Primal Essence",
        "desc_pt": "Força vital selvagem extraída de monstros predadores ou espíritos da floresta.",
        "desc_en": "Wild life force extracted from apex predators or woodland spirits.",
        "rarity": "uncommon", "price": 60, "weight": 1.0,
        "img": "icons/magic/nature/crystal-green.webp",
        "category": "essence", "essenceType": "primal"
    },
    {
        "key": "essence-primal-rare",
        "name_pt": "Essência Primitiva Rara",
        "name_en": "Rare Primal Essence",
        "desc_pt": "Vigor inabalável colhido de dragões ou forças titânicas.",
        "desc_en": "Unshakeable vigor harvested from dragons or titanic forces.",
        "rarity": "rare", "price": 300, "weight": 1.0,
        "img": "icons/magic/nature/crystal-green.webp",
        "category": "essence", "essenceType": "primal"
    },

    # Lingotes de Metal
    {
        "key": "ingot-iron",
        "name_pt": "Lingote de Ferro",
        "name_en": "Iron Ingot",
        "desc_pt": "Bloco de ferro bruto fundido (2 lbs). Utilizado para ferramentas, pregos e itens mundanos não bélicos.",
        "desc_en": "Block of smelted raw iron (2 lbs). Used for tools, nails, and non-combat mundane gear.",
        "rarity": "common", "price": 0.1, "weight": 2.0,
        "img": "icons/commodities/metal/ingot-iron.webp",
        "category": "ingot"
    },
    {
        "key": "ingot-steel",
        "name_pt": "Lingote de Aço",
        "name_en": "Steel Ingot",
        "desc_pt": "Liga de ferro e carbono de excelente tenacidade (2 lbs). O padrão para armas e armaduras de qualidade.",
        "desc_en": "Tough iron-carbon alloy (2 lbs). The universal standard for quality weapons and armor.",
        "rarity": "common", "price": 2, "weight": 2.0,
        "img": "icons/commodities/metal/ingot-grey.webp",
        "category": "ingot"
    },
    {
        "key": "ingot-silver",
        "name_pt": "Lingote de Prata",
        "name_en": "Silver Ingot",
        "desc_pt": "Prata refinada (2 lbs). Utilizada para pratear armas contra licantropos ou joalheria sagrada.",
        "desc_en": "Refined silver (2 lbs). Used for silvering weapons against lycanthropes or holy jewelry.",
        "rarity": "uncommon", "price": 10, "weight": 2.0,
        "img": "icons/commodities/metal/ingot-silver.webp",
        "category": "ingot"
    },
    {
        "key": "ingot-gold",
        "name_pt": "Lingote de Ouro",
        "name_en": "Gold Ingot",
        "desc_pt": "Ouro puro reluzente (2 lbs). Empregado em ornamentos, douramento e condutores arcanos.",
        "desc_en": "Gleaming pure gold (2 lbs). Used in ornamental gear, gilding, and arcane conduits.",
        "rarity": "uncommon", "price": 50, "weight": 2.0,
        "img": "icons/commodities/metal/ingot-gold.webp",
        "category": "ingot"
    },
    {
        "key": "ingot-mithral",
        "name_pt": "Lingote de Mithral",
        "name_en": "Mithral Ingot",
        "desc_pt": "Metal prateado extremamente leve e resistente (1 lb). Permite criar armaduras silenciosas e sem desvantagem em Furtividade.",
        "desc_en": "Extremely light and resilient silvery metal (1 lb). Crafts silent armors with no Stealth penalty.",
        "rarity": "rare", "price": 100, "weight": 1.0,
        "img": "icons/commodities/metal/ingot-silver.webp",
        "category": "ingot"
    },
    {
        "key": "ingot-adamantine",
        "name_pt": "Lingote de Adamantina",
        "name_en": "Adamantine Ingot",
        "desc_pt": "Um dos minerais mais duros conhecidos (2 lbs). Transforma acertos críticos em normais e garante golpes devastadores em objetos.",
        "desc_en": "One of the hardest known minerals (2 lbs). Turns critical hits into normal hits and destroys objects.",
        "rarity": "rare", "price": 100, "weight": 2.0,
        "img": "icons/commodities/metal/ingot-engraved-grey.webp",
        "category": "ingot"
    },

    # Couros e Peles
    {
        "key": "leather-scraps",
        "name_pt": "Retalhos de Couro",
        "name_en": "Leather Scraps",
        "desc_pt": "Pedaços menores de couro aproveitáveis para tiras, bainhas e reparos.",
        "desc_en": "Small leather cutouts useful for straps, sheaths, and field repairs.",
        "rarity": "common", "price": 0.1, "weight": 0.5,
        "img": "icons/commodities/leather/scrap-brown.webp",
        "category": "leather"
    },
    {
        "key": "leather-common",
        "name_pt": "Couro Comum",
        "name_en": "Common Leather",
        "desc_pt": "Pele curtida e tratada de gado ou animais médios. Base para armaduras leves.",
        "desc_en": "Tanned and cured hide from cattle or medium animals. Base for light armors.",
        "rarity": "common", "price": 1, "weight": 2.0,
        "img": "icons/commodities/leather/leather-roll-tan.webp",
        "category": "leather"
    },
    {
        "key": "hide-thick",
        "name_pt": "Pele Grossa",
        "name_en": "Thick Hide",
        "desc_pt": "Couro reforçado colhido de ursos, rinocerontes ou feras corpulentas.",
        "desc_en": "Reinforced thick pelt harvested from bears, rhinos, or sturdy beasts.",
        "rarity": "common", "price": 2, "weight": 4.0,
        "img": "icons/commodities/leather/fur-brown.webp",
        "category": "leather"
    },
    {
        "key": "hide-scaled",
        "name_pt": "Carapaça / Escamas",
        "name_en": "Scaled Hide / Carapace",
        "desc_pt": "Placas rígidas e escamas colhidas de répteis gigantes, monstros ou insetos colossais.",
        "desc_en": "Tough plates and scales harvested from giant reptiles, monstrosities, or insects.",
        "rarity": "uncommon", "price": 5, "weight": 3.0,
        "img": "icons/commodities/biological/scales-tan.webp",
        "category": "leather"
    },
    {
        "key": "hide-dragon-scale",
        "name_pt": "Escama de Dragão",
        "name_en": "Dragon Scale",
        "desc_pt": "Escama reluzente e impérvia recolhida de um dragão verdadeiro. Confere resistência elemental nativa.",
        "desc_en": "Gleaming impervious scale from a true dragon. Grants innate elemental protection.",
        "rarity": "rare", "price": 100, "weight": 5.0,
        "img": "icons/commodities/biological/scales-lizard-gold.webp",
        "category": "leather"
    },

    # Peças Mecânicas
    {
        "key": "parts-simple",
        "name_pt": "Peças Simples",
        "name_en": "Simple Parts",
        "desc_pt": "Pregos, engrenagens rudimentares, rebites e fios de ferro para engenhocas básicas.",
        "desc_en": "Nails, rudimentary gears, rivets, and iron wire for basic contraptions.",
        "rarity": "common", "price": 0.1, "weight": 0.5,
        "img": "icons/commodities/tech/gear-brass-brown.webp",
        "category": "parts"
    },
    {
        "key": "parts-fancy",
        "name_pt": "Peças Refinadas",
        "name_en": "Fancy Parts",
        "desc_pt": "Molas de precisão, engrenagens balanceadas e válvulas colhidas de construtos ou artífices habilidosos.",
        "desc_en": "Precision springs, balanced gears, and valves harvested from clockworks or skilled artisans.",
        "rarity": "uncommon", "price": 2, "weight": 1.0,
        "img": "icons/commodities/tech/cog-brass.webp",
        "category": "parts"
    },
    {
        "key": "parts-esoteric",
        "name_pt": "Peças Esotéricas",
        "name_en": "Esoteric Parts",
        "desc_pt": "Componentes cinéticos arcanos retirados de golens e mecanismos lendários.",
        "desc_en": "Arcane kinetic components salvaged from golems and legendary automata.",
        "rarity": "rare", "price": 20, "weight": 2.0,
        "img": "icons/commodities/tech/cog-steel.webp",
        "category": "parts"
    },

    # Tintas Mágicas e Frascos
    {
        "key": "magical-ink-common",
        "name_pt": "Tinta Mágica Comum",
        "name_en": "Common Magical Ink",
        "desc_pt": "Tinta encantada para cópia e criação de pergaminhos arcanos de nível 1.",
        "desc_en": "Enchanted ink for scribing and creating 1st level arcane scrolls.",
        "rarity": "common", "price": 10, "weight": 0.1,
        "img": "icons/tools/scribal/inkwell-quill-blue.webp",
        "category": "ink"
    },
    {
        "key": "magical-ink-uncommon",
        "name_pt": "Tinta Mágica Incomum",
        "name_en": "Uncommon Magical Ink",
        "desc_pt": "Tinta luminosa para transcrição de pergaminhos de nível 2 e 3.",
        "desc_en": "Luminous ink for transcribing 2nd and 3rd level scrolls.",
        "rarity": "uncommon", "price": 40, "weight": 0.1,
        "img": "icons/tools/scribal/inkwell-quill-blue.webp",
        "category": "ink"
    },
    {
        "key": "glass-vial",
        "name_pt": "Frasco de Vidro",
        "name_en": "Glass Vial",
        "desc_pt": "Recipiente de vidro hermético (4 oz) para poções, óleos e ácidos.",
        "desc_en": "Airtight glass bottle (4 oz) for potions, oils, and acids.",
        "rarity": "common", "price": 1, "weight": 0.1,
        "img": "icons/consumables/potions/bottle-empty.webp",
        "category": "container"
    }
]

# --- 2. RECEITAS (CRAFTING RECIPES) ---
RECIPES_DEF = [
    # Alquimia - Poções
    {
        "key": "recipe-potion-healing",
        "name_pt": "Receita: Poção de Cura",
        "name_en": "Recipe: Potion of Healing",
        "profession": "alchemy",
        "tool": "alchemist",
        "ability": ["int", "wis"],
        "materials": [
            {"key": "reagent-curative-common", "quantity": 3},
            {"key": "glass-vial", "quantity": 1}
        ],
        "time": 2, "checks": 1, "dc": 13,
        "rarity": "common", "value": "50 gp",
        "resultItem": "Potion of Healing",
        "img": "icons/consumables/potions/potion-tube-corked-red.webp"
    },
    {
        "key": "recipe-potion-climbing",
        "name_pt": "Receita: Poção de Escalar",
        "name_en": "Recipe: Potion of Climbing",
        "profession": "alchemy",
        "tool": "alchemist",
        "ability": ["int", "wis"],
        "materials": [
            {"key": "reagent-reactive-common", "quantity": 1},
            {"key": "reagent-poisonous-common", "quantity": 1},
            {"key": "reagent-reactive-uncommon", "quantity": 1},
            {"key": "glass-vial", "quantity": 1}
        ],
        "time": 2, "checks": 1, "dc": 14,
        "rarity": "common", "value": "85 gp",
        "resultItem": "Potion of Climbing",
        "img": "icons/consumables/potions/potion-tube-corked-brown.webp"
    },
    {
        "key": "recipe-potion-greater-healing",
        "name_pt": "Receita: Poção de Cura Maior",
        "name_en": "Recipe: Potion of Greater Healing",
        "profession": "alchemy",
        "tool": "alchemist",
        "ability": ["int", "wis"],
        "materials": [
            {"key": "reagent-curative-common", "quantity": 1},
            {"key": "reagent-curative-uncommon", "quantity": 2},
            {"key": "glass-vial", "quantity": 1}
        ],
        "time": 2, "checks": 1, "dc": 15,
        "rarity": "uncommon", "value": "150 gp",
        "resultItem": "Potion of Greater Healing",
        "img": "icons/consumables/potions/potion-tube-corked-red.webp"
    },
    {
        "key": "recipe-alchemists-fire",
        "name_pt": "Receita: Fogo Alquímico",
        "name_en": "Recipe: Alchemist's Fire",
        "profession": "alchemy",
        "tool": "alchemist",
        "ability": ["int", "wis"],
        "materials": [
            {"key": "reagent-reactive-common", "quantity": 2},
            {"key": "glass-vial", "quantity": 1}
        ],
        "time": 2, "checks": 1, "dc": 13,
        "rarity": "common", "value": "50 gp",
        "resultItem": "Alchemist's Fire",
        "img": "icons/consumables/potions/bottle-bulb-corked-fire-orange.webp"
    },
    {
        "key": "recipe-acid-vial",
        "name_pt": "Receita: Frasco de Ácido",
        "name_en": "Recipe: Acid Vial",
        "profession": "alchemy",
        "tool": "alchemist",
        "ability": ["int", "wis"],
        "materials": [
            {"key": "reagent-reactive-common", "quantity": 1},
            {"key": "reagent-poisonous-common", "quantity": 1},
            {"key": "glass-vial", "quantity": 1}
        ],
        "time": 2, "checks": 1, "dc": 12,
        "rarity": "common", "value": "25 gp",
        "resultItem": "Acid Vial",
        "img": "icons/consumables/potions/bottle-bulb-corked-green.webp"
    },
    {
        "key": "recipe-antitoxin",
        "name_pt": "Receita: Antídoto / Antitoxina",
        "name_en": "Recipe: Antitoxin",
        "profession": "alchemy",
        "tool": "alchemist",
        "ability": ["int", "wis"],
        "materials": [
            {"key": "reagent-curative-common", "quantity": 2},
            {"key": "reagent-poisonous-common", "quantity": 1},
            {"key": "glass-vial", "quantity": 1}
        ],
        "time": 2, "checks": 1, "dc": 13,
        "rarity": "common", "value": "50 gp",
        "resultItem": "Antitoxin",
        "img": "icons/consumables/potions/potion-tube-corked-blue.webp"
    },

    # Ferraria - Blacksmithing (Armas e Armaduras)
    {
        "key": "recipe-longsword",
        "name_pt": "Receita: Espada Longa",
        "name_en": "Recipe: Longsword",
        "profession": "blacksmithing",
        "tool": "smith",
        "ability": ["str"],
        "materials": [
            {"key": "ingot-steel", "quantity": 2},
            {"key": "leather-scraps", "quantity": 1}
        ],
        "time": 4, "checks": 2, "dc": 12,
        "rarity": "common", "value": "15 gp",
        "resultItem": "Longsword",
        "img": "icons/weapons/swords/sword-broad-steel.webp"
    },
    {
        "key": "recipe-greatsword",
        "name_pt": "Receita: Espadão",
        "name_en": "Recipe: Greatsword",
        "profession": "blacksmithing",
        "tool": "smith",
        "ability": ["str"],
        "materials": [
            {"key": "ingot-steel", "quantity": 4},
            {"key": "leather-scraps", "quantity": 2}
        ],
        "time": 6, "checks": 3, "dc": 13,
        "rarity": "common", "value": "50 gp",
        "resultItem": "Greatsword",
        "img": "icons/weapons/swords/greatsword-crossguard-steel.webp"
    },
    {
        "key": "recipe-shield-steel",
        "name_pt": "Receita: Escudo de Aço",
        "name_en": "Recipe: Steel Shield",
        "profession": "blacksmithing",
        "tool": "smith",
        "ability": ["str"],
        "materials": [
            {"key": "ingot-steel", "quantity": 2},
            {"key": "leather-scraps", "quantity": 1}
        ],
        "time": 4, "checks": 2, "dc": 11,
        "rarity": "common", "value": "10 gp",
        "resultItem": "Shield",
        "img": "icons/equipment/shield/heater-steel.webp"
    },
    {
        "key": "recipe-breastplate",
        "name_pt": "Receita: Peitoral de Aço",
        "name_en": "Recipe: Breastplate",
        "profession": "blacksmithing",
        "tool": "smith",
        "ability": ["str"],
        "materials": [
            {"key": "ingot-steel", "quantity": 6},
            {"key": "leather-common", "quantity": 2}
        ],
        "time": 14, "checks": 7, "dc": 14,
        "rarity": "common", "value": "400 gp",
        "resultItem": "Breastplate",
        "img": "icons/equipment/chest/breastplate-steel.webp"
    },
    {
        "key": "recipe-plate-armor",
        "name_pt": "Receita: Armadura de Placas",
        "name_en": "Recipe: Plate Armor",
        "profession": "blacksmithing",
        "tool": "smith",
        "ability": ["str"],
        "materials": [
            {"key": "ingot-steel", "quantity": 16},
            {"key": "leather-common", "quantity": 4}
        ],
        "time": 30, "checks": 15, "dc": 16,
        "rarity": "common", "value": "1500 gp",
        "resultItem": "Plate Armor",
        "img": "icons/equipment/chest/breastplate-metal-scaled-grey.webp"
    },

    # Encantamento - Enchanting
    {
        "key": "recipe-weapon-plus-one",
        "name_pt": "Encantamento: Arma +1",
        "name_en": "Enchantment: +1 Weapon",
        "profession": "enchanting",
        "tool": "arcana",
        "ability": ["int"],
        "materials": [
            {"key": "essence-arcane-uncommon", "quantity": 1},
            {"key": "essence-primal-uncommon", "quantity": 1}
        ],
        "time": 8, "checks": 4, "dc": 14,
        "rarity": "uncommon", "value": "500 gp",
        "resultItem": "Weapon +1",
        "img": "icons/weapons/swords/sword-winged-glow-blue.webp"
    },
    {
        "key": "recipe-armor-plus-one",
        "name_pt": "Encantamento: Armadura +1",
        "name_en": "Enchantment: +1 Armor",
        "profession": "enchanting",
        "tool": "arcana",
        "ability": ["int"],
        "materials": [
            {"key": "essence-arcane-rare", "quantity": 1},
            {"key": "essence-divine-rare", "quantity": 1}
        ],
        "time": 12, "checks": 6, "dc": 16,
        "rarity": "rare", "value": "1500 gp",
        "resultItem": "Armor +1",
        "img": "icons/equipment/chest/breastplate-engraved-gold.webp"
    },
    {
        "key": "recipe-bag-of-holding",
        "name_pt": "Receita: Bolsa Espaçosa (Bag of Holding)",
        "name_en": "Recipe: Bag of Holding",
        "profession": "enchanting",
        "tool": "arcana",
        "ability": ["int"],
        "materials": [
            {"key": "leather-common", "quantity": 2},
            {"key": "essence-arcane-uncommon", "quantity": 1}
        ],
        "time": 6, "checks": 3, "dc": 14,
        "rarity": "uncommon", "value": "500 gp",
        "resultItem": "Bag of Holding",
        "img": "icons/containers/bags/sack-leather-brown.webp"
    },

    # Trabalho em Couro - Leatherworking
    {
        "key": "recipe-leather-armor",
        "name_pt": "Receita: Armadura de Couro",
        "name_en": "Recipe: Leather Armor",
        "profession": "leatherworking",
        "tool": "leatherworker",
        "ability": ["dex"],
        "materials": [
            {"key": "leather-common", "quantity": 2}
        ],
        "time": 4, "checks": 2, "dc": 11,
        "rarity": "common", "value": "10 gp",
        "resultItem": "Leather Armor",
        "img": "icons/equipment/chest/vest-leather-studded.webp"
    },
    {
        "key": "recipe-studded-leather",
        "name_pt": "Receita: Couro Batido",
        "name_en": "Recipe: Studded Leather Armor",
        "profession": "leatherworking",
        "tool": "leatherworker",
        "ability": ["dex"],
        "materials": [
            {"key": "leather-common", "quantity": 3},
            {"key": "parts-simple", "quantity": 2}
        ],
        "time": 8, "checks": 4, "dc": 13,
        "rarity": "common", "value": "45 gp",
        "resultItem": "Studded Leather Armor",
        "img": "icons/equipment/chest/vest-leather-studded.webp"
    },

    # Engenharia e Geringonças - Tinkering
    {
        "key": "recipe-hunting-trap",
        "name_pt": "Receita: Armadilha de Caça",
        "name_en": "Recipe: Hunting Trap",
        "profession": "tinkering",
        "tool": "tinker",
        "ability": ["int"],
        "materials": [
            {"key": "ingot-iron", "quantity": 2},
            {"key": "parts-simple", "quantity": 2}
        ],
        "time": 2, "checks": 1, "dc": 12,
        "rarity": "common", "value": "5 gp",
        "resultItem": "Hunting Trap",
        "img": "icons/commodities/tech/cog-steel.webp"
    },

    # Escriba de Pergaminhos - Scrollscribing
    {
        "key": "recipe-scroll-cantrip",
        "name_pt": "Receita: Pergaminho de Truque (Nível 0)",
        "name_en": "Recipe: Cantrip Spell Scroll",
        "profession": "scrollscribing",
        "tool": "calligrapher",
        "ability": ["int", "wis"],
        "materials": [
            {"key": "magical-ink-common", "quantity": 1}
        ],
        "time": 2, "checks": 1, "dc": 11,
        "rarity": "common", "value": "15 gp",
        "resultItem": "Spell Scroll (Cantrip)",
        "img": "icons/sundries/scrolls/scroll-bound-ribbon-blue.webp"
    },
    {
        "key": "recipe-scroll-1st-level",
        "name_pt": "Receita: Pergaminho de 1º Nível",
        "name_en": "Recipe: 1st Level Spell Scroll",
        "profession": "scrollscribing",
        "tool": "calligrapher",
        "ability": ["int", "wis"],
        "materials": [
            {"key": "magical-ink-common", "quantity": 2}
        ],
        "time": 2, "checks": 1, "dc": 12,
        "rarity": "common", "value": "50 gp",
        "resultItem": "Spell Scroll (1st Level)",
        "img": "icons/sundries/scrolls/scroll-bound-ribbon-blue.webp"
    },
    {
        "key": "recipe-scroll-2nd-level",
        "name_pt": "Receita: Pergaminho de 2º Nível",
        "name_en": "Recipe: 2nd Level Spell Scroll",
        "profession": "scrollscribing",
        "tool": "calligrapher",
        "ability": ["int", "wis"],
        "materials": [
            {"key": "magical-ink-uncommon", "quantity": 2}
        ],
        "time": 4, "checks": 2, "dc": 14,
        "rarity": "uncommon", "value": "200 gp",
        "resultItem": "Spell Scroll (2nd Level)",
        "img": "icons/sundries/scrolls/scroll-bound-ribbon-blue.webp"
    },
    {
        "key": "recipe-scroll-3rd-level",
        "name_pt": "Receita: Pergaminho de 3º Nível",
        "name_en": "Recipe: 3rd Level Spell Scroll",
        "profession": "scrollscribing",
        "tool": "calligrapher",
        "ability": ["int", "wis"],
        "materials": [
            {"key": "magical-ink-uncommon", "quantity": 4}
        ],
        "time": 8, "checks": 4, "dc": 15,
        "rarity": "uncommon", "value": "400 gp",
        "resultItem": "Spell Scroll (3rd Level)",
        "img": "icons/sundries/scrolls/scroll-bound-ribbon-blue.webp"
    },

    # Lapidação de Varinhas - Wand Whittling
    {
        "key": "recipe-wand-warmage-plus-one",
        "name_pt": "Receita: Varinha do Mago de Guerra +1",
        "name_en": "Recipe: Wand of the War Mage +1",
        "profession": "wandwhittling",
        "tool": "woodcarver",
        "ability": ["dex", "int"],
        "materials": [
            {"key": "essence-arcane-uncommon", "quantity": 1},
            {"key": "reagent-reactive-uncommon", "quantity": 2}
        ],
        "time": 6, "checks": 3, "dc": 14,
        "rarity": "uncommon", "value": "500 gp",
        "resultItem": "Wand of the War Mage +1",
        "img": "icons/weapons/wands/wand-carved-gold.webp"
    },

    # Culinária - Cooking
    {
        "key": "recipe-hearty-rations",
        "name_pt": "Receita: Ração de Viagem Enriquecida",
        "name_en": "Recipe: Hearty Trail Rations",
        "profession": "cooking",
        "tool": "cook",
        "ability": ["wis"],
        "materials": [
            {"key": "reagent-curative-common", "quantity": 1}
        ],
        "time": 2, "checks": 1, "dc": 10,
        "rarity": "common", "value": "2 gp",
        "resultItem": "Hearty Rations (5 days)",
        "img": "icons/consumables/food/rations-meat-bread.webp"
    },
    {
        "key": "recipe-common-feast",
        "name_pt": "Receita: Banquete Revigorante",
        "name_en": "Recipe: Invigorating Feast",
        "profession": "cooking",
        "tool": "cook",
        "ability": ["wis"],
        "materials": [
            {"key": "reagent-curative-common", "quantity": 3},
            {"key": "reagent-reactive-common", "quantity": 1}
        ],
        "time": 2, "checks": 1, "dc": 12,
        "rarity": "common", "value": "15 gp",
        "resultItem": "Common Feast",
        "img": "icons/consumables/food/roast-chicken.webp"
    },

    # Aprimoramentos de Ferraria - Blacksmithing Upgrades
    {
        "key": "recipe-upgrade-silvered-weapon",
        "name_pt": "Aprimoramento: Arma Prateada",
        "name_en": "Upgrade: Silvered Weapon",
        "profession": "blacksmithing",
        "tool": "smith",
        "ability": ["str"],
        "materials": [
            {"key": "ingot-silver", "quantity": 1}
        ],
        "time": 2, "checks": 1, "dc": 12,
        "rarity": "common", "value": "100 gp",
        "resultItem": "Silvered Weapon",
        "img": "icons/weapons/swords/sword-broad-silver.webp"
    },
    {
        "key": "recipe-armor-mithral",
        "name_pt": "Receita: Armadura de Mithral",
        "name_en": "Recipe: Mithral Armor",
        "profession": "blacksmithing",
        "tool": "smith",
        "ability": ["str"],
        "materials": [
            {"key": "ingot-mithral", "quantity": 4},
            {"key": "leather-common", "quantity": 2}
        ],
        "time": 16, "checks": 8, "dc": 16,
        "rarity": "uncommon", "value": "800 gp",
        "resultItem": "Mithral Armor",
        "img": "icons/equipment/chest/breastplate-sculpted-white.webp"
    },
    {
        "key": "recipe-armor-adamantine",
        "name_pt": "Receita: Armadura de Adamantina",
        "name_en": "Recipe: Adamantine Armor",
        "profession": "blacksmithing",
        "tool": "smith",
        "ability": ["str"],
        "materials": [
            {"key": "ingot-adamantine", "quantity": 6},
            {"key": "leather-common", "quantity": 2}
        ],
        "time": 20, "checks": 10, "dc": 17,
        "rarity": "uncommon", "value": "1200 gp",
        "resultItem": "Adamantine Armor",
        "img": "icons/equipment/chest/breastplate-engraved-grey.webp"
    }
]

# --- 3. TABELAS DE ROLAGEM (ROLL TABLES) ---
TABLES_DEF = [
    {
        "key": "harvesting-cr-0-4",
        "name_pt": "Colheita de Criaturas (ND 0–4)",
        "name_en": "Creature Harvesting (CR 0–4)",
        "desc_pt": "Tabela de materiais e reagentes colhidos de monstros, dragões, aberrações e construtos de ND 0 a 4.",
        "desc_en": "Table of materials and reagents harvested from monsters, dragons, aberrations, and constructs of CR 0–4.",
        "formula": "1d100",
        "results": [
            {"range": [1, 20], "text_pt": "Nenhum componente aproveitável", "text_en": "No salvageable components"},
            {"range": [21, 50], "text_pt": "1x Reagente Venenoso Comum", "text_en": "1x Common Poisonous Reagent", "itemKey": "reagent-poisonous-common", "qty": 1},
            {"range": [51, 70], "text_pt": "1x Reagente Curativo Comum", "text_en": "1x Common Curative Reagent", "itemKey": "reagent-curative-common", "qty": 1},
            {"range": [71, 80], "text_pt": "1x Reagente Reativo Comum", "text_en": "1x Common Reactive Reagent", "itemKey": "reagent-reactive-common", "qty": 1},
            {"range": [81, 95], "text_pt": "1x Peças Refinadas ou Couro Raro", "text_en": "1x Fancy Parts or Rare Hide", "itemKey": "parts-fancy", "qty": 1},
            {"range": [96, 100], "text_pt": "1x Essência Primitiva ou Arcana Comum", "text_en": "1x Common Primal or Arcane Essence", "itemKey": "essence-primal-common", "qty": 1}
        ]
    },
    {
        "key": "harvesting-cr-5-10",
        "name_pt": "Colheita de Criaturas (ND 5–10)",
        "name_en": "Creature Harvesting (CR 5–10)",
        "desc_pt": "Tabela de materiais e essências colhidos de criaturas de ND 5 a 10.",
        "desc_en": "Table of materials and essences harvested from creatures of CR 5–10.",
        "formula": "1d100",
        "results": [
            {"range": [1, 20], "text_pt": "1x Reagente Reativo Comum", "text_en": "1x Common Reactive Reagent", "itemKey": "reagent-reactive-common", "qty": 1},
            {"range": [21, 50], "text_pt": "1x Reagente Curativo Incomum", "text_en": "1x Uncommon Curative Reagent", "itemKey": "reagent-curative-uncommon", "qty": 1},
            {"range": [51, 70], "text_pt": "1x Reagente Venenoso Incomum", "text_en": "1x Uncommon Poisonous Reagent", "itemKey": "reagent-poisonous-uncommon", "qty": 1},
            {"range": [71, 85], "text_pt": "1x Reagente Reativo Incomum", "text_en": "1x Uncommon Reactive Reagent", "itemKey": "reagent-reactive-uncommon", "qty": 1},
            {"range": [86, 95], "text_pt": "1x Essência Incomum (Arcana/Primitiva)", "text_en": "1x Uncommon Essence (Arcane/Primal)", "itemKey": "essence-arcane-uncommon", "qty": 1},
            {"range": [96, 100], "text_pt": "1x Essência Rara ou Escama Preciosa", "text_en": "1x Rare Essence or Precious Scale", "itemKey": "essence-arcane-rare", "qty": 1}
        ]
    },
    {
        "key": "harvesting-cr-11-16",
        "name_pt": "Colheita de Criaturas (ND 11–16)",
        "name_en": "Creature Harvesting (CR 11–16)",
        "desc_pt": "Tabela de materiais raros, essências e peças esotéricas de criaturas de ND 11 a 16.",
        "desc_en": "Table of rare materials, essences, and esoteric parts from CR 11–16 creatures.",
        "formula": "1d100",
        "results": [
            {"range": [1, 20], "text_pt": "1x Reagente Reativo Incomum", "text_en": "1x Uncommon Reactive Reagent", "itemKey": "reagent-reactive-uncommon", "qty": 1},
            {"range": [21, 50], "text_pt": "1x Reagente Curativo Raro", "text_en": "1x Rare Curative Reagent", "itemKey": "reagent-curative-rare", "qty": 1},
            {"range": [51, 70], "text_pt": "1x Reagente Venenoso Raro", "text_en": "1x Rare Poisonous Reagent", "itemKey": "reagent-poisonous-rare", "qty": 1},
            {"range": [71, 85], "text_pt": "1x Peças Esotéricas ou Escama de Dragão", "text_en": "1x Esoteric Parts or Dragon Scale", "itemKey": "parts-esoteric", "qty": 1},
            {"range": [86, 95], "text_pt": "1x Essência Rara (Arcana/Divina/Primitiva)", "text_en": "1x Rare Essence (Arcane/Divine/Primal)", "itemKey": "essence-arcane-rare", "qty": 1},
            {"range": [96, 100], "text_pt": "1x Essência Muito Rara", "text_en": "1x Very Rare Essence", "itemKey": "essence-arcane-very-rare", "qty": 1}
        ]
    },
    {
        "key": "harvesting-cr-17-plus",
        "name_pt": "Colheita de Criaturas Lendárias (ND 17+)",
        "name_en": "Legendary Creature Harvesting (CR 17+)",
        "desc_pt": "Tabela mítica de materiais de grandes dragões anciãos, arquidemônios e titãs de ND 17 ou superior.",
        "desc_en": "Mythic table of materials from ancient dragons, archfiends, and titans of CR 17+.",
        "formula": "1d100",
        "results": [
            {"range": [1, 20], "text_pt": "1x Reagente Reativo Raro", "text_en": "1x Rare Reactive Reagent", "itemKey": "reagent-reactive-rare", "qty": 1},
            {"range": [21, 45], "text_pt": "1x Reagente Muito Raro", "text_en": "1x Very Rare Reagent", "itemKey": "reagent-curative-very-rare", "qty": 1},
            {"range": [46, 70], "text_pt": "1x Essência Muito Rara", "text_en": "1x Very Rare Essence", "itemKey": "essence-arcane-very-rare", "qty": 1},
            {"range": [71, 90], "text_pt": "2x Escamas de Dragão / Peças Esotéricas", "text_en": "2x Dragon Scales / Esoteric Parts", "itemKey": "hide-dragon-scale", "qty": 2},
            {"range": [91, 100], "text_pt": "1x Essência Lendária (Arcana/Divina/Primitiva)", "text_en": "1x Legendary Essence", "itemKey": "essence-arcane-legendary", "qty": 1}
        ]
    },
    {
        "key": "harvesting-remnants-0-4",
        "name_pt": "Resíduos Mágicos (ND 0–4)",
        "name_en": "Magical Remnants (CR 0–4)",
        "desc_pt": "Resíduos energéticos deixados por Celestiais, Corruptores e Elementais ao serem destruídos.",
        "desc_en": "Energetic remnants left behind by Celestials, Fiends, and Elementals upon destruction.",
        "formula": "1d100",
        "results": [
            {"range": [1, 50], "text_pt": "Nenhum resíduo condensado", "text_en": "No condensed remnants"},
            {"range": [51, 75], "text_pt": "1x Reagente Reativo Comum", "text_en": "1x Common Reactive Reagent", "itemKey": "reagent-reactive-common", "qty": 1},
            {"range": [76, 90], "text_pt": "1x Reagente Curativo ou Venenoso Comum", "text_en": "1x Common Curative or Poisonous Reagent", "itemKey": "reagent-curative-common", "qty": 1},
            {"range": [91, 100], "text_pt": "1x Essência Divina ou Arcana Comum", "text_en": "1x Common Divine or Arcane Essence", "itemKey": "essence-divine-common", "qty": 1}
        ]
    },
    {
        "key": "gathering-wilderness",
        "name_pt": "Coleta na Natureza (Gathering)",
        "name_en": "Wilderness Gathering",
        "desc_pt": "Busca de ervas, fungos, minérios e recursos naturais durante viagens ou descansos.",
        "desc_en": "Foraging herbs, fungi, ores, and natural resources while traveling or resting.",
        "formula": "1d100",
        "results": [
            {"range": [1, 25], "text_pt": "Nenhum recurso especial encontrado", "text_en": "No special resources found"},
            {"range": [26, 60], "text_pt": "1d4 Reagentes Curativos Comuns", "text_en": "1d4 Common Curative Reagents", "itemKey": "reagent-curative-common", "qty": 2},
            {"range": [61, 80], "text_pt": "1d2 Reagentes Venenosos Comuns", "text_en": "1d2 Common Poisonous Reagents", "itemKey": "reagent-poisonous-common", "qty": 1},
            {"range": [81, 95], "text_pt": "1x Reagente Reativo Incomum", "text_en": "1x Uncommon Reactive Reagent", "itemKey": "reagent-reactive-uncommon", "qty": 1},
            {"range": [96, 100], "text_pt": "1x Essência Primitiva Comum", "text_en": "1x Common Primal Essence", "itemKey": "essence-primal-common", "qty": 1}
        ]
    }
]

# --- 4. REGRAS E GUIAS (JOURNAL ENTRIES) ---
RULES_DEF = [
    {
        "key": "rule-quick-summary",
        "name_pt": "Regras: Guia Prático de Crafting",
        "name_en": "Rules: Quick Crafting Guide",
        "content_pt": """<h1>Sistema de Criação de Itens (Kibbles' Crafting Guide)</h1>
<p>O sistema de crafting é projetado para o estilo de vida aventureiro: rápido, intuitivo e com tempo medido em blocos de <strong>2 horas</strong> (perfeito para descansos curtos, acampamentos ou viagens).</p>

<h3>Como Funciona o Processo:</h3>
<ol>
  <li><strong>Escolha o Item:</strong> Selecione a receita que deseja produzir.</li>
  <li><strong>Reúna os Materiais:</strong> Materiais podem ser comprados, saqueados, colhidos de monstros (<em>Harvesting</em>) ou coletados na natureza (<em>Gathering</em>).</li>
  <li><strong>Modificador de Criação:</strong>
    <code>Modificador de Crafting = Bônus de Proficiência da Ferramenta + Modificador de Atributo Relevante</code>
  </li>
  <li><strong>Progresso em 2 Horas:</strong> A cada 2 horas dedicadas ao trabalho, role 1d20 + Modificador de Crafting contra a CD da receita.
    <ul>
      <li><strong>Sucesso:</strong> Você adiciona 2 horas de progresso ao projeto.</li>
      <li><strong>Falha:</strong> Nenhum progresso é adicionado. Se falhar <strong>3 vezes consecutivas</strong>, o projeto falha e todos os materiais são destruídos.</li>
    </ul>
  </li>
  <li><strong>Finalização:</strong> Quando o progresso acumulado atingir o tempo total da receita, o item é concluído!</li>
  <li><strong>Regra do "Take 10":</strong> Você pode optar por não rolar dados e garantir o sucesso dobrando o tempo necessário da receita, desde que 10 + seu Modificador de Crafting atinja ou supere a CD da receita.</li>
</ol>

<h3>Referência de Ferramentas e Atributos:</h3>
<table border="1" cellpadding="4" style="border-collapse: collapse; width: 100%;">
  <thead>
    <tr style="background: #2a2a2a; color: #fff;">
      <th>Profissão</th>
      <th>Ferramenta Relacionada</th>
      <th>Atributo Relevante</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>Alquimia</td><td>Suprimentos de Alquimista</td><td>Inteligência ou Sabedoria</td></tr>
    <tr><td>Ferraria / Forja</td><td>Ferramentas de Ferreiro</td><td>Força</td></tr>
    <tr><td>Encantamento</td><td>Arcanismo</td><td>Inteligência</td></tr>
    <tr><td>Trabalho em Couro</td><td>Ferramentas de Coureiro</td><td>Destreza</td></tr>
    <tr><td>Geringonças / Tinkering</td><td>Ferramentas de Latoeiro</td><td>Inteligência</td></tr>
    <tr><td>Escriba de Pergaminhos</td><td>Suprimentos de Calígrafo</td><td>Inteligência ou Sabedoria</td></tr>
    <tr><td>Lapidação de Varinhas</td><td>Ferramentas de Entalhador</td><td>Destreza ou Inteligência</td></tr>
    <tr><td>Culinária</td><td>Utensílios de Cozinheiro</td><td>Sabedoria</td></tr>
  </tbody>
</table>""",
        "content_en": """<h1>Item Crafting System (Kibbles' Crafting Guide)</h1>
<p>This crafting system is designed for the adventuring lifestyle: fast, intuitive, and paced in <strong>2-hour increments</strong> (ideal for short rests, camp actions, or travel downtime).</p>

<h3>How Crafting Works:</h3>
<ol>
  <li><strong>Select an Item:</strong> Choose the recipe you want to craft.</li>
  <li><strong>Gather Materials:</strong> Materials can be purchased, looted, harvested from creatures, or gathered in the wilderness.</li>
  <li><strong>Crafting Modifier:</strong>
    <code>Crafting Modifier = Tool Proficiency Bonus + Relevant Ability Score Modifier</code>
  </li>
  <li><strong>Progress in 2-Hour Blocks:</strong> For every 2 hours spent, roll 1d20 + Crafting Modifier against the recipe's DC.
    <ul>
      <li><strong>Success:</strong> Add 2 hours of progress toward completion.</li>
      <li><strong>Failure:</strong> No progress made. If you fail <strong>3 times in a row</strong>, the craft fails and materials are ruined.</li>
    </ul>
  </li>
  <li><strong>Completion:</strong> Once total progress equals the required time, the item is finished!</li>
  <li><strong>Taking 10:</strong> You can take 10 by doubling the crafting time if 10 + your Crafting Modifier equals or exceeds the DC.</li>
</ol>"""
    },
    {
        "key": "rule-harvesting",
        "name_pt": "Regras: Colheita de Criaturas (Harvesting)",
        "name_en": "Rules: Creature Harvesting",
        "content_pt": """<h1>Colheita de Criaturas e Resíduos Mágicos</h1>
<p>Ao derrotar monstros e seres fantásticos, os aventureiros podem colher matérias-primas valiosas em vez de encontrar apenas moedas mundanas.</p>

<h3>Perícias Necessárias:</h3>
<ul>
  <li><strong>Dragões e Monstruosidades:</strong> Sabedoria (Medicina)</li>
  <li><strong>Construtos:</strong> Inteligência (Arcanismo)</li>
  <li><strong>Plantas:</strong> Inteligência (Natureza)</li>
  <li><strong>Feras e Couro Básico:</strong> Sabedoria (Sobrevivência)</li>
</ul>

<p>A colheita leva cerca de <strong>10 minutos</strong>. Se a criatura for propícia tanto para colheita básica (carne/couro) quanto colheita exótica, o segundo teste é realizado com <em>Desvantagem</em>.</p>
<p>Seres como Celestiais, Elementais e Ínferos não deixam corpos, mas sim <strong>Resíduos Mágicos (Remnants)</strong> que se condensam em 1 minuto sem necessidade de teste.</p>""",
        "content_en": """<h1>Creature Harvesting and Magical Remnants</h1>
<p>Upon defeating monsters, adventurers can harvest valuable reagents and essences instead of mundane loot.</p>

<h3>Required Skills:</h3>
<ul>
  <li><strong>Dragons and Monstrosities:</strong> Wisdom (Medicine)</li>
  <li><strong>Constructs:</strong> Intelligence (Arcana)</li>
  <li><strong>Plants:</strong> Intelligence (Nature)</li>
  <li><strong>Beasts and Basic Hide:</strong> Wisdom (Survival)</li>
</ul>
<p>Basic or exotic harvesting takes <strong>10 minutes</strong>. Celestials, Elementals, and Fiends leave behind <strong>Magical Remnants</strong> in 1 minute without requiring a check.</p>"""
    }
]

def build_materials_json(lang: str):
    docs = []
    for m in MATERIALS_DEF:
        doc_id = make_id(f"mat-{m['key']}")
        name = m["name_pt"] if lang == "pt-BR" else m["name_en"]
        desc = m["desc_pt"] if lang == "pt-BR" else m["desc_en"]
        
        doc = {
            "_id": doc_id,
            "name": name,
            "type": "loot",
            "img": m["img"],
            "system": {
                "description": {
                    "value": f"<p>{desc}</p>",
                    "chat": "",
                    "unidentified": ""
                },
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
                    "materialKey": m["key"],
                    "category": m["category"],
                    "rarity": m["rarity"]
                }
            }
        }
        docs.append(doc)
    return docs

def build_recipes_json(lang: str):
    docs = []
    for r in RECIPES_DEF:
        doc_id = make_id(f"rec-{r['key']}")
        name = r["name_pt"] if lang == "pt-BR" else r["name_en"]
        
        # Build HTML table for materials
        mat_rows = ""
        for mat in r["materials"]:
            mat_info = next((m for m in MATERIALS_DEF if m["key"] == mat["key"]), None)
            mat_name = mat_info["name_pt" if lang == "pt-BR" else "name_en"] if mat_info else mat["key"]
            mat_rows += f"<li>{mat['quantity']}x {mat_name}</li>"

        desc = f"""<h3>{name}</h3>
<p><strong>Profissão:</strong> {r['profession'].capitalize()} | <strong>CD:</strong> {r['dc']} | <strong>Tempo:</strong> {r['time']} horas ({r['checks']} testes)</p>
<p><strong>Materiais Necessários:</strong></p>
<ul>{mat_rows}</ul>
<p><strong>Resultado:</strong> {r['resultItem']} ({r['value']})</p>"""

        doc = {
            "_id": doc_id,
            "name": name,
            "type": "loot",
            "img": r["img"],
            "system": {
                "description": {
                    "value": desc,
                    "chat": "",
                    "unidentified": ""
                },
                "source": "Kibbles' Crafting Guide",
                "quantity": 1,
                "weight": 0.1,
                "price": {
                    "value": 10,
                    "denomination": "gp"
                },
                "rarity": r["rarity"],
                "identified": True
            },
            "flags": {
                "itensdnd": {
                    "isRecipe": True,
                    "recipeKey": r["key"],
                    "profession": r["profession"],
                    "tool": r["tool"],
                    "ability": r["ability"],
                    "materials": r["materials"],
                    "time": r["time"],
                    "checks": r["checks"],
                    "dc": r["dc"],
                    "resultItem": r["resultItem"],
                    "rarity": r["rarity"]
                }
            }
        }
        docs.append(doc)
    return docs

def build_tables_json(lang: str):
    docs = []
    for t in TABLES_DEF:
        doc_id = make_id(f"tbl-{t['key']}")
        name = t["name_pt"] if lang == "pt-BR" else t["name_en"]
        desc = t["desc_pt"] if lang == "pt-BR" else t["desc_en"]
        
        results = []
        for i, res in enumerate(t["results"]):
            res_id = make_id(f"tbl-res-{t['key']}-{i}")
            text = res["text_pt"] if lang == "pt-BR" else res["text_en"]
            res_doc = {
                "_id": res_id,
                "type": "text",
                "text": text,
                "weight": res["range"][1] - res["range"][0] + 1,
                "range": res["range"],
                "drawn": False,
                "flags": {
                    "itensdnd": {
                        "itemKey": res.get("itemKey"),
                        "qty": res.get("qty", 1)
                    }
                }
            }
            results.append(res_doc)

        doc = {
            "_id": doc_id,
            "name": name,
            "img": "icons/svg/d20-grey.svg",
            "description": f"<p>{desc}</p>",
            "results": results,
            "formula": t["formula"],
            "replacement": True,
            "displayRoll": True,
            "flags": {
                "itensdnd": {
                    "tableKey": t["key"]
                }
            }
        }
        docs.append(doc)
    return docs

def build_rules_json(lang: str):
    docs = []
    for r in RULES_DEF:
        doc_id = make_id(f"rule-{r['key']}")
        name = r["name_pt"] if lang == "pt-BR" else r["name_en"]
        content = r["content_pt"] if lang == "pt-BR" else r["content_en"]
        
        page_id = make_id(f"page-{r['key']}")
        page = {
            "_id": page_id,
            "name": name,
            "type": "text",
            "text": {
                "content": content,
                "format": 1
            },
            "ownership": {"default": -1}
        }

        doc = {
            "_id": doc_id,
            "name": name,
            "pages": [page],
            "flags": {
                "itensdnd": {
                    "ruleKey": r["key"]
                }
            }
        }
        docs.append(doc)
    return docs

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data")
    
    for lang in ["pt-BR", "en"]:
        target_lang_dir = os.path.join(data_dir, lang)
        os.makedirs(target_lang_dir, exist_ok=True)
        
        # 1. Materials
        mats = build_materials_json(lang)
        with open(os.path.join(target_lang_dir, "crafting-materials.json"), "w", encoding="utf-8") as f:
            json.dump(mats, f, ensure_ascii=False, indent=2)
            
        # 2. Recipes
        recs = build_recipes_json(lang)
        with open(os.path.join(target_lang_dir, "crafting-recipes.json"), "w", encoding="utf-8") as f:
            json.dump(recs, f, ensure_ascii=False, indent=2)
            
        # 3. Tables
        tbls = build_tables_json(lang)
        with open(os.path.join(target_lang_dir, "crafting-tables.json"), "w", encoding="utf-8") as f:
            json.dump(tbls, f, ensure_ascii=False, indent=2)
            
        # 4. Rules
        rules = build_rules_json(lang)
        with open(os.path.join(target_lang_dir, "crafting-rules.json"), "w", encoding="utf-8") as f:
            json.dump(rules, f, ensure_ascii=False, indent=2)
            
        print(f"Generated data for {lang}: {len(mats)} materials, {len(recs)} recipes, {len(tbls)} tables, {len(rules)} rules.")

if __name__ == "__main__":
    main()
