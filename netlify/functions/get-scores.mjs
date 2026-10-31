// GET /.netlify/functions/get-scores?board=daily&day=2026-10-31  -> top 20 scores
import { sql, json } from "./_db.mjs";

export default async (req) => {
  const u = new URL(req.url);
  const board = u.searchParams.get("board") === "level" ? "level" : "daily";
  const day = u.searchParams.get("day");
  try {
    const rows = board === "daily" && /^\d{4}-\d{2}-\d{2}$/.test(day || "")
      ? await sql`select name, score from scores where board = 'daily' and day = ${day} order by score desc, created_at asc limit 20`
      : await sql`select name, score from scores where board = ${board} order by score desc, created_at asc limit 20`;
    return json({ scores: rows });
  } catch (e) {
    return json({ error: "Could not load scores" }, 500);
  }
};
