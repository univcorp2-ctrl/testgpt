import { Router } from 'express';
import type { PropertySource } from '../content/propertySource.js';
import { MessageGenerator } from '../generate/messageGenerator.js';
import { LineClient } from '../line/client.js';
import type { Store } from '../store/store.js';
import { logger } from '../util/logger.js';

function currentDateInTimezone(timezone: string): string {
  return new Intl.DateTimeFormat('en-CA', {
    timeZone: timezone,
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  }).format(new Date());
}

export function createJobsRouter(
  store: Store,
  propertySource: PropertySource,
  generator: MessageGenerator,
  lineClient: LineClient,
): Router {
  const router = Router();

  router.post('/daily', async (_req, res) => {
    const settings = await store.getSettings();
    const targetDate = currentDateInTimezone(settings.timezone);
    const groups = await store.listGroups();
    const properties = await propertySource.fetchDailyProperties(targetDate);

    for (const group of groups) {
      if (await store.isDailySent(group.groupId, targetDate)) {
        logger.info({ event: 'jobs.daily.skip_already_sent', groupId: group.groupId, targetDate });
        continue;
      }

      const { messages, fallbackUsed } = await generator.generate(properties);
      await lineClient.pushMessage(group.groupId, messages);
      await store.markDailySent(group.groupId, targetDate);
      await store.appendHistory({
        groupId: group.groupId,
        date: targetDate,
        sentAt: new Date().toISOString(),
        messageCount: messages.length,
        fallbackUsed,
      });
    }

    res.status(200).json({ ok: true, targetDate, groups: groups.length, timezone: settings.timezone });
  });

  return router;
}
