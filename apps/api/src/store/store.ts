import type { Firestore } from '@google-cloud/firestore';
import { FirestoreStore } from './firestoreStore.js';

export type GroupConfig = {
  groupId: string;
  lastSentDate?: string;
  updatedAt: string;
};

export type SendHistory = {
  groupId: string;
  date: string;
  sentAt: string;
  messageCount: number;
  fallbackUsed: boolean;
};

export type ServiceSettings = {
  timezone: string;
  dailyTime: string;
  propertySource: 'sheets' | 'json';
  updatedAt: string;
};

export interface Store {
  upsertGroup(groupId: string): Promise<void>;
  listGroups(): Promise<GroupConfig[]>;
  markDailySent(groupId: string, date: string): Promise<void>;
  isDailySent(groupId: string, date: string): Promise<boolean>;
  appendHistory(history: SendHistory): Promise<void>;
  getSettings(): Promise<ServiceSettings>;
  updateSettings(settings: Pick<ServiceSettings, 'timezone' | 'dailyTime' | 'propertySource'>): Promise<ServiceSettings>;
}

class InMemoryStore implements Store {
  private groups = new Map<string, GroupConfig>();
  private history: SendHistory[] = [];
  private settings: ServiceSettings = {
    timezone: 'Asia/Tokyo',
    dailyTime: '09:00',
    propertySource: 'sheets',
    updatedAt: new Date().toISOString(),
  };

  async upsertGroup(groupId: string): Promise<void> {
    this.groups.set(groupId, { groupId, updatedAt: new Date().toISOString(), lastSentDate: this.groups.get(groupId)?.lastSentDate });
  }

  async listGroups(): Promise<GroupConfig[]> {
    return [...this.groups.values()];
  }

  async markDailySent(groupId: string, date: string): Promise<void> {
    this.groups.set(groupId, { groupId, updatedAt: new Date().toISOString(), lastSentDate: date });
  }

  async isDailySent(groupId: string, date: string): Promise<boolean> {
    return this.groups.get(groupId)?.lastSentDate === date;
  }

  async appendHistory(history: SendHistory): Promise<void> {
    this.history.push(history);
  }

  async getSettings(): Promise<ServiceSettings> {
    return this.settings;
  }

  async updateSettings(settings: Pick<ServiceSettings, 'timezone' | 'dailyTime' | 'propertySource'>): Promise<ServiceSettings> {
    this.settings = {
      ...this.settings,
      ...settings,
      updatedAt: new Date().toISOString(),
    };
    return this.settings;
  }
}

export function createStore(firestore?: Firestore): Store {
  if (firestore) return new FirestoreStore(firestore);
  return new InMemoryStore();
}
