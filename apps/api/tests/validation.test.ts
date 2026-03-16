import { describe, expect, it } from 'vitest';
import { validateGeneratedMessages } from '../src/util/validation.js';

describe('validateGeneratedMessages', () => {
  const properties = [
    {
      title: '物件A',
      price: '5000万円',
      area: '70㎡',
      stationMinutes: '徒歩8分',
      url: 'https://example.com/a',
    },
  ];

  it('passes valid payload', () => {
    const payload = {
      messages: [
        {
          type: 'text',
          text: '価格: 5000万円 面積: 70㎡ 徒歩8分 URL: https://example.com/a',
        },
      ],
    };

    expect(validateGeneratedMessages(payload, properties)).toHaveLength(1);
  });

  it('throws when URL is missing', () => {
    const payload = { messages: [{ type: 'text', text: '価格: 5000万円 面積: 70㎡ 徒歩8分' }] };
    expect(() => validateGeneratedMessages(payload, properties)).toThrowError();
  });
});
