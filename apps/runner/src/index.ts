import fs from "node:fs";
import path from "node:path";
import pino from "pino";
import { PlaywrightAdapter } from "@tri/adapters";
import { applyTurn, buildPrompt, createInitialState, nextSpeaker, parseDebateTurn } from "@tri/debate-engine";
import { DebateStore } from "@tri/store";
import type { Provider } from "@tri/shared";

const logger = pino({ level: "info" });
const store = new DebateStore();
const configPath = process.env.CONFIG_PATH ?? "./config.local.json";

type ProviderConfig = { workspaceUrl: string; profileDir: string };
type AppConfig = { theme: string; turns: number; providers: Record<Provider, ProviderConfig> };

function loadConfig(): AppConfig {
  return JSON.parse(fs.readFileSync(configPath, "utf8")) as AppConfig;
}

async function run() {
  const cfg = loadConfig();
  fs.mkdirSync("./artifacts", { recursive: true });
  let state = store.loadState("main") ?? { ...createInitialState(cfg.theme), debateId: "main", status: "running" as const };
  const adapters = new Map<Provider, PlaywrightAdapter>();

  for (const provider of state.participants) {
    const c = cfg.providers[provider];
    const adapter = new PlaywrightAdapter(provider, c.workspaceUrl, c.profileDir);
    await adapter.init();
    adapters.set(provider, adapter);
  }

  while (state.transcript.length < cfg.turns && state.status === "running") {
    const speaker = nextSpeaker(state);
    const adapter = adapters.get(speaker)!;
    store.addCheckpoint(state.debateId, "pick_next_speaker", { speaker });

    await adapter.openWorkspace();
    const blocked = await adapter.detectBlockedState();
    if (blocked !== "ok") {
      state.status = "manual_takeover_required";
      store.addCheckpoint(state.debateId, "blocked", { blocked, speaker });
      break;
    }

    const prompt = buildPrompt(state, speaker);
    store.addCheckpoint(state.debateId, "compose_prompt", { speaker, prompt });

    await adapter.sendPrompt(prompt);
    await adapter.waitForCompletion();
    const raw = await adapter.readLastAssistantMessage();
    const screenshot = path.join("artifacts", `${Date.now()}-${speaker}.png`);
    await adapter.takeScreenshot(screenshot);

    try {
      const turn = parseDebateTurn(raw);
      state = applyTurn(state, turn);
      store.addCheckpoint(state.debateId, "turn_applied", { round: state.currentRound, speaker, screenshot });
    } catch {
      // one-time repair
      await adapter.sendPrompt("Return only valid debate_turn schema. No extra text.");
      await adapter.waitForCompletion();
      const repairRaw = await adapter.readLastAssistantMessage();
      const repaired = parseDebateTurn(repairRaw);
      state = applyTurn(state, repaired);
      store.addCheckpoint(state.debateId, "repair_applied", { speaker });
    }

    if (state.transcript.length % 12 === 0) {
      store.addCheckpoint(state.debateId, "thread_compaction", { summary: state.rollingSummary, speaker });
    }

    store.saveState(state);
    logger.info({ round: state.currentRound, unresolved: state.unresolvedClaims.length }, "turn complete");
  }

  store.saveState(state);
}

run().catch((err) => {
  logger.error(err);
  process.exit(1);
});
