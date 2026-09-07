/**
 * compendium-sync.mjs
 * Gerenciador de Sincronização dos Compêndios do Módulo itensdnd.
 * Garante que os compêndios estejam sempre povoados com os documentos corretos
 * no Foundry VTT (v12/v14), com suporte a múltiplos idiomas (pt-BR / en).
 */

const MODULE_ID = "itensdnd";

export class CompendiumSync {
  static PACKS = [
    {
      id: "crafting-materials",
      file: "crafting-materials.json",
      documentName: "Item",
      label: "Materiais de Crafting"
    },
    {
      id: "crafting-recipes",
      file: "crafting-recipes.json",
      documentName: "Item",
      label: "Receitas de Crafting"
    },
    {
      id: "crafting-items",
      file: "crafting-items.json",
      documentName: "Item",
      label: "Itens Criáveis (Kibbles)"
    },
    {
      id: "crafting-tables",
      file: "crafting-tables.json",
      documentName: "RollTable",
      label: "Tabelas de Colheita e Coleta"
    },
    {
      id: "crafting-rules",
      file: "crafting-rules.json",
      documentName: "JournalEntry",
      label: "Regras de Crafting e Colheita"
    }
  ];

  /**
   * Verifica se algum pacote está vazio e realiza a sincronização necessária.
   */
  static async checkAndSyncAllPacks({ silent = true } = {}) {
    if (!game.user.isGM) return;
    let anyEmpty = false;

    for (const packInfo of this.PACKS) {
      const pack = game.packs.get(`${MODULE_ID}.${packInfo.id}`);
      if (pack) {
        const idx = await pack.getIndex();
        if (idx.size === 0) {
          anyEmpty = true;
          break;
        }
      }
    }

    let autoSync = true;
    try {
      autoSync = game.settings.get(MODULE_ID, "autoSyncCompendiums");
    } catch (e) {}

    if (anyEmpty || autoSync) {
      await this.syncAllPacks({ force: anyEmpty, silent: silent && !anyEmpty });
    }
  }

  /**
   * Sincroniza todos os pacotes do módulo se estiverem vazios, com IDs inválidos ou se for forçado.
   * @param {object} options
   * @param {boolean} [options.force=false] Força a sobrescrita dos itens
   * @param {boolean} [options.silent=false] Não emite notificações na tela
   */
  static async syncAllPacks({ force = false, silent = false } = {}) {
    if (!game.user.isGM) return;

    // Detecta o idioma da mesa: se começar com "pt", usa os dados em português (pt-BR), caso contrário inglês (en)
    const isPt = game.i18n?.lang?.startsWith("pt");
    const langFolder = isPt ? "pt-BR" : "en";
    let storedLang = "";
    try {
      storedLang = game.settings.get(MODULE_ID, "syncedLanguage") || "";
    } catch (e) {
      storedLang = "";
    }
    const langChanged = storedLang !== langFolder;

    let syncedCount = 0;
    const baseRoute = typeof foundry !== "undefined" && foundry.utils?.getRoute ? foundry.utils.getRoute(`modules/${MODULE_ID}`) : `/modules/${MODULE_ID}`;

    for (const packInfo of this.PACKS) {
      const packKey = `${MODULE_ID}.${packInfo.id}`;
      const pack = game.packs.get(packKey);

      if (!pack) {
        console.warn(`itensdnd | Pacote de compêndio não encontrado: ${packKey}`);
        continue;
      }

      // Se o compêndio estiver bloqueado, desbloqueia temporariamente para gravação
      const wasLocked = pack.locked;
      if (wasLocked) {
        try { await pack.configure({ locked: false }); } catch (e) { pack.locked = false; }
      }

      try {
        const index = await pack.getIndex();
        const hasInvalidIds = index.some(e => !/^[a-zA-Z0-9]{16}$/.test(e._id));

        // Carrega o arquivo JSON do idioma ativo com rota absoluta segura
        const dataUrl = `${baseRoute}/scripts/data/${langFolder}/${packInfo.file}`;
        let response = await fetch(dataUrl).catch(() => null);

        // Fallback sem rota caso a rota padrão não responda
        if (!response || !response.ok) {
          response = await fetch(`modules/${MODULE_ID}/scripts/data/${langFolder}/${packInfo.file}`).catch(() => null);
        }

        if (!response || !response.ok) {
          console.error(`itensdnd | Falha ao carregar arquivo de dados: ${dataUrl}`);
          continue;
        }

        const documentsData = await response.json();
        const shouldSync = index.size === 0 || force || langChanged || hasInvalidIds || (index.size !== documentsData.length);

        if (shouldSync) {
          console.log(`itensdnd | Sincronizando compêndio ${packKey} com ${documentsData.length} registros (${langFolder})...`);

          // Limpa documentos antigos em lotes
          if (index.size > 0) {
            const existingIds = Array.from(index.map(e => e.id || e._id));
            for (let i = 0; i < existingIds.length; i += 100) {
              await pack.documentClass.deleteDocuments(existingIds.slice(i, i + 100), { pack: packKey });
            }
          }

          // Cria os novos documentos no pacote em lotes seguros para evitar limite de socket
          const batchSize = 100;
          for (let i = 0; i < documentsData.length; i += batchSize) {
            const batch = documentsData.slice(i, i + batchSize);
            await pack.documentClass.createDocuments(batch, { pack: packKey, keepId: true });
          }

          syncedCount++;
        }
      } catch (err) {
        console.error(`itensdnd | Erro durante sincronização de ${packKey}:`, err);
      } finally {
        if (wasLocked) {
          try { await pack.configure({ locked: true }); } catch (e) { pack.locked = true; }
        }
      }
    }

    if (syncedCount > 0) {
      try {
        await game.settings.set(MODULE_ID, "syncedLanguage", langFolder);
      } catch (e) {}

      if (!silent) {
        ui.notifications?.info(`Compêndios do sistema de Crafting sincronizados com sucesso (${langFolder})!`);
      }
    }
  }
}

