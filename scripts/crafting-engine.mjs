/**
 * crafting-engine.mjs
 * Motor de lógica de criação de itens para itensdnd (Kibbles' Crafting Guide).
 * Gerencia validação de inventário, cálculo de bônus, rolagens, regra de 3 falhas e Take 10.
 */

const MODULE_ID = "itensdnd";

export class CraftingEngine {
  /**
   * Mapeamento de ferramentas do Kibbles para identificadores de ferramentas do sistema dnd5e
   */
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
   * Obtém todas as receitas disponíveis no compêndio ou carregadas do módulo.
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

    // Fallback para arquivo JSON direto se o compêndio ainda não estiver montado
    const isPt = game.i18n?.lang?.startsWith("pt");
    const lang = isPt ? "pt-BR" : "en";
    const res = await fetch(`modules/${MODULE_ID}/scripts/data/${lang}/crafting-recipes.json`);
    if (res.ok) {
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
   * Verifica a quantidade de um material específico no inventário do ator.
   * @param {Actor} actor
   * @param {string} materialKey
   * @returns {number} Quantidade encontrada
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
   * Avalia os materiais de uma receita para o ator informado.
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
   * Calcula o bônus de criação (Crafting Modifier) do ator para uma determinada receita.
   * Fórmula Kibbles: Bônus de Proficiência da Ferramenta + Modificador do Atributo Relevante
   * @param {Actor} actor
   * @param {object} recipe
   * @returns {{ mod: number, profBonus: number, abilityMod: number, bestAbility: string, toolProficient: boolean }}
   */
  static calculateCraftingModifier(actor, recipe) {
    if (!actor) return { mod: 0, profBonus: 0, abilityMod: 0, bestAbility: "int", toolProficient: false };

    const prof = actor.system?.attributes?.prof || 2;
    let toolProficient = false;
    let profBonus = 0;

    // Caso de Encantamento (usa Arcanismo)
    if (recipe.profession === "enchanting" || recipe.tool === "arcana") {
      const arcSkill = actor.system?.skills?.arc;
      if (arcSkill) {
        const isProf = (arcSkill.value || 0) >= 1;
        toolProficient = isProf;
        profBonus = isProf ? (arcSkill.value * prof) : 0;
      }
    } else {
      // Ferramentas comuns
      const toolKeys = this.TOOL_MAPPING[recipe.tool] || [recipe.tool];
      const toolsData = actor.system?.tools || {};

      for (const tKey of toolKeys) {
        if (toolsData[tKey]?.value >= 1) {
          toolProficient = true;
          profBonus = toolsData[tKey].value * prof;
          break;
        }
      }

      // Verificação em itens de ferramentas na ficha
      if (!toolProficient) {
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

      // Suporte especial do Kibbles: Herbalismo para poções de cura e antídotos
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

    // Seleciona o melhor atributo entre os permitidos pela receita
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
   * Realiza uma rolagem de 2 horas de trabalho no projeto.
   * @param {Actor} actor
   * @param {object} recipe
   * @param {object} currentProgress { hours: number, consecutiveFailures: number }
   * @returns {Promise<object>} Resultado do teste
   */
  static async rollCraftingAttempt(actor, recipe, currentProgress = { hours: 0, consecutiveFailures: 0 }) {
    const { mod, bestAbility } = this.calculateCraftingModifier(actor, recipe);
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

    // Se completou com sucesso, entrega o item e consome materiais
    if (status === "completed") {
      await this.consumeMaterials(actor, recipe);
      await this.awardCraftedItem(actor, recipe);
    } else if (status === "failed") {
      // 3 falhas destroem os materiais
      await this.consumeMaterials(actor, recipe);
    }

    // Enviar mensagem rica no Chat
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
   * Executa a regra do Take 10 (sucesso garantido pelo dobro do tempo).
   * @param {Actor} actor
   * @param {object} recipe
   * @returns {Promise<boolean>}
   */
  static async take10Crafting(actor, recipe) {
    const { mod } = this.calculateCraftingModifier(actor, recipe);
    const take10Score = 10 + mod;

    if (take10Score < recipe.dc) {
      ui.notifications?.warn(`Seu bônus total (${mod}) + 10 = ${take10Score}, insuficiente para atingir a CD ${recipe.dc}.`);
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

    // Envia mensagem no chat
    const content = `
      <div class="itensdnd chat-card crafting-card">
        <header class="card-header flexrow">
          <img src="${recipe.img || 'icons/tools/smithing/anvil.webp'}" title="${recipe.name}" width="36" height="36"/>
          <h3>${recipe.name}</h3>
        </header>
        <div class="card-content">
          <p><strong>${game.i18n.localize("ITENSDND.Workshop.Recipe.Take10")}</strong></p>
          <p>O artesão <strong>${actor.name}</strong> trabalhou com calma e maestria por <strong>${totalHours} horas</strong>.</p>
          <p class="success-banner" style="color: #2e7d32; font-weight: bold;">
            <i class="fas fa-check-circle"></i> ${game.i18n.localize("ITENSDND.Workshop.Notifications.Take10Complete")}
          </p>
        </div>
      </div>
    `;

    await ChatMessage.create({
      user: game.user.id,
      speaker: ChatMessage.getSpeaker({ actor }),
      content,
      style: CONST.CHAT_MESSAGE_STYLES?.OTHER ?? CONST.CHAT_MESSAGE_TYPES?.OTHER
    });

    return true;
  }

  /**
   * Consome os materiais exigidos da ficha do personagem.
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
   * Cria o item resultante no inventário do personagem.
   * @param {Actor} actor
   * @param {object} recipe
   */
  static async awardCraftedItem(actor, recipe) {
    const itemData = {
      name: recipe.resultItem || recipe.name.replace(/^Receita: |^Recipe: /, ""),
      type: "consumable",
      img: recipe.img || "icons/commodities/treasure/chest-wooden.webp",
      system: {
        description: { value: `<p>Item criado na Oficina de Criação por ${actor.name}.</p>` },
        quantity: 1,
        rarity: recipe.rarity || "common"
      }
    };

    // Ajusta tipo de item com base na profissão
    if (recipe.profession === "blacksmithing") {
      itemData.type = recipe.name.toLowerCase().includes("armadura") || recipe.name.toLowerCase().includes("armor") || recipe.name.toLowerCase().includes("escudo") || recipe.name.toLowerCase().includes("shield") ? "equipment" : "weapon";
    }

    await actor.createEmbeddedDocuments("Item", [itemData]);
    ui.notifications?.info(`${game.i18n.localize("ITENSDND.Workshop.Notifications.CraftComplete")}: ${itemData.name}`);
  }

  /**
   * Envia a mensagem com os resultados da rolagem de criação no chat.
   */
  static async postCraftingChatMessage(actor, recipe, roll, isSuccess, newHours, newFailures, status, isTake10) {
    const successColor = isSuccess ? "#2e7d32" : "#c62828";
    const statusText = isSuccess
      ? `<span style="color: ${successColor}; font-weight: bold;"><i class="fas fa-check"></i> ${game.i18n.localize("ITENSDND.Workshop.Notifications.CraftSuccess")}</span>`
      : `<span style="color: ${successColor}; font-weight: bold;"><i class="fas fa-times"></i> ${game.i18n.localize("ITENSDND.Workshop.Notifications.CraftFailure")} (Falhas consecutivas: ${newFailures}/3)</span>`;

    let completionBanner = "";
    if (status === "completed") {
      completionBanner = `
        <div style="background: #e8f5e9; border: 1px solid #4caf50; padding: 6px; border-radius: 4px; margin-top: 6px; text-align: center; color: #1b5e20;">
          <strong>🎉 ${game.i18n.localize("ITENSDND.Chat.ItemCompleted")}: ${recipe.resultItem}</strong>
        </div>`;
    } else if (status === "failed") {
      completionBanner = `
        <div style="background: #ffebee; border: 1px solid #f44336; padding: 6px; border-radius: 4px; margin-top: 6px; text-align: center; color: #b71c1c;">
          <strong>💥 ${game.i18n.localize("ITENSDND.Workshop.Notifications.CraftDestroyed")}</strong>
        </div>`;
    }

    const rollHtml = await roll.render();

    const content = `
      <div class="itensdnd chat-card crafting-card">
        <header class="card-header flexrow" style="display: flex; align-items: center; gap: 8px; border-bottom: 1px solid #ccc; padding-bottom: 4px;">
          <img src="${recipe.img}" width="32" height="32" style="border: none; border-radius: 4px;"/>
          <div>
            <h3 style="margin: 0; font-size: 1.1em;">${recipe.name}</h3>
            <span style="font-size: 0.85em; color: #666;">CD ${recipe.dc} | Progresso: ${newHours}/${recipe.time} horas</span>
          </div>
        </header>
        <div class="card-content" style="margin-top: 6px;">
          <div>${statusText}</div>
          <div style="margin-top: 4px;">${rollHtml}</div>
          ${completionBanner}
        </div>
      </div>
    `;

    await ChatMessage.create({
      user: game.user.id,
      speaker: ChatMessage.getSpeaker({ actor }),
      content,
      type: CONST.CHAT_MESSAGE_TYPES?.ROLL ?? 5,
      rolls: [roll],
      sound: isSuccess ? CONFIG.sounds?.dice : null
    });
  }
}

