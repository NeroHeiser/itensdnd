import test from "node:test";
import assert from "node:assert/strict";
import { CraftingWorkshopApp } from "../scripts/apps/crafting-app.mjs";

test("getActiveProject returns empty default when actor is null, undefined, or lacks flags", () => {
  assert.deepEqual(CraftingWorkshopApp.getActiveProject(null), { recipeId: null, hours: 0, consecutiveFailures: 0 });
  assert.deepEqual(CraftingWorkshopApp.getActiveProject({}), { recipeId: null, hours: 0, consecutiveFailures: 0 });
  assert.deepEqual(CraftingWorkshopApp.getActiveProject({ flags: {} }), { recipeId: null, hours: 0, consecutiveFailures: 0 });
});

test("getActiveProject parses project state from actor.getFlag function or flags object", () => {
  const actorWithMethod = {
    getFlag: (scope, key) => {
      if (scope === "itensdnd" && key === "activeProject") {
        return { recipeId: "recipe-potion-healing", hours: "4", consecutiveFailures: 1 };
      }
      return null;
    }
  };

  const projectFromMethod = CraftingWorkshopApp.getActiveProject(actorWithMethod);
  assert.equal(projectFromMethod.recipeId, "recipe-potion-healing");
  assert.equal(projectFromMethod.hours, 4);
  assert.equal(projectFromMethod.consecutiveFailures, 1);

  const actorWithFlags = {
    flags: {
      itensdnd: {
        activeProject: { recipeId: "recipe-iron-sword", hours: 6, consecutiveFailures: 2 }
      }
    }
  };

  const projectFromFlags = CraftingWorkshopApp.getActiveProject(actorWithFlags);
  assert.equal(projectFromFlags.recipeId, "recipe-iron-sword");
  assert.equal(projectFromFlags.hours, 6);
  assert.equal(projectFromFlags.consecutiveFailures, 2);
});

test("setActiveProject sets flag on actor when active project data is provided", async () => {
  let flagSet = null;
  const actor = {
    setFlag: async (scope, key, val) => {
      flagSet = { scope, key, val };
    }
  };

  await CraftingWorkshopApp.setActiveProject(actor, {
    recipeId: "recipe-plate-armor",
    hours: 12,
    consecutiveFailures: 0
  });

  assert.ok(flagSet !== null);
  assert.equal(flagSet.scope, "itensdnd");
  assert.equal(flagSet.key, "activeProject");
  assert.deepEqual(flagSet.val, {
    recipeId: "recipe-plate-armor",
    hours: 12,
    consecutiveFailures: 0
  });
});

test("setActiveProject unsets flag when project is null or lacks recipeId", async () => {
  let unsetCalled = false;
  const actor = {
    unsetFlag: async (scope, key) => {
      if (scope === "itensdnd" && key === "activeProject") {
        unsetCalled = true;
      }
    }
  };

  await CraftingWorkshopApp.setActiveProject(actor, null);
  assert.equal(unsetCalled, true);

  unsetCalled = false;
  await CraftingWorkshopApp.setActiveProject(actor, { recipeId: null, hours: 0 });
  assert.equal(unsetCalled, true);
});

test("CraftingWorkshopApp instance delegates project persistence to its actor", async () => {
  const actor = {
    flags: {
      itensdnd: {
        activeProject: { recipeId: "recipe-alchemist-fire", hours: 2, consecutiveFailures: 0 }
      }
    },
    setFlag: async (scope, key, val) => {
      actor.flags[scope] = actor.flags[scope] || {};
      actor.flags[scope][key] = val;
    },
    unsetFlag: async (scope, key) => {
      if (actor.flags?.[scope]) delete actor.flags[scope][key];
    }
  };

  const app = new CraftingWorkshopApp({ actor });
  assert.equal(app.getActiveProject().recipeId, "recipe-alchemist-fire");
  assert.equal(app.getActiveProject().hours, 2);

  await app.setActiveProject({ recipeId: "recipe-alchemist-fire", hours: 4, consecutiveFailures: 1 });
  assert.equal(actor.flags.itensdnd.activeProject.hours, 4);
  assert.equal(actor.flags.itensdnd.activeProject.consecutiveFailures, 1);

  await app.setActiveProject(null);
  assert.equal(actor.flags.itensdnd.activeProject, undefined);
  assert.equal(app.getActiveProject().recipeId, null);
});
