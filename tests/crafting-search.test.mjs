import test from "node:test";
import assert from "node:assert/strict";
import { CraftingWorkshopApp } from "../scripts/apps/crafting-app.mjs";

test("filterRecipesBySearch returns original list for empty, null, or whitespace queries", () => {
  const recipes = [
    { name: "Healing Potion", resultItem: "Potion of Healing" },
    { name: "Alchemist Fire", resultItem: "Flask of Alchemist Fire" }
  ];

  assert.equal(CraftingWorkshopApp.filterRecipesBySearch(recipes, ""), recipes);
  assert.equal(CraftingWorkshopApp.filterRecipesBySearch(recipes, "   "), recipes);
  assert.equal(CraftingWorkshopApp.filterRecipesBySearch(recipes, null), recipes);
  assert.equal(CraftingWorkshopApp.filterRecipesBySearch(recipes, undefined), recipes);
});

test("filterRecipesBySearch filters recipes matching name case-insensitively", () => {
  const recipes = [
    { name: "Healing Potion", resultItem: "Potion of Healing" },
    { name: "Antitoxin", resultItem: "Vial of Antitoxin" },
    { name: "Greater Healing Potion", resultItem: "Potion of Greater Healing" }
  ];

  const results = CraftingWorkshopApp.filterRecipesBySearch(recipes, "healing");
  assert.equal(results.length, 2);
  assert.equal(results[0].name, "Healing Potion");
  assert.equal(results[1].name, "Greater Healing Potion");
});

test("filterRecipesBySearch filters recipes matching resultItem", () => {
  const recipes = [
    { name: "Cure Moderate", resultItem: "Elixir of Health" },
    { name: "Basic Brew", resultItem: "Flask of Acid" }
  ];

  const results = CraftingWorkshopApp.filterRecipesBySearch(recipes, "acid");
  assert.equal(results.length, 1);
  assert.equal(results[0].name, "Basic Brew");
});

test("filterRecipesBySearch returns empty array when no matches found", () => {
  const recipes = [
    { name: "Healing Potion", resultItem: "Potion of Healing" }
  ];

  const results = CraftingWorkshopApp.filterRecipesBySearch(recipes, "sword");
  assert.deepEqual(results, []);
});

test("CraftingWorkshopApp initializes search query state and handles render listener", () => {
  const app = new CraftingWorkshopApp();
  assert.equal(app.searchQuery, "");
  assert.equal(app._preserveSearchFocus, false);

  let renderCalled = false;
  app.render = () => { renderCalled = true; };

  let inputListener = null;
  const mockInput = {
    value: "potion",
    focus: () => {},
    setSelectionRange: () => {},
    addEventListener: (event, handler) => {
      if (event === "input") inputListener = handler;
    }
  };

  app.element = {
    querySelector: (selector) => {
      if (selector === 'input[name="searchQuery"]') return mockInput;
      return null;
    }
  };

  app._onRender();
  assert.ok(typeof inputListener === "function", "Expected input listener to be registered");

  inputListener({ target: { value: "poison" } });
  assert.equal(app.searchQuery, "poison");
  assert.equal(app._preserveSearchFocus, true);
  assert.equal(renderCalled, true);
});
