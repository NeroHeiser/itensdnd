import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.resolve(__dirname, "..");
const dataDir = path.join(rootDir, "scripts", "data");

const PACK_FILES = [
  "crafting-items.json",
  "crafting-materials.json",
  "crafting-recipes.json",
  "crafting-rules.json",
  "crafting-tables.json"
];

for (const lang of ["en", "pt-BR"]) {
  test(`data files for ${lang} are valid JSON and contain 16-character alphanumeric _id`, () => {
    const langDir = path.join(dataDir, lang);
    assert.ok(fs.existsSync(langDir), `Directory must exist: ${langDir}`);

    for (const fileName of PACK_FILES) {
      const filePath = path.join(langDir, fileName);
      assert.ok(fs.existsSync(filePath), `File must exist: ${filePath}`);

      const raw = fs.readFileSync(filePath, "utf-8");
      let data = null;
      assert.doesNotThrow(() => {
        data = JSON.parse(raw);
      }, `Failed to parse ${fileName} for ${lang}`);

      assert.ok(Array.isArray(data), `Expected ${fileName} to contain an array of documents`);
      assert.ok(data.length > 0, `Expected ${fileName} to not be empty`);

      for (const doc of data) {
        assert.ok(doc._id, `Document in ${fileName} must have _id`);
        assert.match(
          doc._id,
          /^[a-zA-Z0-9]{16}$/,
          `Document _id ${doc._id} in ${fileName} must be 16-char alphanumeric`
        );
        assert.ok(doc.name, `Document in ${fileName} must have a name`);
      }
    }
  });
}

test("recipe materials reference existing material keys in crafting-materials", () => {
  for (const lang of ["en", "pt-BR"]) {
    const materialsPath = path.join(dataDir, lang, "crafting-materials.json");
    const recipesPath = path.join(dataDir, lang, "crafting-recipes.json");

    const materials = JSON.parse(fs.readFileSync(materialsPath, "utf-8"));
    const recipes = JSON.parse(fs.readFileSync(recipesPath, "utf-8"));

    const materialKeys = new Set(materials.map(m => m.flags?.itensdnd?.materialKey).filter(Boolean));
    assert.ok(materialKeys.size > 50, `Expected at least 50 unique material keys in ${lang}`);

    for (const recipe of recipes) {
      const reqs = recipe.flags?.itensdnd?.materials || [];
      for (const req of reqs) {
        assert.ok(req.key, `Recipe requirement in "${recipe.name}" must declare key`);
      }
    }
  }
});
