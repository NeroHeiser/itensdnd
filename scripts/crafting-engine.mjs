const MODULE_ID = "itensdnd";

export class CraftingEngine {
  static TOOL_MAPPING = {
    alchemist: ["alchemist", "alchemists-supplies"],
    smith: ["smith", "smiths-tools"],
    leatherworker: ["leatherworker", "leatherworkers-tools"],
    tinker: ["tinker", "tinkers-tools"],
    calligrapher: ["calligrapher", "calligraphers-supplies"],
    woodcarver: ["woodcarver", "woodcarvers-tools"],
    cook: ["cook", "cooks-utensils"],
    poisoner: ["poisoner", "poisoners-kit"],
    jeweler: ["jeweler", "jewelers-tools"]
  };

  /**
   * Retrieves all available recipes from compendium or bundled fallback data.
   * @returns {Promise<Array<object>>}
   */
  static async getRecipes() {
    const pack = game.packs.get(`${MODULE_ID}.crafting-recipes`);
    if (pack) {
      const docs = await pack.getDocuments();
      if (docs.length > 0) {
        return docs.map(d => ({
          id: d.id,
          name: d.name,
          img: d.img,
          ...d.flags?.itensdnd,
          description: d.system?.description?.value || ""
        }));
      }
    }

    const isPt = game.i18n?.lang?.startsWith("pt");
    const lang = isPt ? "pt-BR" : "en";
    const baseRoute = typeof foundry !== "undefined" && foundry.utils?.getRoute ? foundry.utils.getRoute(`modules/${MODULE_ID}`) : `/modules/${MODULE_ID}`;
    let res = await fetch(`${baseRoute}/scripts/data/${lang}/crafting-recipes.json`).catch(() => null);
    if (!res || !res.ok) {
      res = await fetch(`modules/${MODULE_ID}/scripts/data/${lang}/crafting-recipes.json`).catch(() => null);
    }
    if (res && res.ok) {
      const data = await res.json();
      return data.map(d => ({
        id: d._id,
        name: d.name,
        img: d.img,
        ...d.flags?.itensdnd,
        description: d.system?.description?.value || ""
      }));
    }
    return [];
  }

  /**
   * Counts the total quantity of a material key present in actor items.
   * @param {Actor} actor
   * @param {string} materialKey
   * @returns {number}
   */
  static getMaterialCount(actor, materialKey) {
    if (!actor?.items) return 0;
    let count = 0;
    for (const item of actor.items) {
      const key = item.flags?.itensdnd?.materialKey;
      if (key === materialKey) {
        count += (item.system?.quantity || 1);
      }
    }
    return count;
  }

  /**
   * Verifies inventory availability for all required materials in a recipe.
   * @param {Actor} actor
   * @param {object} recipe
   * @returns {{ hasAll: boolean, materialsStatus: Array<object> }}
   */
  static checkMaterials(actor, recipe) {
    if (!recipe?.materials) return { hasAll: true, materialsStatus: [] };
    let hasAll = true;
    const materialsStatus = [];

    for (const req of recipe.materials) {
      const count = this.getMaterialCount(actor, req.key);
      const needed = req.quantity || 1;
      const satisfied = count >= needed;
      if (!satisfied) hasAll = false;

      materialsStatus.push({
        key: req.key,
        needed,
        have: count,
        satisfied
      });
    }

    return { hasAll, materialsStatus };
  }

  /**
   * Calculates actor crafting modifier based on tool proficiency and highest permitted ability.
   * @param {Actor} actor
   * @param {object} recipe
   * @returns {{ mod: number, profBonus: number, abilityMod: number, bestAbility: string, toolProficient: boolean }}
   */
  static calculateCraftingModifier(actor, recipe) {
    if (!actor) return { mod: 0, profBonus: 0, abilityMod: 0, bestAbility: "int", toolProficient: false };

    const prof = actor.system?.attributes?.prof || 2;
    let toolProficient = false;
    let profBonus = 0;

    if (recipe.profession === "enchanting" || recipe.tool === "arcana") {
      const arcSkill = actor.system?.skills?.arc;
      if (arcSkill) {
        const isProf = (arcSkill.value || 0) >= 1;
        toolProficient = isProf;
        profBonus = isProf ? (arcSkill.value * prof) : 0;
      }
    } else {
      const toolKeys = this.TOOL_MAPPING[recipe.tool] || [recipe.tool];
      const toolsData = actor.system?.tools || {};

      for (const tKey of toolKeys) {
        if (toolsData[tKey]?.value >= 1) {
          toolProficient = true;
          profBonus = toolsData[tKey].value * prof;
          break;
        }
      }

      if (!toolProficient && actor.items) {
        for (const item of actor.items) {
          if (item.type === "tool") {
            const itemKey = item.system?.baseItem || item.name.toLowerCase();
            if (toolKeys.some(k => itemKey.includes(k))) {
              if (item.system?.proficient >= 1) {
                toolProficient = true;
                profBonus = (item.system.proficient || 1) * prof;
                break;
              }
            }
          }
        }
      }

      if (!toolProficient && recipe.profession === "alchemy") {
        const herbKeys = ["herbalism", "herbalism-kit"];
        for (const hKey of herbKeys) {
          if (toolsData[hKey]?.value >= 1) {
            toolProficient = true;
            profBonus = toolsData[hKey].value * prof;
            break;
          }
        }
      }
    }

    const allowedAbilities = recipe.ability || ["int"];
    let bestAbility = allowedAbilities[0];
    let maxAbilityMod = -99;

    for (const abl of allowedAbilities) {
      const ablMod = actor.system?.abilities?.[abl]?.mod ?? 0;
      if (ablMod > maxAbilityMod) {
        maxAbilityMod = ablMod;
        bestAbility = abl;
      }
    }

    const totalMod = profBonus + maxAbilityMod;
    return {
      mod: totalMod,
      profBonus,
      abilityMod: maxAbilityMod,
      bestAbility,
      toolProficient
    };
  }

  /**
   * Executes a two-hour crafting work session with progress tracking and failure checks.
   * @param {Actor} actor
   * @param {object} recipe
   * @param {object} currentProgress
   * @returns {Promise<object>}
   */
  static async rollCraftingAttempt(actor, recipe, currentProgress = { hours: 0, consecutiveFailures: 0 }) {
    const { mod } = this.calculateCraftingModifier(actor, recipe);
    const roll = new Roll(`1d20 + ${mod}`);
    await roll.evaluate();

    const rollTotal = roll.total;
    const isSuccess = rollTotal >= recipe.dc;

    let newHours = currentProgress.hours;
    let newFailures = currentProgress.consecutiveFailures;
    let status = "inProgress";

    if (isSuccess) {
      newHours += 2;
      newFailures = 0;
      if (newHours >= recipe.time) {
        status = "completed";
      }
    } else {
      newFailures += 1;
      if (newFailures >= 3) {
        status = "failed";
      }
    }

    if (status === "completed") {
      await this.consumeMaterials(actor, recipe);
      await this.awardCraftedItem(actor, recipe);
    } else if (status === "failed") {
      await this.consumeMaterials(actor, recipe);
    }

    await this.postCraftingChatMessage(actor, recipe, roll, isSuccess, newHours, newFailures, status, false);

    return {
      roll,
      rollTotal,
      isSuccess,
      newHours,
      newFailures,
      status
    };
  }

  /**
   * Resolves crafting attempt under Take 10 rule (guaranteed success for double crafting time).
   * @param {Actor} actor
   * @param {object} recipe
   * @returns {Promise<boolean>}
   */
  static async take10Crafting(actor, recipe) {
    const { mod } = this.calculateCraftingModifier(actor, recipe);
    const take10Score = 10 + mod;

    if (take10Score < recipe.dc) {
      ui.notifications?.warn(
        game.i18n.format?.("ITENSDND.Workshop.Notifications.Take10Insufficient", { mod, score: take10Score, dc: recipe.dc }) ||
        `Total modifier (${mod}) + 10 = ${take10Score}, insufficient to meet DC ${recipe.dc}.`
      );
      return false;
    }

    const { hasAll } = this.checkMaterials(actor, recipe);
    if (!hasAll) {
      ui.notifications?.warn(game.i18n.localize("ITENSDND.Workshop.Notifications.NoMaterials"));
      return false;
    }

    const totalHours = recipe.time * 2;
    await this.consumeMaterials(actor, recipe);
    await this.awardCraftedItem(actor, recipe);

    const content = `
      <div class="itensdnd chat-card crafting-card">
        <header class="card-header flexrow">
          <img src="${recipe.img || 'icons/tools/smithing/anvil.webp'}" title="${recipe.name}" width="36" height="36"/>
          <h3>${recipe.name}</h3>
        </header>
        <div class="card-content">
          <p><strong>${game.i18n.localize("ITENSDND.Workshop.Recipe.Take10")}</strong></p>
          <p>${actor.name} worked carefully and diligently for ${totalHours} hours.</p>
          <p class="success-banner" style="color: #2e7d32; font-weight: bold;">
            <i class="fas fa-check-circle"></i> ${game.i18n.localize("ITENSDND.Workshop.Notifications.Take10Complete")}
          </p>
        </div>
      </div>
    `;

    const messageData = CraftingEngine.buildChatMessageData({
      user: game.user.id,
      speaker: ChatMessage.getSpeaker({ actor }),
      content,
      isRoll: false
    });

    await ChatMessage.create(messageData);

    return true;
  }

  /**
   * Consumes required recipe materials from actor inventory.
   * @param {Actor} actor
   * @param {object} recipe
   */
  static async consumeMaterials(actor, recipe) {
    if (!recipe.materials) return;

    for (const req of recipe.materials) {
      let remainingToDeduct = req.quantity || 1;
      const itemsToUpdate = [];
      const itemsToDelete = [];

      for (const item of actor.items) {
        if (remainingToDeduct <= 0) break;
        if (item.flags?.itensdnd?.materialKey === req.key) {
          const currentQty = item.system?.quantity || 1;
          if (currentQty > remainingToDeduct) {
            itemsToUpdate.push({ _id: item.id, "system.quantity": currentQty - remainingToDeduct });
            remainingToDeduct = 0;
          } else {
            remainingToDeduct -= currentQty;
            itemsToDelete.push(item.id);
          }
        }
      }

      if (itemsToUpdate.length > 0) {
        await actor.updateEmbeddedDocuments("Item", itemsToUpdate);
      }
      if (itemsToDelete.length > 0) {
        await actor.deleteEmbeddedDocuments("Item", itemsToDelete);
      }
    }
  }

  /**
   * Creates the resulting item document in actor inventory.
   * @param {Actor} actor
   * @param {object} recipe
   */
  static async awardCraftedItem(actor, recipe) {
    const resName = recipe.resultItem || recipe.name.replace(/^Receita: |^Recipe: /, "");
    let finalItemData = null;

    try {
      const pack = game.packs.get("itensdnd.crafting-items");
      if (pack) {
        await pack.getIndex();
        const targetId = recipe.flags?.itensdnd?.resultItemId || recipe.resultItemId;
        let compendiumDoc = null;

        if (targetId) {
          compendiumDoc = await pack.getDocument(targetId).catch(() => null);
        }
        if (!compendiumDoc) {
          const entry = pack.index.find(e => e.name === resName || e.name.toLowerCase() === resName.toLowerCase());
          if (entry) {
            compendiumDoc = await pack.getDocument(entry._id).catch(() => null);
          }
        }

        if (compendiumDoc) {
          finalItemData = compendiumDoc.toObject();
          delete finalItemData._id;
          if (finalItemData.system) {
            finalItemData.system.quantity = 1;
          }
        }
      }
    } catch (err) {
      console.warn("itensdnd | Could not retrieve item from compendium, using fallback:", err);
    }

    if (!finalItemData) {
      finalItemData = {
        name: resName,
        type: "consumable",
        img: recipe.img || "icons/commodities/treasure/chest-wooden.webp",
        system: {
          description: { value: `<p>Crafted in the workshop by ${actor.name}.</p>` },
          quantity: 1,
          rarity: recipe.rarity || "common"
        }
      };

      if (recipe.profession === "blacksmithing") {
        const lower = recipe.name.toLowerCase();
        finalItemData.type = lower.includes("armadura") || lower.includes("armor") || lower.includes("escudo") || lower.includes("shield") ? "equipment" : "weapon";
      }
    }

    await actor.createEmbeddedDocuments("Item", [finalItemData]);
    ui.notifications?.info(`${game.i18n.localize("ITENSDND.Workshop.Notifications.CraftComplete")}: ${finalItemData.name}`);
  }

  /**
   * Publishes crafting check card to chat.
   */
  static async postCraftingChatMessage(actor, recipe, roll, isSuccess, newHours, newFailures, status, isTake10) {
    const successColor = isSuccess ? "#2e7d32" : "#c62828";
    const failuresLabel = game.i18n.localize("ITENSDND.Workshop.Notifications.ConsecutiveFailures") || "Consecutive failures";
    const statusText = isSuccess
      ? `<span style="color: ${successColor}; font-weight: bold;"><i class="fas fa-check"></i> ${game.i18n.localize("ITENSDND.Workshop.Notifications.CraftSuccess")}</span>`
      : `<span style="color: ${successColor}; font-weight: bold;"><i class="fas fa-times"></i> ${game.i18n.localize("ITENSDND.Workshop.Notifications.CraftFailure")} (${failuresLabel}: ${newFailures}/3)</span>`;

    let completionBanner = "";
    if (status === "completed") {
      completionBanner = `
        <div style="background: #e8f5e9; border: 1px solid #4caf50; padding: 6px; border-radius: 4px; margin-top: 6px; text-align: center; color: #1b5e20;">
          <strong><i class="fas fa-check-circle"></i> ${game.i18n.localize("ITENSDND.Chat.ItemCompleted")}: ${recipe.resultItem}</strong>
        </div>`;
    } else if (status === "failed") {
      completionBanner = `
        <div style="background: #ffebee; border: 1px solid #f44336; padding: 6px; border-radius: 4px; margin-top: 6px; text-align: center; color: #b71c1c;">
          <strong><i class="fas fa-exclamation-triangle"></i> ${game.i18n.localize("ITENSDND.Workshop.Notifications.CraftDestroyed")}</strong>
        </div>`;
    }

    const rollHtml = await roll.render();
    const dcLabel = game.i18n.localize("ITENSDND.Workshop.Recipe.DC") || "DC";
    const progressLabel = game.i18n.localize("ITENSDND.Workshop.Progress") || "Progress";
    const hoursLabel = game.i18n.localize("ITENSDND.Workshop.Recipe.Hours") || "hours";

    const content = `
      <div class="itensdnd chat-card crafting-card">
        <header class="card-header flexrow" style="display: flex; align-items: center; gap: 8px; border-bottom: 1px solid #ccc; padding-bottom: 4px;">
          <img src="${recipe.img}" width="32" height="32" style="border: none; border-radius: 4px;"/>
          <div>
            <h3 style="margin: 0; font-size: 1.1em;">${recipe.name}</h3>
            <span style="font-size: 0.85em; color: #666;">${dcLabel} ${recipe.dc} | ${progressLabel}: ${newHours}/${recipe.time} ${hoursLabel}</span>
          </div>
        </header>
        <div class="card-content" style="margin-top: 6px;">
          <div>${statusText}</div>
          <div style="margin-top: 4px;">${rollHtml}</div>
          ${completionBanner}
        </div>
      </div>
    `;

    const messageData = CraftingEngine.buildChatMessageData({
      user: game.user.id,
      speaker: ChatMessage.getSpeaker({ actor }),
      content,
      rolls: [roll],
      sound: isSuccess ? CONFIG.sounds?.dice : null,
      isRoll: true
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
