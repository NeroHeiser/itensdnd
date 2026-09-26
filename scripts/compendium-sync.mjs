const MODULE_ID = "itensdnd";

export class CompendiumSync {
  static PACKS = [
    {
      id: "crafting-materials",
      file: "crafting-materials.json",
      documentName: "Item",
      label: "Crafting Materials"
    },
    {
      id: "crafting-recipes",
      file: "crafting-recipes.json",
      documentName: "Item",
      label: "Crafting Recipes"
    },
    {
      id: "crafting-items",
      file: "crafting-items.json",
      documentName: "Item",
      label: "Craftable Items (Kibbles)"
    },
    {
      id: "crafting-tables",
      file: "crafting-tables.json",
      documentName: "RollTable",
      label: "Harvesting & Gathering Tables"
    },
    {
      id: "crafting-rules",
      file: "crafting-rules.json",
      documentName: "JournalEntry",
      label: "Crafting & Harvesting Rules"
    }
  ];

  /**
   * Inspects all module compendiums and triggers synchronization if any pack is empty.
   * @param {object} options
   * @param {boolean} [options.silent=true]
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
   * Synchronizes all module packs if empty, requested via force, or language changed.
   * @param {object} options
   * @param {boolean} [options.force=false]
   * @param {boolean} [options.silent=false]
   */
  static async syncAllPacks({ force = false, silent = false } = {}) {
    if (!game.user.isGM) return;

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
        console.warn(`itensdnd | Compendium pack not found: ${packKey}`);
        continue;
      }

      const wasLocked = pack.locked;
      if (wasLocked) {
        try { await pack.configure({ locked: false }); } catch (e) { pack.locked = false; }
      }

      try {
        const index = await pack.getIndex();
        const hasInvalidIds = index.some(e => !/^[a-zA-Z0-9]{16}$/.test(e._id));

        const dataUrl = `${baseRoute}/scripts/data/${langFolder}/${packInfo.file}`;
        let response = await fetch(dataUrl).catch(() => null);

        if (!response || !response.ok) {
          response = await fetch(`modules/${MODULE_ID}/scripts/data/${langFolder}/${packInfo.file}`).catch(() => null);
        }

        if (!response || !response.ok) {
          console.error(`itensdnd | Failed to load data file: ${dataUrl}`);
          continue;
        }

        const documentsData = await response.json();
        const shouldSync = index.size === 0 || force || langChanged || hasInvalidIds || (index.size !== documentsData.length);

        if (shouldSync) {
          console.log(`itensdnd | Synchronizing pack ${packKey} with ${documentsData.length} records (${langFolder})...`);

          if (index.size > 0) {
            const existingIds = Array.from(index.map(e => e.id || e._id));
            for (let i = 0; i < existingIds.length; i += 100) {
              await pack.documentClass.deleteDocuments(existingIds.slice(i, i + 100), { pack: packKey });
            }
          }

          const batchSize = 100;
          for (let i = 0; i < documentsData.length; i += batchSize) {
            const batch = documentsData.slice(i, i + batchSize);
            await pack.documentClass.createDocuments(batch, { pack: packKey, keepId: true });
          }

          syncedCount++;
        }
      } catch (err) {
        console.error(`itensdnd | Error while synchronizing ${packKey}:`, err);
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
        ui.notifications?.info(
          game.i18n.format?.("ITENSDND.Compendium.SyncSuccess", { lang: langFolder }) ||
          `Crafting compendiums synchronized successfully (${langFolder})!`
        );
      }
    }
  }
}
