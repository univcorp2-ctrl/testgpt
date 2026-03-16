import { google } from 'googleapis';
import type { PropertyRecord, PropertySource } from './propertySource.js';

export class GoogleSheetsPropertySource implements PropertySource {
  constructor(
    private readonly spreadsheetId: string,
    private readonly range: string,
    private readonly clientEmail: string,
    private readonly privateKey: string,
  ) {}

  async fetchDailyProperties(_targetDate: string): Promise<PropertyRecord[]> {
    const auth = new google.auth.JWT({
      email: this.clientEmail,
      key: this.privateKey.replace(/\\n/g, '\n'),
      scopes: ['https://www.googleapis.com/auth/spreadsheets.readonly'],
    });

    const sheets = google.sheets({ version: 'v4', auth });
    const response = await sheets.spreadsheets.values.get({
      spreadsheetId: this.spreadsheetId,
      range: this.range,
    });

    const rows = response.data.values ?? [];
    return rows.slice(1).map((row) => ({
      title: row[0] ?? '',
      price: row[1] ?? '',
      area: row[2] ?? '',
      stationMinutes: row[3] ?? '',
      url: row[4] ?? '',
      notes: row[5] ?? '',
    }));
  }
}
