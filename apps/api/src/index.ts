import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';
import { Firestore } from '@google-cloud/firestore';
import { JsonPropertySource } from './content/propertySource.js';
import { GoogleSheetsPropertySource } from './content/googleSheetsSource.js';
import { MessageGenerator } from './generate/messageGenerator.js';
import { LineClient } from './line/client.js';
import { createJobsRouter } from './routes/jobs.js';
import { createSettingsRouter } from './routes/settings.js';
import { createWebhookRouter } from './routes/webhook.js';
import { createStore } from './store/store.js';
import { logger } from './util/logger.js';

const app = express();
app.use(
  express.json({
    verify: (req, _res, buf) => {
      (req as { rawBody?: string }).rawBody = buf.toString('utf-8');
    },
  }),
);

const useFirestore = process.env.USE_FIRESTORE === 'true';
const firestore = useFirestore ? new Firestore() : undefined;
const store = createStore(firestore);

const propertySource = process.env.PROPERTY_SOURCE === 'sheets'
  ? new GoogleSheetsPropertySource(
      process.env.GOOGLE_SHEETS_SPREADSHEET_ID ?? '',
      process.env.GOOGLE_SHEETS_RANGE ?? 'properties!A:F',
      process.env.GOOGLE_SERVICE_ACCOUNT_EMAIL ?? '',
      process.env.GOOGLE_SERVICE_ACCOUNT_PRIVATE_KEY ?? '',
    )
  : new JsonPropertySource(process.env.PROPERTY_JSON_PATH ?? './data/properties.json');

const lineClient = new LineClient(process.env.LINE_CHANNEL_ACCESS_TOKEN ?? '');
const generator = new MessageGenerator(process.env.OPENAI_API_KEY);

app.use('/webhook', createWebhookRouter(store, process.env.LINE_CHANNEL_SECRET ?? ''));
app.use('/jobs', createJobsRouter(store, propertySource, generator, lineClient));
app.use('/api/settings', createSettingsRouter(store));

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
app.use('/ui', express.static(path.resolve(__dirname, '../public')));

app.get('/healthz', (_req, res) => res.status(200).json({ ok: true }));

const port = Number(process.env.PORT ?? 8080);
app.listen(port, () => {
  logger.info({ event: 'server.started', port });
});
