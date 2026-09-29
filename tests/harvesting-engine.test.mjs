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

test("parseChallengeRating correctly converts numbers, numeric strings, and fractional strings", () => {
  assert.equal(HarvestingEngine.parseChallengeRating(0), 0);
  assert.equal(HarvestingEngine.parseChallengeRating(5), 5);
  assert.equal(HarvestingEngine.parseChallengeRating(0.25), 0.25);
  assert.equal(HarvestingEngine.parseChallengeRating("0"), 0);
  assert.equal(HarvestingEngine.parseChallengeRating("5"), 5);
  assert.equal(HarvestingEngine.parseChallengeRating("  10  "), 10);
  assert.equal(HarvestingEngine.parseChallengeRating("1/2"), 0.5);
  assert.equal(HarvestingEngine.parseChallengeRating("1/4"), 0.25);
  assert.equal(HarvestingEngine.parseChallengeRating("1/8"), 0.125);
  assert.equal(HarvestingEngine.parseChallengeRating(null), 0);
  assert.equal(HarvestingEngine.parseChallengeRating(undefined), 0);
  assert.equal(HarvestingEngine.parseChallengeRating(""), 0);
  assert.equal(HarvestingEngine.parseChallengeRating("invalid"), 0);
  assert.equal(HarvestingEngine.parseChallengeRating("1/0"), 0);
});

test("getTableAndDC correctly resolves tables and DCs for fractional string CR values", () => {
  const crQuarter = HarvestingEngine.getTableAndDC("1/4", false);
  assert.equal(crQuarter.tableKey, "harvesting-cr-0-4");
  assert.equal(crQuarter.dc, 8);

  const crHalf = HarvestingEngine.getTableAndDC("1/2", false);
  assert.equal(crHalf.tableKey, "harvesting-cr-0-4");
  assert.equal(crHalf.dc, 8);

  const crEighth = HarvestingEngine.getTableAndDC("1/8", false);
  assert.equal(crEighth.tableKey, "harvesting-cr-0-4");
  assert.equal(crEighth.dc, 8);

  const crStringFive = HarvestingEngine.getTableAndDC("5", false);
  assert.equal(crStringFive.tableKey, "harvesting-cr-5-10");
  assert.equal(crStringFive.dc, 10);

  const crStringSeventeen = HarvestingEngine.getTableAndDC("17", false);
  assert.equal(crStringSeventeen.tableKey, "harvesting-cr-17-plus");
  assert.equal(crStringSeventeen.dc, 14);
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
