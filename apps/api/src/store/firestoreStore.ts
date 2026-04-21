import type { Firestore } from '@google-cloud/firestore';
import type { GroupConfig, SendHistory, ServiceSettings, Store } from './store.js';

const settingsDocId = 'default';

export class FirestoreStore implements Store {
  constructor(private readonly firestore: Firestore) {}

  async upsertGroup(groupId: string): Promise<void> {
    await this.firestore.collection('lineGroups').doc(groupId).set(
      {
        groupId,
        updatedAt: new Date().toISOString(),
      },
      { merge: true },
    );
  }

  async listGroups(): Promise<GroupConfig[]> {
    const snap = await this.firestore.collection('lineGroups').get();
    return snap.docs.map((doc) => doc.data() as GroupConfig);
  }

  async markDailySent(groupId: string, date: string): Promise<void> {
    await this.firestore.collection('lineGroups').doc(groupId).set(
      {
        lastSentDate: date,
        updatedAt: new Date().toISOString(),
      },
      { merge: true },
    );
  }

  async isDailySent(groupId: string, date: string): Promise<boolean> {
    const doc = await this.firestore.collection('lineGroups').doc(groupId).get();
    return doc.exists && doc.data()?.lastSentDate === date;
  }

  async appendHistory(history: SendHistory): Promise<void> {
    await this.firestore.collection('lineSendHistory').add(history);
  }

  async getSettings(): Promise<ServiceSettings> {
    const doc = await this.firestore.collection('serviceSettings').doc(settingsDocId).get();
    if (!doc.exists) {
      return {
        timezone: 'Asia/Tokyo',
        dailyTime: '09:00',
        propertySource: 'sheets',
        updatedAt: new Date().toISOString(),
      };
    }

    return doc.data() as ServiceSettings;
  }

  async updateSettings(settings: Pick<ServiceSettings, 'timezone' | 'dailyTime' | 'propertySource'>): Promise<ServiceSettings> {
    const payload: ServiceSettings = {
      ...settings,
      updatedAt: new Date().toISOString(),
    };

    await this.firestore.collection('serviceSettings').doc(settingsDocId).set(payload, { merge: true });
    return payload;
  }
}
