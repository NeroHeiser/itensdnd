import test from "node:test";
import assert from "node:assert/strict";
import { HarvestingApp } from "../scripts/apps/harvesting-app.mjs";
import { CraftingWorkshopApp } from "../scripts/apps/crafting-app.mjs";

test("HarvestingApp uses valid FontAwesome Free icon", () => {
  const icon = HarvestingApp.DEFAULT_OPTIONS.window.icon;
  assert.equal(icon, "fas fa-paw");
  assert.notEqual(icon, "fas fa-claw-marks", "Must not use FontAwesome Pro claw-marks icon");
});

test("CraftingWorkshopApp uses valid FontAwesome Free icon", () => {
  const icon = CraftingWorkshopApp.DEFAULT_OPTIONS.window.icon;
  assert.equal(icon, "fas fa-hammer");
});

test("HarvestingApp can be instantiated safely", () => {
  const app = new HarvestingApp();
  assert.ok(app instanceof HarvestingApp);
  assert.equal(app.harvester, null);
  assert.equal(app.target, null);
});
