import Database from "better-sqlite3";
import type { CanonicalState } from "@tri/shared";

export class DebateStore {
  db: Database.Database;

  constructor(path = "./data/debate.db") {
    this.db = new Database(path);
    this.db.pragma("journal_mode = WAL");
    this.migrate();
  }

  migrate() {
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS debate_state (
        debate_id TEXT PRIMARY KEY,
        payload TEXT NOT NULL,
        updated_at TEXT NOT NULL
      );
      CREATE TABLE IF NOT EXISTS debate_checkpoints (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        debate_id TEXT NOT NULL,
        step TEXT NOT NULL,
        payload TEXT NOT NULL,
        created_at TEXT NOT NULL
      );
    `);
  }

  saveState(state: CanonicalState) {
    const stmt = this.db.prepare(`
      INSERT INTO debate_state (debate_id, payload, updated_at)
      VALUES (@debateId, @payload, @updatedAt)
      ON CONFLICT(debate_id) DO UPDATE SET payload=@payload, updated_at=@updatedAt
    `);
    stmt.run({ debateId: state.debateId, payload: JSON.stringify(state), updatedAt: new Date().toISOString() });
  }

  loadState(debateId: string): CanonicalState | null {
    const row = this.db.prepare("SELECT payload FROM debate_state WHERE debate_id = ?").get(debateId) as { payload: string } | undefined;
    return row ? (JSON.parse(row.payload) as CanonicalState) : null;
  }

  addCheckpoint(debateId: string, step: string, payload: unknown) {
    this.db.prepare("INSERT INTO debate_checkpoints (debate_id, step, payload, created_at) VALUES (?, ?, ?, ?)")
      .run(debateId, step, JSON.stringify(payload), new Date().toISOString());
  }
}
