// POST /.netlify/functions/add-score  {board, day, name, score}
import { sql, json, cleanName } from "./_db.mjs";

export default async (req) => {
  if (req.method !== "POST") return json({ error: "Use POST" }, 405);
  let b;
  try { b = await req.json(); } catch { return json({ error: "Bad request" }, 400); }
  const board = b.board === "level" ? "level" : "daily";
  const name = cleanName(b.name);
  const score = Math.floor(Number(b.score));
  const day = board === "daily" && /^\d{4}-\d{2}-\d{2}$/.test(b.day || "") ? b.day : null;
  if (!name) return json({ error: "Pick a name" }, 400);
  if (!Number.isFinite(score) || score < 0 || score > 10000000) return json({ error: "Bad score" }, 400);
  if (board === "daily" && !day) return json({ error: "Missing day" }, 400);
  try {
    await sql`insert into scores (board, day, name, score) values (${board}, ${day}, ${name}, ${score})`;
    return json({ ok: true });
  } catch (e) {
    return json({ error: "Could not save score" }, 500);
  }
};
