import { CraftingEngine } from "../crafting-engine.mjs";

const MODULE_ID = "itensdnd";

const BaseApplication = (typeof foundry !== "undefined" && foundry.applications?.api?.HandlebarsApplicationMixin)
  ? foundry.applications.api.HandlebarsApplicationMixin(foundry.applications.api.ApplicationV2)
  : (typeof Application !== "undefined" ? Application : class {});

export class CraftingWorkshopApp extends BaseApplication {
  constructor(options = {}) {
    super(options);
    this.actor = options.actor || this._getPrimaryActor();
    this.activeProfession = "alchemy";
    this.selectedRecipeId = null;
    this.searchQuery = "";
    this._preserveSearchFocus = false;
    this.craftableOnly = false;
    this.searchDebounceMs = 150;
    this._searchTimeout = null;
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

  /**
   * Retrieves active crafting project state from actor flag or fallback.
   * @param {Actor} actor
   * @returns {{ recipeId: string|null, hours: number, consecutiveFailures: number }}
   */
  static getActiveProject(actor) {
    if (!actor) {
      return { recipeId: null, hours: 0, consecutiveFailures: 0 };
    }
    const flag = typeof actor.getFlag === "function"
      ? actor.getFlag(MODULE_ID, "activeProject")
      : actor.flags?.[MODULE_ID]?.activeProject;

    if (flag && typeof flag === "object") {
      return {
        recipeId: flag.recipeId || null,
        hours: Number(flag.hours) || 0,
        consecutiveFailures: Number(flag.consecutiveFailures) || 0
      };
    }
    return { recipeId: null, hours: 0, consecutiveFailures: 0 };
  }

  /**
   * Persists active crafting project state onto the actor document.
   * @param {Actor} actor
   * @param {object|null} project
   * @returns {Promise<void>}
   */
  static async setActiveProject(actor, project) {
    if (!actor) return;
    if (!project || !project.recipeId) {
      if (typeof actor.unsetFlag === "function") {
        await actor.unsetFlag(MODULE_ID, "activeProject");
      } else if (actor.flags?.[MODULE_ID]) {
        delete actor.flags[MODULE_ID].activeProject;
      }
    } else {
      const data = {
        recipeId: project.recipeId,
        hours: Number(project.hours) || 0,
        consecutiveFailures: Number(project.consecutiveFailures) || 0
      };
      if (typeof actor.setFlag === "function") {
        await actor.setFlag(MODULE_ID, "activeProject", data);
      } else {
        actor.flags = actor.flags || {};
        actor.flags[MODULE_ID] = actor.flags[MODULE_ID] || {};
        actor.flags[MODULE_ID].activeProject = data;
      }
    }
  }

  getActiveProject() {
    return CraftingWorkshopApp.getActiveProject(this.actor);
  }

  async setActiveProject(project) {
    return CraftingWorkshopApp.setActiveProject(this.actor, project);
  }

  _getPrimaryActor() {
    const controlled = typeof canvas !== "undefined" ? canvas.tokens?.controlled[0]?.actor : null;
    if (controlled && controlled.type === "character") return controlled;
    const userChar = typeof game !== "undefined" ? game.user?.character : null;
    if (userChar) return userChar;
    return (typeof game !== "undefined" ? game.actors?.find(a => a.type === "character" && a.isOwner) : null) || null;
  }

  /**
   * Filters recipes matching query against recipe name or result item.
   * @param {Array<object>} recipes
   * @param {string} query
   * @returns {Array<object>}
   */
  static filterRecipesBySearch(recipes, query) {
    if (!query || typeof query !== "string" || !query.trim()) return recipes;
    const q = query.trim().toLowerCase();
    return recipes.filter(r => (
      (r.name && r.name.toLowerCase().includes(q)) ||
      (r.resultItem && r.resultItem.toLowerCase().includes(q))
    ));
  }

  _onRender(context, options) {
    super._onRender?.(context, options);

    const searchInput = this.element?.querySelector('input[name="searchQuery"]');
    if (searchInput) {
      if (this._preserveSearchFocus) {
        searchInput.focus();
        const len = searchInput.value.length;
        searchInput.setSelectionRange(len, len);
        this._preserveSearchFocus = false;
      }

      searchInput.addEventListener("input", event => {
        this.searchQuery = event.target.value;
        this._preserveSearchFocus = true;
        if (this._searchTimeout) clearTimeout(this._searchTimeout);

        if (this.searchDebounceMs > 0) {
          this._searchTimeout = setTimeout(() => {
            this.render();
          }, this.searchDebounceMs);
        } else {
          this.render();
        }
      });
    }
  }

  async _prepareContext(options = {}) {
    const actors = (typeof game !== "undefined" ? game.actors?.filter(a => a.type === "character" && a.isOwner) : []) || [];
    const allRecipes = await CraftingEngine.getRecipes();

    const activeProject = this.getActiveProject();

    // Auto-select active project recipe if user hasn't explicitly picked a recipe
    if (activeProject.recipeId && !this.selectedRecipeId) {
      this.selectedRecipeId = activeProject.recipeId;
      const activeRecipe = allRecipes.find(r => (r.id === activeProject.recipeId || r.key === activeProject.recipeId));
      if (activeRecipe?.profession) {
        this.activeProfession = activeRecipe.profession;
      }
    }

    let recipes = allRecipes.filter(r => (r.profession || "alchemy") === this.activeProfession);
    recipes = CraftingWorkshopApp.filterRecipesBySearch(recipes, this.searchQuery);

    if (this.craftableOnly && this.actor) {
      recipes = recipes.filter(r => CraftingEngine.checkMaterials(this.actor, r).hasAll);
    }

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

    const currentHours = activeProject.recipeId === this.selectedRecipeId ? activeProject.hours : 0;
    const currentFailures = activeProject.recipeId === this.selectedRecipeId ? activeProject.consecutiveFailures : 0;
    const totalHoursNeeded = selectedRecipe?.time || 2;
    const progressPercent = Math.min(100, Math.round((currentHours / totalHoursNeeded) * 100));

    const professions = [
      { key: "alchemy", label: game.i18n.localize("ITENSDND.Workshop.Professions.alchemy"), icon: "fas fa-flask" },
      { key: "poisoncraft", label: game.i18n.localize("ITENSDND.Workshop.Professions.poisoncraft"), icon: "fas fa-skull-crossbones" },
      { key: "blacksmithing", label: game.i18n.localize("ITENSDND.Workshop.Professions.blacksmithing"), icon: "fas fa-gavel" },
      { key: "enchanting", label: game.i18n.localize("ITENSDND.Workshop.Professions.enchanting"), icon: "fas fa-wand-magic-sparkles" },
      { key: "leatherworking", label: game.i18n.localize("ITENSDND.Workshop.Professions.leatherworking"), icon: "fas fa-shield-alt" },
      { key: "tinkering", label: game.i18n.localize("ITENSDND.Workshop.Professions.tinkering"), icon: "fas fa-cogs" },
      { key: "scrollscribing", label: game.i18n.localize("ITENSDND.Workshop.Professions.scrollscribing"), icon: "fas fa-scroll" },
      { key: "wandwhittling", label: game.i18n.localize("ITENSDND.Workshop.Professions.wandwhittling"), icon: "fas fa-magic" },
      { key: "cooking", label: game.i18n.localize("ITENSDND.Workshop.Professions.cooking"), icon: "fas fa-utensils" }
    ];

    const canTake10 = Boolean(this.actor) && canCraft && ((10 + craftingMod.mod) >= (selectedRecipe?.dc || 0));
    const canRoll = Boolean(this.actor) && (canCraft || currentHours > 0) && currentFailures < 3;
    const canReset = currentHours > 0 || currentFailures > 0;

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
      canTake10,
      canRoll,
      canReset,
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

  static async #onSelectActor(event, target) {
    const actorId = target.value;
    this.actor = (typeof game !== "undefined" ? game.actors?.get(actorId) : null) || null;
    this.selectedRecipeId = null;
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

    let project = this.getActiveProject();
    if (project.recipeId !== this.selectedRecipeId) {
      const { hasAll } = CraftingEngine.checkMaterials(this.actor, recipe);
      if (!hasAll) {
        ui.notifications?.warn(game.i18n.localize("ITENSDND.Workshop.Notifications.NoMaterials"));
        return;
      }
      project = { recipeId: this.selectedRecipeId, hours: 0, consecutiveFailures: 0 };
    }

    const res = await CraftingEngine.rollCraftingAttempt(this.actor, recipe, project);
    if (res.status === "completed" || res.status === "failed") {
      await this.setActiveProject(null);
    } else {
      project.hours = res.newHours;
      project.consecutiveFailures = res.newFailures;
      await this.setActiveProject(project);
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
      await this.setActiveProject(null);
      this.render();
    }
  }

  static async #onResetProject(event, target) {
    await this.setActiveProject(null);
    this.render();
  }

  static async #onToggleFilter(event, target) {
    this.craftableOnly = target.checked;
    this.render();
  }
}
