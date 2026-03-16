import fs from 'fs/promises';

export type PropertyRecord = {
  title: string;
  price: string;
  area: string;
  stationMinutes: string;
  url: string;
  notes?: string;
};

export interface PropertySource {
  fetchDailyProperties(targetDate: string): Promise<PropertyRecord[]>;
}

export class JsonPropertySource implements PropertySource {
  constructor(private readonly jsonPath: string) {}

  async fetchDailyProperties(_targetDate: string): Promise<PropertyRecord[]> {
    const raw = await fs.readFile(this.jsonPath, 'utf-8');
    const parsed = JSON.parse(raw) as PropertyRecord[];
    return parsed;
  }
}
