import axios from 'axios';
import type { PropertyRecord } from '../content/propertySource.js';
import { logger } from '../util/logger.js';
import { type LineTextMessage, safeJsonParse, validateGeneratedMessages } from '../util/validation.js';

export class MessageGenerator {
  constructor(private readonly openAiApiKey?: string) {}

  async generate(properties: PropertyRecord[]): Promise<{ messages: LineTextMessage[]; fallbackUsed: boolean }> {
    if (!this.openAiApiKey) {
      return { messages: this.fallback(properties), fallbackUsed: true };
    }

    const prompt = {
      instruction:
        '不動産情報の導入文/締め文のみ変化させる。物件のprice, area, stationMinutes, urlは一切改変しない。JSONのみ返す。',
      properties,
      output: { messages: [{ type: 'text', text: '...' }] },
    };

    try {
      const res = await axios.post(
        'https://api.openai.com/v1/chat/completions',
        {
          model: process.env.OPENAI_MODEL ?? 'gpt-4o-mini',
          response_format: { type: 'json_object' },
          messages: [
            { role: 'system', content: 'You are a strict JSON formatter.' },
            { role: 'user', content: JSON.stringify(prompt) },
          ],
          temperature: 0.6,
        },
        {
          headers: {
            Authorization: `Bearer ${this.openAiApiKey}`,
            'Content-Type': 'application/json',
          },
          timeout: 12000,
        },
      );

      const content = res.data.choices?.[0]?.message?.content ?? '{}';
      const parsed = safeJsonParse(content);
      const messages = validateGeneratedMessages(parsed, properties);
      return { messages, fallbackUsed: false };
    } catch (error) {
      logger.error({ event: 'generate.ai.failed', message: (error as Error).message });
      return { messages: this.fallback(properties), fallbackUsed: true };
    }
  }

  private fallback(properties: PropertyRecord[]): LineTextMessage[] {
    const intro = '本日のおすすめ物件情報です。詳細は以下をご確認ください。';
    const lines = properties.map(
      (p, idx) =>
        `${idx + 1}. ${p.title}\n価格: ${p.price}\n面積: ${p.area}\n駅徒歩: ${p.stationMinutes}\nURL: ${p.url}`,
    );
    const outro = '気になる物件があればお気軽にご連絡ください。';

    return [{ type: 'text', text: [intro, ...lines, outro].join('\n\n') }];
  }
}
