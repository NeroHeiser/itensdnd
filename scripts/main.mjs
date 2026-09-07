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

  game.settings.registerMenu(MODULE_ID, "syncMenu", {
    name: "ITENSDND.Settings.SyncMenu.Name",
    label: "ITENSDND.Settings.SyncMenu.Label",
    hint: "ITENSDND.Settings.SyncMenu.Hint",
    icon: "fas fa-sync-alt",
    type: class SyncCompendiumsForm extends FormApplication {
      static get defaultOptions() {
        return foundry.utils.mergeObject(super.defaultOptions, {
          title: "Sincronizar Compêndios de Crafting",
          template: "templates/generic-form.html",
          width: 400,
          height: "auto"
        });
      }
      async render() {
        new Dialog({
          title: "Sincronizar Compêndios",
          content: "<p>Deseja sincronizar e carregar todos os <strong>478 itens criáveis, 478 receitas, 92 materiais e 15 tabelas</strong> do Kibbles nos compêndios?</p>",
          buttons: {
            confirm: {
              icon: '<i class="fas fa-sync"></i>',
              label: "Sincronizar Agora",
              callback: async () => {
                ui.notifications?.info("Iniciando sincronização dos compêndios...");
                await CompendiumSync.syncAllPacks({ force: true, silent: false });
              }
            },
            cancel: {
              icon: '<i class="fas fa-times"></i>',
              label: "Cancelar"
            }
          },
          default: "confirm"
        }).render(true);
      }
    },
    restricted: true
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
  // Pré-carregamento de templates Handlebars
  loadTemplates([
    "modules/itensdnd/templates/crafting-app.hbs",
    "modules/itensdnd/templates/harvesting-app.hbs"
  ]);
});

/**
 * Hook de Inicialização Completa (ready).
 */
Hooks.once("ready", async () => {
  console.log("Itens & Sistema de Crafting D&D 5e | Sistema pronto!");

  // Sincronização automática ou recuperação de compêndios vazios
  if (game.user.isGM) {
    await CompendiumSync.checkAndSyncAllPacks({ silent: false });
  }

  // Exportar API global do módulo
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

/**
 * Injeção de botão no cabeçalho das fichas de personagem (D&D 5e Actor Sheet).
 * Suporte aprimorado para ActorSheet5eCharacter2 (dnd5e v3/v4) e fichas clássicas.
 */
function addSheetWorkshopButton(app, buttons) {
  try {
    if (!game.settings.get(MODULE_ID, "enableSheetButton")) return;
  } catch (e) {}

  const actor = app.actor || app.document;
  if (!actor || actor.type !== "character") return;

  // Evitar duplicatas
  if (buttons.some(b => b.class === "itensdnd-sheet-btn")) return;

  buttons.unshift({
    label: game.i18n.localize("ITENSDND.Settings.Menu.Label") || "Oficina",
    class: "itensdnd-sheet-btn",
    icon: "fas fa-hammer",
    onclick: () => {
      new CraftingWorkshopApp({ actor }).render({ force: true });
    }
  });
}

// 1. Hook global de cabeçalho de aplicações (compatível com dnd5e 3+ ActorSheet5eCharacter2)
Hooks.on("getApplicationHeaderButtons", (app, buttons) => {
  addSheetWorkshopButton(app, buttons);
});

// 2. Hook legado de fichas de ator (ApplicationV1 e temas alternativos)
Hooks.on("getActorSheetHeaderButtons", (sheet, buttons) => {
  addSheetWorkshopButton(sheet, buttons);
});

// 3. Injeção direta no render da ficha (tanto no topo da janela quanto no painel de descanso)
Hooks.on("renderActorSheet", (app, html) => {
  try {
    if (!game.settings.get(MODULE_ID, "enableSheetButton")) return;
  } catch (e) {}

  const actor = app.actor || app.document;
  if (!actor || actor.type !== "character") return;

  const root = html instanceof HTMLElement ? html : html[0];
  if (!root) return;

  // 1. Injetar na barra de título da janela (.window-header)
  const windowApp = root.closest(".window-app") || document.getElementById(app.id) || (app.element ? (app.element[0] || app.element) : null);
  const header = windowApp?.querySelector(".window-header");
  if (header && !header.querySelector(".itensdnd-sheet-btn")) {
    const btn = document.createElement("a");
    btn.className = "header-button control itensdnd-sheet-btn";
    btn.innerHTML = '<i class="fas fa-hammer"></i> ' + (game.i18n.localize("ITENSDND.Settings.Menu.Label") || "Oficina");
    btn.title = game.i18n.localize("ITENSDND.Settings.Menu.Hint") || "Abrir Oficina de Criação";
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

  // 2. Injetar botão elegante dentro da ficha do D&D 5e v3 (ao lado dos botões de descanso)
  const restContainer = root.querySelector(".sheet-header .header-actions, .sheet-header .character-details, [data-action='rest']");
  if (restContainer && !root.querySelector(".itensdnd-sheet-inner-btn")) {
    const craftBtn = document.createElement("button");
    craftBtn.type = "button";
    craftBtn.className = "itensdnd-sheet-inner-btn";
    craftBtn.title = game.i18n.localize("ITENSDND.Settings.Menu.Label") || "Oficina de Criação";
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


