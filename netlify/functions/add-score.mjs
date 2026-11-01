// POST /.netlify/functions/add-score  {board, day, name, score}
import { sql, json, cleanName, preflight } from "./_db.mjs";

export default async (req) => {
  const pre = preflight(req); if (pre) return pre;
  if (req.method !== "POST") return json({ error: "Use POST" }, 405);
  let b;
  try { b = await req.json(); } catch { return json({ error: "Bad request" }, 400); }
  // Boards are a fixed list so a caller cannot invent one. Monster Farkle
  // (farkle.html) posts to its own, and the scores table already has the
  // columns, so no migration.
  const BOARDS = ["daily", "level", "farkle", "farkle_daily"];
  const board = BOARDS.includes(b.board) ? b.board : "daily";
  const name = cleanName(b.name);
  const score = Math.floor(Number(b.score));
  const daily = board === "daily" || board === "farkle_daily";
  const day = daily && /^\d{4}-\d{2}-\d{2}$/.test(b.day || "") ? b.day : null;
  if (!name) return json({ error: "Pick a name" }, 400);
  if (!Number.isFinite(score) || score < 0 || score > 10000000) return json({ error: "Bad score" }, 400);
  if (daily && !day) return json({ error: "Missing day" }, 400);
  try {
    await sql`insert into scores (board, day, name, score) values (${board}, ${day}, ${name}, ${score})`;
    return json({ ok: true });
  } catch (e) {
    return json({ error: "Could not save score" }, 500);
  }
};
