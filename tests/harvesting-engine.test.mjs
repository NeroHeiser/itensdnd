import test from "node:test";
import assert from "node:assert/strict";
import { HarvestingEngine } from "../scripts/harvesting-engine.mjs";

test("getTableAndDC returns remnants table with DC 0 when isRemnants is true", () => {
  const resultLowCR = HarvestingEngine.getTableAndDC(2, true);
  assert.equal(resultLowCR.tableKey, "harvesting-remnants-0-4");
  assert.equal(resultLowCR.dc, 0);

  const resultHighCR = HarvestingEngine.getTableAndDC(20, true);
  assert.equal(resultHighCR.tableKey, "harvesting-remnants-0-4");
  assert.equal(resultHighCR.dc, 0);
});

test("getTableAndDC maps creature challenge rating to corresponding tables and DCs", () => {
  const cr0 = HarvestingEngine.getTableAndDC(0, false);
  assert.equal(cr0.tableKey, "harvesting-cr-0-4");
  assert.equal(cr0.dc, 8);

  const cr4 = HarvestingEngine.getTableAndDC(4, false);
  assert.equal(cr4.tableKey, "harvesting-cr-0-4");
  assert.equal(cr4.dc, 8);

  const cr5 = HarvestingEngine.getTableAndDC(5, false);
  assert.equal(cr5.tableKey, "harvesting-cr-5-10");
  assert.equal(cr5.dc, 10);

  const cr10 = HarvestingEngine.getTableAndDC(10, false);
  assert.equal(cr10.tableKey, "harvesting-cr-5-10");
  assert.equal(cr10.dc, 10);

  const cr11 = HarvestingEngine.getTableAndDC(11, false);
  assert.equal(cr11.tableKey, "harvesting-cr-11-16");
  assert.equal(cr11.dc, 12);

  const cr16 = HarvestingEngine.getTableAndDC(16, false);
  assert.equal(cr16.tableKey, "harvesting-cr-11-16");
  assert.equal(cr16.dc, 12);

  const cr17 = HarvestingEngine.getTableAndDC(17, false);
  assert.equal(cr17.tableKey, "harvesting-cr-17-plus");
  assert.equal(cr17.dc, 14);

  const cr25 = HarvestingEngine.getTableAndDC(25, false);
  assert.equal(cr25.tableKey, "harvesting-cr-17-plus");
  assert.equal(cr25.dc, 14);
});

test("SKILL_REQUIREMENTS correctly configures required skills and abilities by creature type", () => {
  const dragon = HarvestingEngine.SKILL_REQUIREMENTS.dragon;
  assert.equal(dragon.skill, "med");
  assert.equal(dragon.ability, "wis");

  const construct = HarvestingEngine.SKILL_REQUIREMENTS.construct;
  assert.equal(construct.skill, "arc");
  assert.equal(construct.ability, "int");

  const beast = HarvestingEngine.SKILL_REQUIREMENTS.beast;
  assert.equal(beast.skill, "sur");
  assert.equal(beast.ability, "wis");

  const plant = HarvestingEngine.SKILL_REQUIREMENTS.plant;
  assert.equal(plant.skill, "nat");
  assert.equal(plant.ability, "int");

  const celestial = HarvestingEngine.SKILL_REQUIREMENTS.celestial;
  assert.equal(celestial.remnants, true);

  const fiend = HarvestingEngine.SKILL_REQUIREMENTS.fiend;
  assert.equal(fiend.remnants, true);
});
