import type { BlockedState, Provider } from "@tri/shared";
import { chromium, type BrowserContext, type Page } from "playwright";

export type SelectorStrategy = {
  input: string[];
  sendButton: string[];
  assistantMessage: string[];
  completionMarker: string[];
};

export interface SiteAdapter {
  openWorkspace(): Promise<void>;
  sendPrompt(prompt: string): Promise<void>;
  waitForCompletion(): Promise<void>;
  readLastAssistantMessage(): Promise<string>;
  detectBlockedState(): Promise<BlockedState>;
  takeScreenshot(filePath: string): Promise<void>;
  exportThreadUrl(): Promise<string>;
}

export const selectorConfig: Record<Provider, SelectorStrategy> = {
  chatgpt: {
    input: ["textarea[placeholder*='Message']", "textarea"],
    sendButton: ["button[aria-label*='Send']", "button:has-text('Send')"],
    assistantMessage: ["[data-message-author-role='assistant']", "article"],
    completionMarker: ["button:has-text('Stop')"]
  },
  claude: {
    input: ["textarea[placeholder*='Talk to Claude']", "textarea"],
    sendButton: ["button:has-text('Send')", "button[aria-label*='Send']"],
    assistantMessage: ["[data-testid='assistant-message']", "article"],
    completionMarker: ["button:has-text('Stop')"]
  },
  gemini: {
    input: ["rich-textarea textarea", "textarea"],
    sendButton: ["button[aria-label*='Send message']", "button:has-text('Send')"],
    assistantMessage: ["message-content", "article"],
    completionMarker: ["button:has-text('Stop response')"]
  }
};

export class PlaywrightAdapter implements SiteAdapter {
  private context!: BrowserContext;
  private page!: Page;
  constructor(private provider: Provider, private workspaceUrl: string, private profileDir: string) {}

  async init() {
    this.context = await chromium.launchPersistentContext(this.profileDir, { headless: false });
    this.page = await this.context.newPage();
  }

  private async firstVisible(selectors: string[]) {
    for (const selector of selectors) {
      const loc = this.page.locator(selector).first();
      if (await loc.isVisible().catch(() => false)) return loc;
    }
    throw new Error("ui_changed");
  }

  async openWorkspace() { await this.page.goto(this.workspaceUrl); }
  async sendPrompt(prompt: string) {
    const s = selectorConfig[this.provider];
    const input = await this.firstVisible(s.input);
    await input.fill(prompt);
    const send = await this.firstVisible(s.sendButton);
    await send.click();
  }
  async waitForCompletion() { await this.page.waitForTimeout(2500); }
  async readLastAssistantMessage() {
    const s = selectorConfig[this.provider];
    const text = await this.page.locator(s.assistantMessage.join(",")).last().innerText();
    return text;
  }
  async detectBlockedState(): Promise<BlockedState> {
    const url = this.page.url();
    if (url.includes("login")) return "login_required";
    return "ok";
  }
  async takeScreenshot(filePath: string) { await this.page.screenshot({ path: filePath, fullPage: true }); }
  async exportThreadUrl() { return this.page.url(); }
}

export function extractAssistantTextFromHtml(html: string): string {
  const match = html.match(/data-assistant-message="([\s\S]*?)"/);
  return match ? match[1] : "";
}
