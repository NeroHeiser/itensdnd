import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.resolve(__dirname, "..");

function flattenKeys(obj, prefix = "") {
  let keys = [];
  for (const [k, v] of Object.entries(obj)) {
    const fullKey = prefix ? `${prefix}.${k}` : k;
    if (v && typeof v === "object" && !Array.isArray(v)) {
      keys = keys.concat(flattenKeys(v, fullKey));
    } else {
      keys.push(fullKey);
    }
  }
  return keys;
}

test("localization files exist, are valid JSON, and have symmetric keys", () => {
  const enPath = path.join(rootDir, "lang", "en.json");
  const ptPath = path.join(rootDir, "lang", "pt-BR.json");

  assert.ok(fs.existsSync(enPath), "lang/en.json must exist");
  assert.ok(fs.existsSync(ptPath), "lang/pt-BR.json must exist");

  const enData = JSON.parse(fs.readFileSync(enPath, "utf-8"));
  const ptData = JSON.parse(fs.readFileSync(ptPath, "utf-8"));

  const enKeys = flattenKeys(enData).sort();
  const ptKeys = flattenKeys(ptData).sort();

  assert.deepEqual(enKeys, ptKeys, "en.json and pt-BR.json must declare identical key sets");
  assert.ok(enKeys.length > 30, "localization keys must be populated");
});
