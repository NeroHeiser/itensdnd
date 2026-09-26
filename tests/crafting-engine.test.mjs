import test from "node:test";
import assert from "node:assert/strict";
import { CraftingEngine } from "../scripts/crafting-engine.mjs";

test("getMaterialCount returns zero when actor has no items or matching material", () => {
  assert.equal(CraftingEngine.getMaterialCount(null, "iron-ingot"), 0);
  assert.equal(CraftingEngine.getMaterialCount({}, "iron-ingot"), 0);
  assert.equal(CraftingEngine.getMaterialCount({ items: [] }, "iron-ingot"), 0);

  const actor = {
    items: [
      { name: "Leather", flags: { itensdnd: { materialKey: "leather-strip" } }, system: { quantity: 5 } }
    ]
  };
  assert.equal(CraftingEngine.getMaterialCount(actor, "iron-ingot"), 0);
});

test("getMaterialCount aggregates quantities across multiple item stacks", () => {
  const actor = {
    items: [
      { name: "Iron Ingot", flags: { itensdnd: { materialKey: "iron-ingot" } }, system: { quantity: 3 } },
      { name: "Iron Ingot Extra", flags: { itensdnd: { materialKey: "iron-ingot" } }, system: { quantity: 2 } },
      { name: "Wood", flags: { itensdnd: { materialKey: "wood-plank" } }, system: { quantity: 10 } }
    ]
  };

  assert.equal(CraftingEngine.getMaterialCount(actor, "iron-ingot"), 5);
  assert.equal(CraftingEngine.getMaterialCount(actor, "wood-plank"), 10);
});

test("checkMaterials verifies required quantities and reports satisfaction status", () => {
  const actor = {
    items: [
      { flags: { itensdnd: { materialKey: "iron-ingot" } }, system: { quantity: 5 } },
      { flags: { itensdnd: { materialKey: "wood-plank" } }, system: { quantity: 1 } }
    ]
  };

  const recipeComplete = {
    materials: [
      { key: "iron-ingot", quantity: 3 },
      { key: "wood-plank", quantity: 1 }
    ]
  };

  const resComplete = CraftingEngine.checkMaterials(actor, recipeComplete);
  assert.equal(resComplete.hasAll, true);
  assert.equal(resComplete.materialsStatus.length, 2);
  assert.equal(resComplete.materialsStatus[0].satisfied, true);
  assert.equal(resComplete.materialsStatus[1].satisfied, true);

  const recipeMissing = {
    materials: [
      { key: "iron-ingot", quantity: 10 },
      { key: "magic-dust", quantity: 1 }
    ]
  };

  const resMissing = CraftingEngine.checkMaterials(actor, recipeMissing);
  assert.equal(resMissing.hasAll, false);
  assert.equal(resMissing.materialsStatus[0].satisfied, false);
  assert.equal(resMissing.materialsStatus[0].have, 5);
  assert.equal(resMissing.materialsStatus[1].satisfied, false);
  assert.equal(resMissing.materialsStatus[1].have, 0);
});

test("checkMaterials handles recipes with empty or undefined materials", () => {
  const actor = { items: [] };
  assert.equal(CraftingEngine.checkMaterials(actor, {}).hasAll, true);
  assert.equal(CraftingEngine.checkMaterials(actor, { materials: [] }).hasAll, true);
});

test("calculateCraftingModifier returns default fallback when actor is missing", () => {
  const result = CraftingEngine.calculateCraftingModifier(null, { tool: "smith", ability: ["str"] });
  assert.deepEqual(result, {
    mod: 0,
    profBonus: 0,
    abilityMod: 0,
    bestAbility: "int",
    toolProficient: false
  });
});

test("calculateCraftingModifier uses tool proficiency from actor.system.tools", () => {
  const actor = {
    system: {
      attributes: { prof: 3 },
      tools: {
        smith: { value: 1 }
      },
      abilities: {
        str: { mod: 4 },
        dex: { mod: 2 }
      }
    }
  };

  const recipe = {
    tool: "smith",
    ability: ["str", "dex"]
  };

  const result = CraftingEngine.calculateCraftingModifier(actor, recipe);
  assert.equal(result.toolProficient, true);
  assert.equal(result.profBonus, 3);
  assert.equal(result.abilityMod, 4);
  assert.equal(result.bestAbility, "str");
  assert.equal(result.mod, 7);
});

test("calculateCraftingModifier identifies tool items in inventory when tools data lacks proficiency", () => {
  const actor = {
    system: {
      attributes: { prof: 2 },
      tools: {},
      abilities: {
        dex: { mod: 3 }
      }
    },
    items: [
      {
        type: "tool",
        name: "Smith's Tools",
        system: { baseItem: "smiths-tools", proficient: 1 }
      }
    ]
  };

  const recipe = {
    tool: "smith",
    ability: ["dex"]
  };

  const result = CraftingEngine.calculateCraftingModifier(actor, recipe);
  assert.equal(result.toolProficient, true);
  assert.equal(result.profBonus, 2);
  assert.equal(result.mod, 5);
});

test("calculateCraftingModifier handles enchanting profession using Arcana skill", () => {
  const actor = {
    system: {
      attributes: { prof: 4 },
      skills: {
        arc: { value: 2 }
      },
      abilities: {
        int: { mod: 5 }
      }
    }
  };

  const recipe = {
    profession: "enchanting",
    tool: "arcana",
    ability: ["int"]
  };

  const result = CraftingEngine.calculateCraftingModifier(actor, recipe);
  assert.equal(result.toolProficient, true);
  assert.equal(result.profBonus, 8);
  assert.equal(result.abilityMod, 5);
  assert.equal(result.mod, 13);
});

test("calculateCraftingModifier supports herbalism kit fallback for alchemy profession", () => {
  const actor = {
    system: {
      attributes: { prof: 2 },
      tools: {
        herbalism: { value: 1 }
      },
      abilities: {
        wis: { mod: 3 }
      }
    }
  };

  const recipe = {
    profession: "alchemy",
    tool: "alchemist",
    ability: ["wis"]
  };

  const result = CraftingEngine.calculateCraftingModifier(actor, recipe);
  assert.equal(result.toolProficient, true);
  assert.equal(result.profBonus, 2);
  assert.equal(result.bestAbility, "wis");
  assert.equal(result.mod, 5);
});

test("calculateCraftingModifier selects highest ability modifier among allowed options", () => {
  const actor = {
    system: {
      attributes: { prof: 2 },
      tools: {},
      abilities: {
        str: { mod: 1 },
        dex: { mod: 4 },
        int: { mod: 2 }
      }
    }
  };

  const recipe = {
    tool: "tinker",
    ability: ["str", "dex", "int"]
  };

  const result = CraftingEngine.calculateCraftingModifier(actor, recipe);
  assert.equal(result.bestAbility, "dex");
  assert.equal(result.abilityMod, 4);
  assert.equal(result.mod, 4);
  assert.equal(result.toolProficient, false);
});
