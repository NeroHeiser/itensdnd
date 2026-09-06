/**
 * harvesting-app.mjs
 * Interface interativa ApplicationV2 para Colheita de Criaturas (Harvesting & Remnants).
 */

import { HarvestingEngine } from "../harvesting-engine.mjs";

const MODULE_ID = "itensdnd";

const BaseApplication = foundry.applications?.api?.HandlebarsApplicationMixin
  ? foundry.applications.api.HandlebarsApplicationMixin(foundry.applications.api.ApplicationV2)
  : Application;

export class HarvestingApp extends BaseApplication {
  constructor(options = {}) {
    super(options);
    this.harvester = options.harvester || this._getPrimaryHarvester();
    this.target = options.target || this._getPrimaryTarget();
  }

  static DEFAULT_OPTIONS = {
    id: "itensdnd-harvesting-app",
    classes: ["itensdnd", "harvesting-app"],
    tag: "div",
    window: {
      title: "ITENSDND.Harvesting.Title",
      icon: "fas fa-claw-marks",
      resizable: true
    },
    position: {
      width: 520,
      height: 480
    },
    actions: {
      selectHarvester: HarvestingApp.#onSelectHarvester,
      selectTarget: HarvestingApp.#onSelectTarget,
      rollHarvest: HarvestingApp.#onRollHarvest
    }
  };

  static PARTS = {
    harvesting: {
      template: "modules/itensdnd/templates/harvesting-app.hbs"
    }
  };

  _getPrimaryHarvester() {
    const controlled = canvas.tokens?.controlled[0]?.actor;
    if (controlled && controlled.type === "character") return controlled;
    const userChar = game.user.character;
    if (userChar) return userChar;
    return game.actors?.find(a => a.type === "character" && a.isOwner) || null;
  }

  _getPrimaryTarget() {
    const targetToken = Array.from(game.user.targets)[0]?.actor;
    if (targetToken) return targetToken;
    const tokens = canvas.tokens?.controlled || [];
    if (tokens.length >= 2) return tokens[1].actor;
    return null;
  }

  async _prepareContext(options = {}) {
    const characters = game.actors?.filter(a => a.type === "character" && a.isOwner) || [];
    const targets = canvas.tokens?.placeables?.map(t => t.actor).filter(a => a && a.id !== this.harvester?.id) || [];

    const targetCr = this.target?.system?.details?.cr ?? 1;
    const targetType = (this.target?.system?.details?.type?.value || "monstrosity").toLowerCase();
    const typeInfo = HarvestingEngine.SKILL_REQUIREMENTS[targetType] || { skill: "sur", label: "Sobrevivência" };
    const isRemnants = Boolean(typeInfo.remnants);
    const { dc } = HarvestingEngine.getTableAndDC(targetCr, isRemnants);

    let harvesterSkillMod = 0;
    if (this.harvester && !isRemnants) {
      harvesterSkillMod = this.harvester.system?.skills?.[typeInfo.skill]?.total ?? 0;
    }

    return {
      harvester: this.harvester,
      characters,
      target: this.target,
      targets,
      targetCr,
      targetType,
      typeInfo,
      isRemnants,
      dc,
      harvesterSkillMod
    };
  }

  static async #onSelectHarvester(event, target) {
    const actorId = target.value;
    this.harvester = game.actors.get(actorId) || null;
    this.render();
  }

  static async #onSelectTarget(event, target) {
    const actorId = target.value;
    this.target = game.actors.get(actorId) || null;
    this.render();
  }

  static async #onRollHarvest(event, target) {
    await HarvestingEngine.performHarvest(this.harvester, this.target);
    this.render();
  }
}

