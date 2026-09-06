/**
 * crafting-app.mjs
 * Interface interativa ApplicationV2 para a Oficina de Criação (Kibbles' Crafting Guide).
 */

import { CraftingEngine } from "../crafting-engine.mjs";

const MODULE_ID = "itensdnd";

const BaseApplication = foundry.applications?.api?.HandlebarsApplicationMixin
  ? foundry.applications.api.HandlebarsApplicationMixin(foundry.applications.api.ApplicationV2)
  : Application;

export class CraftingWorkshopApp extends BaseApplication {
  constructor(options = {}) {
    super(options);
    this.actor = options.actor || this._getPrimaryActor();
    this.activeProfession = "alchemy";
    this.selectedRecipeId = null;
    this.searchQuery = "";
    this.craftableOnly = false;
    this.activeProject = {
      recipeId: null,
      hours: 0,
      consecutiveFailures: 0
    };
  }

  static DEFAULT_OPTIONS = {
    id: "itensdnd-crafting-workshop",
    classes: ["itensdnd", "crafting-workshop"],
    tag: "div",
    window: {
      title: "ITENSDND.Workshop.Title",
      icon: "fas fa-hammer",
      resizable: true
    },
    position: {
      width: 800,
      height: 700
    },
    actions: {
      selectActor: CraftingWorkshopApp.#onSelectActor,
      changeProfession: CraftingWorkshopApp.#onChangeProfession,
      selectRecipe: CraftingWorkshopApp.#onSelectRecipe,
      rollAttempt: CraftingWorkshopApp.#onRollAttempt,
      take10: CraftingWorkshopApp.#onTake10,
      resetProject: CraftingWorkshopApp.#onResetProject,
      toggleFilter: CraftingWorkshopApp.#onToggleFilter
    }
  };

  static PARTS = {
    workshop: {
      template: "modules/itensdnd/templates/crafting-app.hbs"
    }
  };

  _getPrimaryActor() {
    const controlled = canvas.tokens?.controlled[0]?.actor;
    if (controlled && controlled.type === "character") return controlled;
    const userChar = game.user.character;
    if (userChar) return userChar;
    return game.actors?.find(a => a.type === "character" && a.isOwner) || null;
  }

  async _prepareContext(options = {}) {
    const actors = game.actors?.filter(a => a.type === "character" && a.isOwner) || [];
    const allRecipes = await CraftingEngine.getRecipes();

    // Filtra por profissão ativa
    let recipes = allRecipes.filter(r => (r.profession || "alchemy") === this.activeProfession);

    // Filtro de busca por nome
    if (this.searchQuery.trim()) {
      const q = this.searchQuery.toLowerCase();
      recipes = recipes.filter(r => r.name.toLowerCase().includes(q) || (r.resultItem && r.resultItem.toLowerCase().includes(q)));
    }

    // Filtro de receitas criáveis
    if (this.craftableOnly && this.actor) {
      recipes = recipes.filter(r => CraftingEngine.checkMaterials(this.actor, r).hasAll);
    }

    // Se nenhuma receita selecionada, pega a primeira da lista
    let selectedRecipe = recipes.find(r => r.id === this.selectedRecipeId || r.key === this.selectedRecipeId);
    if (!selectedRecipe && recipes.length > 0) {
      selectedRecipe = recipes[0];
      this.selectedRecipeId = selectedRecipe.id || selectedRecipe.key;
    }

    let materialsStatus = [];
    let canCraft = false;
    let craftingMod = { mod: 0, bestAbility: "int", profBonus: 0, toolProficient: false };

    if (selectedRecipe && this.actor) {
      const check = CraftingEngine.checkMaterials(this.actor, selectedRecipe);
      materialsStatus = check.materialsStatus;
      canCraft = check.hasAll;
      craftingMod = CraftingEngine.calculateCraftingModifier(this.actor, selectedRecipe);
    }

    const currentHours = this.activeProject.recipeId === this.selectedRecipeId ? this.activeProject.hours : 0;
    const currentFailures = this.activeProject.recipeId === this.selectedRecipeId ? this.activeProject.consecutiveFailures : 0;
    const totalHoursNeeded = selectedRecipe?.time || 2;
    const progressPercent = Math.min(100, Math.round((currentHours / totalHoursNeeded) * 100));

    const professions = [
      { key: "alchemy", label: game.i18n.localize("ITENSDND.Workshop.Professions.alchemy"), icon: "fas fa-flask" },
      { key: "blacksmithing", label: game.i18n.localize("ITENSDND.Workshop.Professions.blacksmithing"), icon: "fas fa-gavel" },
      { key: "enchanting", label: game.i18n.localize("ITENSDND.Workshop.Professions.enchanting"), icon: "fas fa-wand-magic-sparkles" },
      { key: "leatherworking", label: game.i18n.localize("ITENSDND.Workshop.Professions.leatherworking"), icon: "fas fa-shield-alt" },
      { key: "tinkering", label: game.i18n.localize("ITENSDND.Workshop.Professions.tinkering"), icon: "fas fa-cogs" },
      { key: "scrollscribing", label: game.i18n.localize("ITENSDND.Workshop.Professions.scrollscribing"), icon: "fas fa-scroll" },
      { key: "wandwhittling", label: game.i18n.localize("ITENSDND.Workshop.Professions.wandwhittling"), icon: "fas fa-magic" },
      { key: "cooking", label: game.i18n.localize("ITENSDND.Workshop.Professions.cooking"), icon: "fas fa-utensils" }
    ];

    return {
      actor: this.actor,
      actors,
      professions,
      activeProfession: this.activeProfession,
      recipes,
      selectedRecipe,
      materialsStatus,
      canCraft,
      craftingMod,
      progress: {
        hours: currentHours,
        total: totalHoursNeeded,
        percent: progressPercent,
        consecutiveFailures: currentFailures
      },
      searchQuery: this.searchQuery,
      craftableOnly: this.craftableOnly
    };
  }

  // Ações da Interface
  static async #onSelectActor(event, target) {
    const actorId = target.value;
    this.actor = game.actors.get(actorId) || null;
    this.render();
  }

  static async #onChangeProfession(event, target) {
    this.activeProfession = target.dataset.profession || "alchemy";
    this.selectedRecipeId = null;
    this.render();
  }

  static async #onSelectRecipe(event, target) {
    this.selectedRecipeId = target.dataset.recipeId;
    this.render();
  }

  static async #onRollAttempt(event, target) {
    if (!this.actor) {
      ui.notifications?.warn(game.i18n.localize("ITENSDND.Workshop.Notifications.SelectActorFirst"));
      return;
    }

    const allRecipes = await CraftingEngine.getRecipes();
    const recipe = allRecipes.find(r => (r.id === this.selectedRecipeId || r.key === this.selectedRecipeId));
    if (!recipe) return;

    if (this.activeProject.recipeId !== this.selectedRecipeId) {
      // Inicia novo projeto
      const { hasAll } = CraftingEngine.checkMaterials(this.actor, recipe);
      if (!hasAll) {
        ui.notifications?.warn(game.i18n.localize("ITENSDND.Workshop.Notifications.NoMaterials"));
        return;
      }
      this.activeProject = { recipeId: this.selectedRecipeId, hours: 0, consecutiveFailures: 0 };
    }

    const res = await CraftingEngine.rollCraftingAttempt(this.actor, recipe, this.activeProject);
    this.activeProject.hours = res.newHours;
    this.activeProject.consecutiveFailures = res.newFailures;

    if (res.status === "completed" || res.status === "failed") {
      this.activeProject = { recipeId: null, hours: 0, consecutiveFailures: 0 };
    }

    this.render();
  }

  static async #onTake10(event, target) {
    if (!this.actor) {
      ui.notifications?.warn(game.i18n.localize("ITENSDND.Workshop.Notifications.SelectActorFirst"));
      return;
    }

    const allRecipes = await CraftingEngine.getRecipes();
    const recipe = allRecipes.find(r => (r.id === this.selectedRecipeId || r.key === this.selectedRecipeId));
    if (!recipe) return;

    const ok = await CraftingEngine.take10Crafting(this.actor, recipe);
    if (ok) {
      this.activeProject = { recipeId: null, hours: 0, consecutiveFailures: 0 };
      this.render();
    }
  }

  static async #onResetProject(event, target) {
    this.activeProject = { recipeId: null, hours: 0, consecutiveFailures: 0 };
    this.render();
  }

  static async #onToggleFilter(event, target) {
    this.craftableOnly = target.checked;
    this.render();
  }
}

