import { describe, expect, it } from 'vitest';
import { createStore } from '../src/store/store.js';

describe('settings in store', () => {
  it('returns default settings and updates settings', async () => {
    const store = createStore();
    const before = await store.getSettings();
    expect(before.timezone).toBe('Asia/Tokyo');

    const updated = await store.updateSettings({
      timezone: 'Asia/Tokyo',
      dailyTime: '08:30',
      propertySource: 'json',
    });

    expect(updated.dailyTime).toBe('08:30');
    expect(updated.propertySource).toBe('json');
  });
});
