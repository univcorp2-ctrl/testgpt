import { describe, expect, it } from "vitest";
import { applyTurn, createInitialState, parseDebateTurn } from "../packages/debate-engine/src/index";

describe("debate engine", () => {
  it("parses schema and updates state", () => {
    const raw = `<debate_turn><round>1</round><speaker>chatgpt</speaker><role>synthesizer</role><position>x</position><new_claims><claim id="c1">A</claim></new_claims><attacks></attacks><defenses></defenses><open_questions><question>?</question></open_questions><question_to_next>n</question_to_next><delta_summary>s</delta_summary></debate_turn>[[END_TURN]]`;
    const turn = parseDebateTurn(raw);
    const next = applyTurn(createInitialState("t"), turn);
    expect(next.claimGraph.c1.claim).toBe("A");
    expect(next.currentRound).toBe(2);
  });
});
