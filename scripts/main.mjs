import { CompendiumSync } from "./compendium-sync.mjs";
import { CraftingEngine } from "./crafting-engine.mjs";
import { HarvestingEngine } from "./harvesting-engine.mjs";
import { CraftingWorkshopApp } from "./apps/crafting-app.mjs";
import { HarvestingApp } from "./apps/harvesting-app.mjs";

const MODULE_ID = "itensdnd";

Hooks.once("init", () => {
  console.log("itensdnd | Initializing module");

  game.settings.register(MODULE_ID, "enableSheetButton", {
    name: "ITENSDND.Settings.EnableSheetButton.Name",
    hint: "ITENSDND.Settings.EnableSheetButton.Hint",
    scope: "client",
    config: true,
    type: Boolean,
    default: true
  });

  game.settings.register(MODULE_ID, "autoSyncCompendiums", {
    name: "ITENSDND.Settings.AutoSyncCompendiums.Name",
    hint: "ITENSDND.Settings.AutoSyncCompendiums.Hint",
    scope: "world",
    config: true,
    type: Boolean,
    default: true
  });

  game.settings.register(MODULE_ID, "syncedLanguage", {
    name: "ITENSDND.Settings.SyncedLanguage.Name",
    hint: "ITENSDND.Settings.SyncedLanguage.Hint",
    scope: "world",
    config: false,
    type: String,
    default: ""
  });

  game.settings.registerMenu(MODULE_ID, "workshopMenu", {
    name: "ITENSDND.Settings.Menu.Name",
    label: "ITENSDND.Settings.Menu.Label",
    hint: "ITENSDND.Settings.Menu.Hint",
    icon: "fas fa-hammer",
    type: CraftingWorkshopApp,
    restricted: false
  });

  game.settings.registerMenu(MODULE_ID, "harvestMenu", {
    name: "ITENSDND.Settings.HarvestMenu.Name",
    label: "ITENSDND.Settings.HarvestMenu.Label",
    hint: "ITENSDND.Settings.HarvestMenu.Hint",
    icon: "fas fa-paw",
    type: HarvestingApp,
    restricted: false
  });

  game.settings.registerMenu(MODULE_ID, "syncMenu", {
    name: "ITENSDND.Settings.SyncMenu.Name",
    label: "ITENSDND.Settings.SyncMenu.Label",
    hint: "ITENSDND.Settings.SyncMenu.Hint",
    icon: "fas fa-sync-alt",
    type: class SyncCompendiumsForm extends FormApplication {
      static get defaultOptions() {
        return foundry.utils.mergeObject(super.defaultOptions, {
          title: game.i18n.localize("ITENSDND.Settings.SyncMenu.Label") || "Sync Crafting Compendiums",
          template: "templates/generic-form.html",
          width: 400,
          height: "auto"
        });
      }
      async render() {
        new Dialog({
          title: game.i18n.localize("ITENSDND.Settings.SyncMenu.Label") || "Sync Compendiums",
          content: `<p>${game.i18n.localize("ITENSDND.Settings.SyncMenu.Hint") || "Synchronize compendium data from module packs."}</p>`,
          buttons: {
            confirm: {
              icon: '<i class="fas fa-sync"></i>',
              label: game.i18n.localize("ITENSDND.Settings.SyncMenu.Label") || "Sync Now",
              callback: async () => {
                ui.notifications?.info(game.i18n.localize("ITENSDND.Compendium.SyncStart") || "Starting compendium synchronization...");
                await CompendiumSync.syncAllPacks({ force: true, silent: false });
              }
            },
            cancel: {
              icon: '<i class="fas fa-times"></i>',
              label: game.i18n.localize("Cancel") || "Cancel"
            }
          },
          default: "confirm"
        }).render(true);
      }
    },
    restricted: true
  });

  if (!Handlebars.helpers.multiply) {
    Handlebars.registerHelper("multiply", (a, b) => (Number(a) || 0) * (Number(b) || 0));
  }
  if (!Handlebars.helpers.eq) {
    Handlebars.registerHelper("eq", (a, b) => a === b);
  }
  if (!Handlebars.helpers.gte) {
    Handlebars.registerHelper("gte", (a, b) => Number(a) >= Number(b));
  }
  if (!Handlebars.helpers.gt) {
    Handlebars.registerHelper("gt", (a, b) => Number(a) > Number(b));
  }
  if (!Handlebars.helpers.or) {
    Handlebars.registerHelper("or", (a, b) => a || b);
  }

  loadTemplates([
    "modules/itensdnd/templates/crafting-app.hbs",
    "modules/itensdnd/templates/harvesting-app.hbs"
  ]);
});

Hooks.once("ready", async () => {
  console.log("itensdnd | Module ready");

  if (game.user.isGM) {
    await CompendiumSync.checkAndSyncAllPacks({ silent: false });
  }

  const moduleObj = game.modules.get(MODULE_ID);
  if (moduleObj) {
    moduleObj.api = {
      CraftingEngine,
      HarvestingEngine,
      CraftingWorkshopApp,
      HarvestingApp,
      openWorkshop: (actor) => new CraftingWorkshopApp({ actor }).render({ force: true }),
      openHarvesting: (target, harvester) => new HarvestingApp({ target, harvester }).render({ force: true }),
      syncCompendiums: (force = false) => CompendiumSync.syncAllPacks({ force, silent: false })
    };
  }
});

function addSheetWorkshopButton(app, buttons) {
  try {
    if (!game.settings.get(MODULE_ID, "enableSheetButton")) return;
  } catch (e) {}

  const actor = app.actor || app.document;
  if (!actor || actor.type !== "character") return;

  if (buttons.some(b => b.class === "itensdnd-sheet-btn")) return;

  buttons.unshift({
    label: game.i18n.localize("ITENSDND.Settings.Menu.Label") || "Workshop",
    class: "itensdnd-sheet-btn",
    icon: "fas fa-hammer",
    onclick: () => {
      new CraftingWorkshopApp({ actor }).render({ force: true });
    }
  });
}

Hooks.on("getApplicationHeaderButtons", (app, buttons) => {
  addSheetWorkshopButton(app, buttons);
});

Hooks.on("getActorSheetHeaderButtons", (sheet, buttons) => {
  addSheetWorkshopButton(sheet, buttons);
});

Hooks.on("renderActorSheet", (app, html) => {
  try {
    if (!game.settings.get(MODULE_ID, "enableSheetButton")) return;
  } catch (e) {}

  const actor = app.actor || app.document;
  if (!actor || actor.type !== "character") return;

  const root = html instanceof HTMLElement ? html : html[0];
  if (!root) return;

  const windowApp = root.closest(".window-app") || document.getElementById(app.id) || (app.element ? (app.element[0] || app.element) : null);
  const header = windowApp?.querySelector(".window-header");
  if (header && !header.querySelector(".itensdnd-sheet-btn")) {
    const btn = document.createElement("a");
    btn.className = "header-button control itensdnd-sheet-btn";
    btn.innerHTML = '<i class="fas fa-hammer"></i> ' + (game.i18n.localize("ITENSDND.Settings.Menu.Label") || "Workshop");
    btn.title = game.i18n.localize("ITENSDND.Settings.Menu.Hint") || "Open Crafting Workshop";
    btn.onclick = (ev) => {
      ev.preventDefault();
      new CraftingWorkshopApp({ actor }).render({ force: true });
    };
    const closeBtn = header.querySelector(".close");
    if (closeBtn) {
      header.insertBefore(btn, closeBtn);
    } else {
      header.appendChild(btn);
    }
  }

  const restContainer = root.querySelector(".sheet-header .header-actions, .sheet-header .character-details, [data-action='rest']");
  if (restContainer && !root.querySelector(".itensdnd-sheet-inner-btn")) {
    const craftBtn = document.createElement("button");
    craftBtn.type = "button";
    craftBtn.className = "itensdnd-sheet-inner-btn";
    craftBtn.title = game.i18n.localize("ITENSDND.Settings.Menu.Label") || "Crafting Workshop";
    craftBtn.innerHTML = '<i class="fas fa-hammer"></i>';
    craftBtn.style.cssText = "width: 28px; height: 28px; border-radius: 4px; margin-left: 6px; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; background: rgba(0,0,0,0.3); border: 1px solid #795548; color: #ffb74d;";
    craftBtn.onclick = (ev) => {
      ev.preventDefault();
      new CraftingWorkshopApp({ actor }).render({ force: true });
    };
    const targetParent = restContainer.parentElement || restContainer;
    targetParent.appendChild(craftBtn);
  }
});
