import { Router } from 'express';
import { verifyLineSignature } from '../line/signature.js';
import type { Store } from '../store/store.js';
import { logger } from '../util/logger.js';

type LineEvent = {
  type: string;
  source?: { groupId?: string };
};

export function createWebhookRouter(store: Store, channelSecret: string): Router {
  const router = Router();

  router.post('/line', (req, res) => {
    const signature = req.header('x-line-signature');
    const rawBody = (req as { rawBody?: string }).rawBody ?? '';

    if (!verifyLineSignature(rawBody, signature, channelSecret)) {
      res.status(401).json({ ok: false, error: 'invalid signature' });
      return;
    }

    const events = ((req.body?.events ?? []) as LineEvent[]);
    res.status(200).json({ ok: true });

    setImmediate(async () => {
      for (const event of events) {
        if (event.type !== 'join' && event.type !== 'message') continue;
        const groupId = event.source?.groupId;
        if (!groupId) continue;

        try {
          await store.upsertGroup(groupId);
          logger.info({ event: 'line.webhook.group_upserted', groupId });
        } catch (error) {
          logger.error({ event: 'line.webhook.group_upsert_failed', groupId, message: (error as Error).message });
        }
      }
    });
  });

  return router;
}
