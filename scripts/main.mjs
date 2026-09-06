/**
 * main.mjs
 * Módulo de Itens & Sistema de Crafting (D&D 5e) para Foundry VTT (v12-v14).
 * Baseado no Kibbles' Crafting Guide e The Griffon's Saddlebag.
 */

import { CompendiumSync } from "./compendium-sync.mjs";
import { CraftingEngine } from "./crafting-engine.mjs";
import { HarvestingEngine } from "./harvesting-engine.mjs";
import { CraftingWorkshopApp } from "./apps/crafting-app.mjs";
import { HarvestingApp } from "./apps/harvesting-app.mjs";

const MODULE_ID = "itensdnd";

/**
 * Hook de Inicialização do Foundry VTT (init).
 */
Hooks.once("init", () => {
  console.log("Itens & Sistema de Crafting D&D 5e | Inicializando módulo...");

  // Registrar configurações do módulo
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

  // Menus de atalho nas Configurações
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

  // Registrar helpers auxiliares do Handlebars caso não estejam disponíveis
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
});

/**
 * Hook de Inicialização Completa (ready).
 */
Hooks.once("ready", async () => {
  console.log("Itens & Sistema de Crafting D&D 5e | Sistema pronto!");

  // Sincronização automática dos compêndios para o Mestre
  if (game.user.isGM && game.settings.get(MODULE_ID, "autoSyncCompendiums")) {
    await CompendiumSync.syncAllPacks({ silent: true });
  }

  // Exportar API global do módulo
  const moduleObj = game.modules.get(MODULE_ID);
  if (moduleObj) {
    moduleObj.api = {
      CraftingEngine,
      HarvestingEngine,
      CraftingWorkshopApp,
      HarvestingApp,
      openWorkshop: (actor) => new CraftingWorkshopApp({ actor }).render(true),
      openHarvesting: (target, harvester) => new HarvestingApp({ target, harvester }).render(true),
      syncCompendiums: (force = false) => CompendiumSync.syncAllPacks({ force, silent: false })
    };
  }
});

/**
 * Injeção de botão no cabeçalho das fichas de personagem (D&D 5e Actor Sheet).
 */
Hooks.on("getActorSheetHeaderButtons", (sheet, buttons) => {
  if (!game.settings.get(MODULE_ID, "enableSheetButton")) return;
  const actor = sheet.actor;
  if (!actor || actor.type !== "character") return;

  buttons.unshift({
    label: game.i18n.localize("ITENSDND.Settings.Menu.Label") || "Oficina",
    class: "itensdnd-sheet-btn",
    icon: "fas fa-hammer",
    onclick: () => {
      new CraftingWorkshopApp({ actor }).render(true);
    }
  });
});
