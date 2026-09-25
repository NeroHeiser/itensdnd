import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.resolve(__dirname, "..");

test("all packs defined in module.json have existing physical directories on disk", () => {
  const manifestPath = path.join(rootDir, "module.json");
  const manifest = JSON.parse(fs.readFileSync(manifestPath, "utf-8"));

  assert.ok(Array.isArray(manifest.packs), "module.json must declare packs array");
  assert.ok(manifest.packs.length > 0, "module.json must declare at least one pack");

  for (const pack of manifest.packs) {
    const packDirPath = path.join(rootDir, pack.path);
    assert.ok(
      fs.existsSync(packDirPath),
      `Expected pack directory to exist on disk: ${pack.path}`
    );
    assert.ok(
      fs.statSync(packDirPath).isDirectory(),
      `Expected path to be a directory: ${pack.path}`
    );
  }
});

test("crafting-items pack is properly registered in module.json", () => {
  const manifestPath = path.join(rootDir, "module.json");
  const manifest = JSON.parse(fs.readFileSync(manifestPath, "utf-8"));
  const craftingItemsPack = manifest.packs.find(p => p.name === "crafting-items");

  assert.ok(craftingItemsPack, "crafting-items pack must be declared in module.json");
  assert.equal(craftingItemsPack.path, "packs/crafting-items");
  assert.equal(craftingItemsPack.type, "Item");
  assert.equal(craftingItemsPack.system, "dnd5e");
});
