import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';
import { logger } from '../util/logger.js';
import type { LineTextMessage } from '../util/validation.js';

export class LineClient {
  constructor(private readonly accessToken: string) {}

  async pushMessage(groupId: string, messages: LineTextMessage[]): Promise<void> {
    const retryKey = uuidv4();
    const maxAttempts = 3;

    for (let attempt = 1; attempt <= maxAttempts; attempt += 1) {
      try {
        const response = await axios.post(
          'https://api.line.me/v2/bot/message/push',
          { to: groupId, messages },
          {
            headers: {
              Authorization: `Bearer ${this.accessToken}`,
              'Content-Type': 'application/json',
              'X-Line-Retry-Key': retryKey,
            },
            timeout: 10000,
          },
        );

        logger.info({
          event: 'line.push.success',
          groupId,
          status: response.status,
          requestId: response.headers['x-line-request-id'],
          attempt,
          retryKey,
        });
        return;
      } catch (error) {
        const err = axios.isAxiosError(error) ? error : undefined;
        logger.error({
          event: 'line.push.error',
          groupId,
          status: err?.response?.status,
          requestId: err?.response?.headers?.['x-line-request-id'],
          attempt,
          retryKey,
          message: err?.message ?? 'Unknown line push error',
        });

        if (attempt === maxAttempts) {
          throw error;
        }
        await new Promise((resolve) => setTimeout(resolve, attempt * 500));
      }
    }
  }
}
