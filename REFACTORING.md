# Architecture & Refactoring Log: Quality, Testability & Application Audit

## 1. Overview
This log documents the architecture audit, test expansion, clean code alignment, internationalization, and application UX/state refactoring applied to the `itensdnd` module for Foundry VTT (v12-v14).

---

## 2. Completed Priorities & Architectural Decisions

### Phase 1: Codebase & Domain Logic Audit

#### Priority 1: Domain Logic Test Expansion & Guard Robustness
- **Objective:** Establish isolated unit tests for core crafting and harvesting rules without requiring browser DOM or active Foundry session.
- **Implemented:**
  - Added unit test suites [`tests/crafting-engine.test.mjs`](file:///run/media/lopes/Hd%20interno/Programa%C3%A7%C3%A3o/Foundry/itensdnd/tests/crafting-engine.test.mjs) and [`tests/harvesting-engine.test.mjs`](file:///run/media/lopes/Hd%20interno/Programa%C3%A7%C3%A3o/Foundry/itensdnd/tests/harvesting-engine.test.mjs).
  - Covered inventory quantity aggregation (`getMaterialCount`), recipe prerequisite verification (`checkMaterials`), crafting modifier calculation (`calculateCraftingModifier` tool mapping, herbalism fallback, ability maximization), CR-to-DC mapping (`getTableAndDC`), and creature type skill requirements.
  - Hardened `CraftingEngine.calculateCraftingModifier` against `TypeError` by adding nullish safety check when `actor.items` is undefined.
- **Commit:** `483319c` (`test(core): add unit tests for crafting and harvesting domain rules`).

#### Priority 2: Clean Code & English Standardization
- **Objective:** Enforce codebase rules (concise technical English, clean JSDocs, no trivial comments, zero emojis).
- **Implemented:**
  - Refactored [`scripts/main.mjs`](file:///run/media/lopes/Hd%20interno/Programa%C3%A7%C3%A3o/Foundry/itensdnd/scripts/main.mjs), [`scripts/crafting-engine.mjs`](file:///run/media/lopes/Hd%20interno/Programa%C3%A7%C3%A3o/Foundry/itensdnd/scripts/crafting-engine.mjs), [`scripts/harvesting-engine.mjs`](file:///run/media/lopes/Hd%20interno/Programa%C3%A7%C3%A3o/Foundry/itensdnd/scripts/harvesting-engine.mjs), [`scripts/compendium-sync.mjs`](file:///run/media/lopes/Hd%20interno/Programa%C3%A7%C3%A3o/Foundry/itensdnd/scripts/compendium-sync.mjs), [`scripts/apps/crafting-app.mjs`](file:///run/media/lopes/Hd%20interno/Programa%C3%A7%C3%A3o/Foundry/itensdnd/scripts/apps/crafting-app.mjs), and [`scripts/apps/harvesting-app.mjs`](file:///run/media/lopes/Hd%20interno/Programa%C3%A7%C3%A3o/Foundry/itensdnd/scripts/apps/harvesting-app.mjs).
  - Replaced emojis in chat status templates with standard FontAwesome icon elements.
  - Normalized console logging format across all modules (`itensdnd | <Message>`).
- **Commit:** `59926c9` (`refactor(scripts): standardize codebase to concise English without emojis`).

#### Priority 3: UI String Externalization & Bilingual Key Symmetry
- **Objective:** Eliminate hardcoded text in templates and scripts, ensuring complete localization coverage.
- **Implemented:**
  - Expanded [`lang/en.json`](file:///run/media/lopes/Hd%20interno/Programa%C3%A7%C3%A3o/Foundry/itensdnd/lang/en.json) and [`lang/pt-BR.json`](file:///run/media/lopes/Hd%20interno/Programa%C3%A7%C3%A3o/Foundry/itensdnd/lang/pt-BR.json) with symmetric keys covering workshop badges, modifiers, failure banners, harvesting details, and compendium sync notifications.
  - Updated [`templates/crafting-app.hbs`](file:///run/media/lopes/Hd%20interno/Programa%C3%A7%C3%A3o/Foundry/itensdnd/templates/crafting-app.hbs) and [`templates/harvesting-app.hbs`](file:///run/media/lopes/Hd%20interno/Programa%C3%A7%C3%A3o/Foundry/itensdnd/templates/harvesting-app.hbs) to use Handlebars `{{localize}}` exclusively.
  - Created [`tests/localization.test.mjs`](file:///run/media/lopes/Hd%20interno/Programa%C3%A7%C3%A3o/Foundry/itensdnd/tests/localization.test.mjs) enforcing valid JSON syntax and 100% key set symmetry between English and Brazilian Portuguese.
- **Commit:** `5a3268e` (`feat(i18n): externalize hardcoded UI strings and ensure bilingual key symmetry`).

---

### Phase 2: Application Layer Audit (ApplicationV2 & UX)

#### Priority 4 (App Priority 1): Fractional Challenge Rating Parsing & Target Deduplication
- **Objective:** Prevent low-CR creatures with fractional notation (`"1/4"`, `"1/2"`, `"1/8"`) from being assigned high-tier DCs due to string comparison failure, and deduplicate scene tokens.
- **Implemented:**
  - Added `HarvestingEngine.parseChallengeRating` supporting fractional numbers and strings.
  - Updated `getTableAndDC` and `performHarvest` to normalize challenge ratings before evaluating DC brackets.
  - Updated `HarvestingApp._prepareContext` to deduplicate scene actors and auto-select primary target safely.
- **Commit:** `14c3a25` (`fix(harvesting): add safe fractional CR parsing and deduplicate scene target actors`).

#### Priority 5 (App Priority 2): Actor Crafting Project State Persistence
- **Objective:** Prevent progress loss (hours and failures) when windows close or actors switch.
- **Implemented:**
  - Implemented `CraftingWorkshopApp.getActiveProject(actor)` and `CraftingWorkshopApp.setActiveProject(actor, project)` reading and writing to `actor.setFlag("itensdnd", "activeProject")`.
  - Added unit test suite [`tests/crafting-persistence.test.mjs`](file:///run/media/lopes/Hd%20interno/Programa%C3%A7%C3%A3o/Foundry/itensdnd/tests/crafting-persistence.test.mjs).
- **Commit:** `539216b` (`feat(crafting): persist active crafting project state to actor flags`).

#### Priority 6 (App Priority 3): Search Debounce & Action Button State Integrity
- **Objective:** Reduce DOM reflows during recipe searches and provide explicit button disablement states.
- **Implemented:**
  - Added configurable 150ms debounce (`searchDebounceMs`) to search input events in `CraftingWorkshopApp`.
  - Calculated `canTake10`, `canRoll`, and `canReset` flags in `_prepareContext` and bound `disabled` attributes in [`templates/crafting-app.hbs`](file:///run/media/lopes/Hd%20interno/Programa%C3%A7%C3%A3o/Foundry/itensdnd/templates/crafting-app.hbs).
  - Added `.btn-action:disabled` styling in [`styles/itensdnd.css`](file:///run/media/lopes/Hd%20interno/Programa%C3%A7%C3%A3o/Foundry/itensdnd/styles/itensdnd.css).
- **Commit:** `62e2111` (`feat(workshop): debounce search input and enforce action button states`).

---

## 3. Test Suite & Verification

Run the entire automated unit test suite natively via Node.js:

```bash
node --test tests/*.test.mjs
```

### Coverage Summary
- **Test files:** 7 (`chat-message`, `crafting-search`, `crafting-engine`, `crafting-persistence`, `harvesting-engine`, `icons`, `localization`, `packs-integrity`).
- **Total tests:** 32 passing, 0 failing.
- **Average duration:** ~1000ms.
- **Memory footprint:** Minimal (native test runner, no external runtime dependencies).
