import fs from "node:fs";
import { describe, expect, it } from "vitest";
import { extractAssistantTextFromHtml } from "../packages/adapters/src/index";

describe("adapter parser", () => {
  it("extracts assistant content from fixture", () => {
    const html = fs.readFileSync("tests/fixtures/chatgpt-snapshot.html", "utf8");
    const text = extractAssistantTextFromHtml(html);
    expect(text).toContain("<debate_turn>");
  });
});
