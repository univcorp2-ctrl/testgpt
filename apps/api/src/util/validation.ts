import { z } from 'zod';
import type { PropertyRecord } from '../content/propertySource.js';

export const LINE_MAX_MESSAGES = 5;
export const LINE_MAX_TEXT_LENGTH = 5000;

const messageSchema = z.object({
  type: z.literal('text'),
  text: z.string().min(1).max(LINE_MAX_TEXT_LENGTH),
});

const generatedSchema = z.object({
  messages: z.array(messageSchema).min(1).max(LINE_MAX_MESSAGES),
});

export type LineTextMessage = z.infer<typeof messageSchema>;

const urlRegex = /^https?:\/\//;
const numberRegex = /\d+[\d,.]*/g;

export function validateGeneratedMessages(
  payload: unknown,
  properties: PropertyRecord[],
): LineTextMessage[] {
  const parsed = generatedSchema.parse(payload);
  const joined = parsed.messages.map((m) => m.text).join('\n');

  for (const property of properties) {
    if (!joined.includes(property.url) || !urlRegex.test(property.url)) {
      throw new Error(`Generated messages missing property URL: ${property.url}`);
    }

    const sourceNumbers = `${property.price} ${property.area} ${property.stationMinutes}`.match(numberRegex) ?? [];
    for (const num of sourceNumbers) {
      if (!joined.includes(num)) {
        throw new Error(`Generated messages missing source numeric value: ${num}`);
      }
    }
  }

  return parsed.messages;
}

export function safeJsonParse(value: string): unknown {
  try {
    return JSON.parse(value);
  } catch {
    return null;
  }
}
