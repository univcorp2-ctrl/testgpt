import crypto from 'crypto';

export function verifyLineSignature(body: string, signature: string | undefined, channelSecret: string): boolean {
  if (!signature) return false;

  const digest = crypto
    .createHmac('sha256', channelSecret)
    .update(body)
    .digest('base64');

  const provided = Buffer.from(signature);
  const expected = Buffer.from(digest);

  if (provided.length !== expected.length) return false;
  return crypto.timingSafeEqual(provided, expected);
}
