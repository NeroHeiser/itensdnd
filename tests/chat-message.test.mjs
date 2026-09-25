import test from "node:test";
import assert from "node:assert/strict";
import { CraftingEngine } from "../scripts/crafting-engine.mjs";
import { HarvestingEngine } from "../scripts/harvesting-engine.mjs";

test("buildChatMessageData generates style property without type in Foundry V12+", () => {
  globalThis.CONST = {
    CHAT_MESSAGE_STYLES: {
      OTHER: 0,
      ROLL: 5
    }
  };

  const rollMsg = CraftingEngine.buildChatMessageData({
    user: "u123",
    speaker: { actor: "a1" },
    content: "test roll",
    rolls: [{ total: 15 }],
    isRoll: true
  });

  assert.equal(rollMsg.style, 5);
  assert.equal(rollMsg.type, undefined, "type property should not be present in V12+");
  assert.equal(rollMsg.user, "u123");

  const otherMsg = HarvestingEngine.buildChatMessageData({
    user: "u123",
    speaker: { actor: "a1" },
    content: "harvest text",
    isRoll: false
  });

  assert.equal(otherMsg.style, 0);
  assert.equal(otherMsg.type, undefined, "type property should not be present in V12+");
});

test("buildChatMessageData falls back to type property in legacy Foundry V11", () => {
  globalThis.CONST = {
    CHAT_MESSAGE_TYPES: {
      OTHER: 0,
      ROLL: 5
    }
  };

  const rollMsg = CraftingEngine.buildChatMessageData({
    user: "u123",
    speaker: { actor: "a1" },
    content: "test roll",
    rolls: [{ total: 15 }],
    isRoll: true
  });

  assert.equal(rollMsg.type, 5);
  assert.equal(rollMsg.style, undefined, "style property should not be present in V11 legacy");

  const otherMsg = HarvestingEngine.buildChatMessageData({
    user: "u123",
    speaker: { actor: "a1" },
    content: "harvest text",
    isRoll: false
  });

  assert.equal(otherMsg.type, 0);
  assert.equal(otherMsg.style, undefined, "style property should not be present in V11 legacy");
});
