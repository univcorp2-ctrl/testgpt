import { z } from "zod";

export const ProviderSchema = z.enum(["chatgpt", "claude", "gemini"]);
export type Provider = z.infer<typeof ProviderSchema>;

export const BlockedStateSchema = z.enum([
  "ok",
  "login_required",
  "captcha",
  "rate_limited",
  "ui_changed"
]);
export type BlockedState = z.infer<typeof BlockedStateSchema>;

export const DebateTurnSchema = z.object({
  round: z.number().int().nonnegative(),
  speaker: ProviderSchema,
  role: z.enum(["synthesizer", "critic", "explorer"]),
  position: z.string().min(1),
  newClaims: z.array(z.object({ id: z.string(), text: z.string() })),
  attacks: z.array(z.object({ target: z.string(), text: z.string() })),
  defenses: z.array(z.object({ target: z.string(), text: z.string() })),
  openQuestions: z.array(z.string()),
  questionToNext: z.string(),
  deltaSummary: z.string()
});

export type DebateTurn = z.infer<typeof DebateTurnSchema>;

export type CanonicalState = {
  debateId: string;
  theme: string;
  participants: Provider[];
  currentRound: number;
  rollingSummary: string;
  unresolvedClaims: string[];
  claimGraph: Record<string, { claim: string; status: "open" | "challenged" | "defended" }>;
  lastValidTurnPerProvider: Partial<Record<Provider, number>>;
  checkpoints: string[];
  transcript: DebateTurn[];
  status: "idle" | "running" | "paused" | "manual_takeover_required" | "completed";
};

export const DEFAULT_ROLE_MAP: Record<Provider, DebateTurn["role"]> = {
  chatgpt: "synthesizer",
  claude: "critic",
  gemini: "explorer"
};

export const DEBATE_SCHEMA_INSTRUCTION = `Every response MUST match:\n<debate_turn>...[[END_TURN]]`;
