const MODULE_ID = "itensdnd";

export class HarvestingEngine {
  static SKILL_REQUIREMENTS = {
    dragon: { skill: "med", ability: "wis", label: "Medicine (Wisdom)" },
    monstrosity: { skill: "med", ability: "wis", label: "Medicine (Wisdom)" },
    giant: { skill: "med", ability: "wis", label: "Medicine (Wisdom)" },
    construct: { skill: "arc", ability: "int", label: "Arcana (Intelligence)" },
    plant: { skill: "nat", ability: "int", label: "Nature (Intelligence)" },
    beast: { skill: "sur", ability: "wis", label: "Survival (Wisdom)" },
    aberration: { skill: "arc", ability: "int", label: "Arcana (Intelligence)" },
    undead: { skill: "arc", ability: "int", label: "Arcana (Intelligence)" },
    celestial: { remnants: true, label: "Magical Remnants (Automatic)" },
    fiend: { remnants: true, label: "Magical Remnants (Automatic)" },
    elemental: { remnants: true, label: "Magical Remnants (Automatic)" }
  };

  /**
   * Parses challenge rating into a valid positive number supporting fractional strings (e.g., "1/4", "1/2").
   * @param {number|string} cr
   * @returns {number}
   */
  static parseChallengeRating(cr) {
    if (typeof cr === "number") return isNaN(cr) ? 0 : Math.max(0, cr);
    if (typeof cr === "string") {
      const trimmed = cr.trim();
      if (trimmed.includes("/")) {
        const [numerator, denominator] = trimmed.split("/").map(Number);
        if (denominator && !isNaN(numerator) && !isNaN(denominator)) {
          return Math.max(0, numerator / denominator);
        }
      }
      const parsed = Number(trimmed);
      return isNaN(parsed) ? 0 : Math.max(0, parsed);
    }
    return 0;
  }

  /**
   * Determines roll table key and DC from creature challenge rating or remnants rule.
   * @param {number|string} cr
   * @param {boolean} isRemnants
   * @returns {{ tableKey: string, dc: number }}
   */
  static getTableAndDC(cr = 1, isRemnants = false) {
    if (isRemnants) {
      return { tableKey: "harvesting-remnants-0-4", dc: 0 };
    }

    const numericCr = this.parseChallengeRating(cr);

    if (numericCr <= 4) {
      return { tableKey: "harvesting-cr-0-4", dc: 8 };
    } else if (numericCr <= 10) {
      return { tableKey: "harvesting-cr-5-10", dc: 10 };
    } else if (numericCr <= 16) {
      return { tableKey: "harvesting-cr-11-16", dc: 12 };
    } else {
      return { tableKey: "harvesting-cr-17-plus", dc: 14 };
    }
  }

  /**
   * Executes creature harvesting between harvester and target actor.
   * @param {Actor} harvester
   * @param {Actor} target
   * @param {object} options
   */
  static async performHarvest(harvester, target, options = {}) {
    if (!harvester) {
      ui.notifications?.warn(game.i18n.localize("ITENSDND.Harvesting.Notifications.SelectHarvester") || "Select a harvesting character.");
      return;
    }
    if (!target) {
      ui.notifications?.warn(game.i18n.localize("ITENSDND.Harvesting.Notifications.SelectTarget") || "Select a target for harvesting.");
      return;
    }

    const rawCr = target.system?.details?.cr ?? 1;
    const cr = this.parseChallengeRating(rawCr);
    const typeStr = (target.system?.details?.type?.value || "monstrosity").toLowerCase();
    const typeInfo = this.SKILL_REQUIREMENTS[typeStr] || { skill: "sur", ability: "wis", label: "Survival" };

    const isRemnants = Boolean(typeInfo.remnants);
    const { tableKey, dc } = this.getTableAndDC(cr, isRemnants);

    let isSuccess = true;
    let roll = null;

    if (!isRemnants) {
      const skillMod = harvester.system?.skills?.[typeInfo.skill]?.total ?? 0;
      roll = new Roll(`1d20 + ${skillMod}`);
      await roll.evaluate();
      isSuccess = roll.total >= dc;
    }

    const pack = game.packs.get(`${MODULE_ID}.crafting-tables`);
    let table = null;
    if (pack) {
      const index = await pack.getIndex();
      const entry = index.find(e => e.name.toLowerCase().includes(tableKey) || e.id.includes(tableKey));
      if (entry) table = await pack.getDocument(entry._id);
    }

    let resultText = "Common Curative Reagent";
    let drawnItemKey = "reagent-curative-common";
    let drawnQty = 1;

    if (table) {
      const draw = await table.draw({ displayChat: false });
      const res = draw.results[0];
      if (res) {
        resultText = res.text;
        drawnItemKey = res.flags?.itensdnd?.itemKey || "reagent-curative-common";
        drawnQty = res.flags?.itensdnd?.qty || 1;
      }
    }

    if (isSuccess) {
      await this.awardHarvestMaterial(harvester, drawnItemKey, drawnQty, resultText);
    }

    await this.postHarvestChatMessage(harvester, target, roll, dc, isSuccess, isRemnants, resultText, drawnQty);
  }

  /**
   * Adds harvested material to harvester inventory.
   * @param {Actor} harvester
   * @param {string} itemKey
   * @param {number} qty
   * @param {string} label
   */
  static async awardHarvestMaterial(harvester, itemKey, qty, label) {
    const pack = game.packs.get(`${MODULE_ID}.crafting-materials`);
    let itemData = null;

    if (pack) {
      const docs = await pack.getDocuments();
      const match = docs.find(d => d.flags?.itensdnd?.materialKey === itemKey);
      if (match) {
        itemData = match.toObject();
        itemData.system.quantity = qty;
      }
    }

    if (!itemData) {
      itemData = {
        name: label,
        type: "loot",
        img: "icons/consumables/potions/potion-tube-corked-green.webp",
        system: {
          quantity: qty,
          rarity: "common",
          price: { value: 5, denomination: "gp" }
        },
        flags: { itensdnd: { materialKey: itemKey } }
      };
    }

    const existing = harvester.items.find(i => i.flags?.itensdnd?.materialKey === itemKey);
    if (existing) {
      const cur = existing.system?.quantity || 1;
      await existing.update({ "system.quantity": cur + qty });
    } else {
      await harvester.createEmbeddedDocuments("Item", [itemData]);
    }

    const completeMsg = game.i18n.format?.("ITENSDND.Harvesting.Notifications.HarvestComplete", { qty, item: itemData.name }) ||
      `Harvesting complete: +${qty}x ${itemData.name}`;
    ui.notifications?.info(completeMsg);
  }

  /**
   * Publishes harvest card to chat.
   */
  static async postHarvestChatMessage(harvester, target, roll, dc, isSuccess, isRemnants, resultText, qty) {
    let rollHtml = "";
    if (roll) {
      rollHtml = await roll.render();
    }

    const title = isRemnants
      ? `${game.i18n.localize("ITENSDND.Harvesting.RemnantsTitle") || "Magical Remnants Collection"}: ${target.name}`
      : `${game.i18n.localize("ITENSDND.Harvesting.HarvestTitle") || "Creature Harvesting"}: ${target.name} (CR ${target.system?.details?.cr ?? 1})`;

    const harvesterLabel = game.i18n.localize("ITENSDND.Harvesting.Harvester") || "Harvester";
    const successMsg = game.i18n.format?.("ITENSDND.Harvesting.SuccessMessage", { item: resultText }) ||
      `Success! Obtained: <strong>${resultText}</strong>`;
    const failureMsg = game.i18n.format?.("ITENSDND.Harvesting.FailureMessage", { dc }) ||
      `Check failed (DC ${dc}). No viable materials could be recovered.`;

    const statusBanner = isSuccess
      ? `<div style="color: #2e7d32; font-weight: bold; margin-top: 4px;"><i class="fas fa-check-circle"></i> ${successMsg}</div>`
      : `<div style="color: #c62828; font-weight: bold; margin-top: 4px;"><i class="fas fa-times-circle"></i> ${failureMsg}</div>`;

    const content = `
      <div class="itensdnd chat-card harvest-card">
        <header class="card-header flexrow" style="display: flex; align-items: center; gap: 8px; border-bottom: 1px solid #ccc; padding-bottom: 4px;">
          <img src="${target.img || 'icons/svg/mystery-man.svg'}" width="32" height="32" style="border: none; border-radius: 4px;"/>
          <div>
            <h3 style="margin: 0; font-size: 1.1em;">${title}</h3>
            <span style="font-size: 0.85em; color: #666;">${harvesterLabel}: ${harvester.name}</span>
          </div>
        </header>
        <div class="card-content" style="margin-top: 6px;">
          ${rollHtml}
          ${statusBanner}
        </div>
      </div>
    `;

    const messageData = HarvestingEngine.buildChatMessageData({
      user: game.user.id,
      speaker: ChatMessage.getSpeaker({ actor: harvester }),
      content,
      rolls: roll ? [roll] : [],
      isRoll: Boolean(roll)
    });

    await ChatMessage.create(messageData);
  }

  /**
   * Prepares chat message data conforming to Foundry V12+ style property or V11 type fallback.
   * @param {object} params
   * @returns {object}
   */
  static buildChatMessageData({ user, speaker, content, rolls, sound, isRoll = false }) {
    const data = { user, speaker, content };
    if (rolls) data.rolls = rolls;
    if (sound) data.sound = sound;

    if (typeof CONST !== "undefined" && CONST.CHAT_MESSAGE_STYLES) {
      data.style = isRoll ? (CONST.CHAT_MESSAGE_STYLES.ROLL ?? 5) : (CONST.CHAT_MESSAGE_STYLES.OTHER ?? 0);
    } else {
      data.type = isRoll
        ? (typeof CONST !== "undefined" ? CONST.CHAT_MESSAGE_TYPES?.ROLL ?? 5 : 5)
        : (typeof CONST !== "undefined" ? CONST.CHAT_MESSAGE_TYPES?.OTHER ?? 0 : 0);
    }
    return data;
  }
}
