import { Router } from 'express';
import type { Store } from '../store/store.js';

export function createSettingsRouter(store: Store): Router {
  const router = Router();

  router.get('/', async (_req, res) => {
    const settings = await store.getSettings();
    const groups = await store.listGroups();
    res.status(200).json({ settings, groups });
  });

  router.put('/', async (req, res) => {
    const { timezone, dailyTime, propertySource } = req.body ?? {};
    if (!timezone || !dailyTime || !['sheets', 'json'].includes(propertySource)) {
      res.status(400).json({ ok: false, error: 'invalid settings payload' });
      return;
    }

    const updated = await store.updateSettings({ timezone, dailyTime, propertySource });
    res.status(200).json({ ok: true, settings: updated });
  });

  return router;
}
