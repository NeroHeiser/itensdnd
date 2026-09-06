/**
 * harvesting-engine.mjs
 * Motor de colheita de criaturas (Harvesting & Remnants) para itensdnd.
 * Baseado nas regras do Kibbles' Crafting Guide.
 */

const MODULE_ID = "itensdnd";

export class HarvestingEngine {
  /**
   * Mapeamento de tipo de criatura para perícia requerida
   */
  static SKILL_REQUIREMENTS = {
    dragon: { skill: "med", ability: "wis", label: "Medicina (Sabedoria)" },
    monstrosity: { skill: "med", ability: "wis", label: "Medicina (Sabedoria)" },
    giant: { skill: "med", ability: "wis", label: "Medicina (Sabedoria)" },
    construct: { skill: "arc", ability: "int", label: "Arcanismo (Inteligência)" },
    plant: { skill: "nat", ability: "int", label: "Natureza (Inteligência)" },
    beast: { skill: "sur", ability: "wis", label: "Sobrevivência (Sabedoria)" },
    aberration: { skill: "arc", ability: "int", label: "Arcanismo (Inteligência)" },
    undead: { skill: "arc", ability: "int", label: "Arcanismo (Inteligência)" },
    celestial: { remnants: true, label: "Resíduos Mágicos (Automático)" },
    fiend: { remnants: true, label: "Resíduos Mágicos (Automático)" },
    elemental: { remnants: true, label: "Resíduos Mágicos (Automático)" }
  };

  /**
   * Determina a tabela apropriada e a CD com base no ND da criatura.
   * @param {number} cr
   * @param {boolean} isRemnants
   * @returns {{ tableKey: string, dc: number }}
   */
  static getTableAndDC(cr = 1, isRemnants = false) {
    if (isRemnants) {
      return { tableKey: "harvesting-remnants-0-4", dc: 0 };
    }

    if (cr <= 4) {
      return { tableKey: "harvesting-cr-0-4", dc: 8 };
    } else if (cr <= 10) {
      return { tableKey: "harvesting-cr-5-10", dc: 10 };
    } else if (cr <= 16) {
      return { tableKey: "harvesting-cr-11-16", dc: 12 };
    } else {
      return { tableKey: "harvesting-cr-17-plus", dc: 14 };
    }
  }

  /**
   * Executa o processo de colheita entre o artesão (harvester) e o alvo (target).
   * @param {Actor} harvester
   * @param {Actor} target
   * @param {object} options
   */
  static async performHarvest(harvester, target, options = {}) {
    if (!harvester) {
      ui.notifications?.warn("Selecione um personagem colhedor.");
      return;
    }
    if (!target) {
      ui.notifications?.warn("Selecione um alvo para colheita.");
      return;
    }

    const cr = target.system?.details?.cr ?? 1;
    const typeStr = (target.system?.details?.type?.value || "monstrosity").toLowerCase();
    const typeInfo = this.SKILL_REQUIREMENTS[typeStr] || { skill: "sur", ability: "wis", label: "Sobrevivência" };

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

    // Consulta a RollTable
    const pack = game.packs.get(`${MODULE_ID}.crafting-tables`);
    let table = null;
    if (pack) {
      const index = await pack.getIndex();
      const entry = index.find(e => e.name.toLowerCase().includes(tableKey) || e.id.includes(tableKey));
      if (entry) table = await pack.getDocument(entry._id);
    }

    let resultText = "1x Reagente Comum";
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
      // Adicionar o material colhido ao inventário do colhedor
      await this.awardHarvestMaterial(harvester, drawnItemKey, drawnQty, resultText);
    }

    // Publicar mensagem no chat
    await this.postHarvestChatMessage(harvester, target, roll, dc, isSuccess, isRemnants, resultText, drawnQty);
  }

  /**
   * Adiciona o material obtido à ficha do colhedor.
   */
  static async awardHarvestMaterial(harvester, itemKey, qty, label) {
    // Tenta localizar no compêndio de materiais
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

    // Se o item já existe no ator, soma a quantidade
    const existing = harvester.items.find(i => i.flags?.itensdnd?.materialKey === itemKey);
    if (existing) {
      const cur = existing.system?.quantity || 1;
      await existing.update({ "system.quantity": cur + qty });
    } else {
      await harvester.createEmbeddedDocuments("Item", [itemData]);
    }

    ui.notifications?.info(`Colheita concluída! +${qty}x ${itemData.name}`);
  }

  /**
   * Publica o card de resultado no chat.
   */
  static async postHarvestChatMessage(harvester, target, roll, dc, isSuccess, isRemnants, resultText, qty) {
    let rollHtml = "";
    if (roll) {
      rollHtml = await roll.render();
    }

    const title = isRemnants
      ? `Coleta de Resíduos Mágicos: ${target.name}`
      : `Colheita de Criatura: ${target.name} (ND ${target.system?.details?.cr ?? 1})`;

    const statusBanner = isSuccess
      ? `<div style="color: #2e7d32; font-weight: bold; margin-top: 4px;"><i class="fas fa-check-circle"></i> Sucesso! Obtido: <strong>${resultText}</strong></div>`
      : `<div style="color: #c62828; font-weight: bold; margin-top: 4px;"><i class="fas fa-times-circle"></i> Falha no teste (CD ${dc}). Nenhum material íntegro pôde ser recuperado.</div>`;

    const content = `
      <div class="itensdnd chat-card harvest-card">
        <header class="card-header flexrow" style="display: flex; align-items: center; gap: 8px; border-bottom: 1px solid #ccc; padding-bottom: 4px;">
          <img src="${target.img || 'icons/svg/mystery-man.svg'}" width="32" height="32" style="border: none; border-radius: 4px;"/>
          <div>
            <h3 style="margin: 0; font-size: 1.1em;">${title}</h3>
            <span style="font-size: 0.85em; color: #666;">Colhedor: ${harvester.name}</span>
          </div>
        </header>
        <div class="card-content" style="margin-top: 6px;">
          ${rollHtml}
          ${statusBanner}
        </div>
      </div>
    `;

    await ChatMessage.create({
      user: game.user.id,
      speaker: ChatMessage.getSpeaker({ actor: harvester }),
      content,
      type: roll ? (CONST.CHAT_MESSAGE_TYPES?.ROLL ?? 5) : (CONST.CHAT_MESSAGE_TYPES?.OTHER ?? 0),
      rolls: roll ? [roll] : []
    });
  }
}

