import crypto from 'crypto';
import { describe, expect, it } from 'vitest';
import { verifyLineSignature } from '../src/line/signature.js';

describe('verifyLineSignature', () => {
  it('returns true when signature is valid', () => {
    const body = JSON.stringify({ hello: 'world' });
    const secret = 'test_secret';
    const signature = crypto.createHmac('sha256', secret).update(body).digest('base64');

    expect(verifyLineSignature(body, signature, secret)).toBe(true);
  });

  it('returns false when signature is invalid', () => {
    expect(verifyLineSignature('{}', 'bad', 'secret')).toBe(false);
  });
});
