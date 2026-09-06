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

    for (const packInfo of this.PACKS) {
      const packKey = `${MODULE_ID}.${packInfo.id}`;
      const pack = game.packs.get(packKey);

      if (!pack) {
        console.warn(`itensdnd | Pacote de compêndio não encontrado: ${packKey}`);
        continue;
      }

      // Se o compêndio estiver bloqueado, desbloqueia temporariamente para gravação
      const wasLocked = pack.locked;
      if (wasLocked) await pack.configure({ locked: false });

      try {
        const index = await pack.getIndex();
        const hasInvalidIds = index.some(e => !/^[a-zA-Z0-9]{16}$/.test(e._id));

        // Carrega o arquivo JSON do idioma ativo (pt-BR ou en)
        const dataUrl = `modules/${MODULE_ID}/scripts/data/${langFolder}/${packInfo.file}`;
        const response = await fetch(dataUrl);
        if (!response.ok) {
          console.error(`itensdnd | Falha ao carregar arquivo de dados: ${dataUrl}`);
          continue;
        }

        const documentsData = await response.json();
        const shouldSync = index.size === 0 || force || langChanged || hasInvalidIds || (index.size !== documentsData.length);

        if (shouldSync) {
          console.log(`itensdnd | Sincronizando compêndio ${packKey} com ${documentsData.length} registros (${langFolder})...`);

          // Limpa documentos antigos se estiver forçando ou mudando de idioma
          if (index.size > 0) {
            const existingIds = Array.from(index.map(e => e._id));
            await pack.documentClass.deleteDocuments(existingIds, { pack: packKey });
          }

          // Cria os novos documentos no pacote
          await pack.documentClass.createDocuments(documentsData, { pack: packKey, keepId: true });
          syncedCount++;
        }
      } catch (err) {
        console.error(`itensdnd | Erro durante sincronização de ${packKey}:`, err);
      } finally {
        if (wasLocked) await pack.configure({ locked: true });
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
