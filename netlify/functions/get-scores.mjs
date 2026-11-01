// GET /.netlify/functions/get-scores?board=daily&day=2026-10-31  -> top 20 scores
import { sql, json, preflight } from "./_db.mjs";

export default async (req) => {
  const pre = preflight(req); if (pre) return pre;
  const u = new URL(req.url);
  // Same fixed list as add-score. Monster Farkle has its own two boards.
  const BOARDS = ["daily", "level", "farkle", "farkle_daily"];
  const asked = u.searchParams.get("board");
  const board = BOARDS.includes(asked) ? asked : "daily";
  const day = u.searchParams.get("day");
  try {
    const daily = board === "daily" || board === "farkle_daily";
    const rows = daily && /^\d{4}-\d{2}-\d{2}$/.test(day || "")
      ? await sql`select name, score from scores where board = ${board} and day = ${day} order by score desc, created_at asc limit 20`
      : await sql`select name, score from scores where board = ${board} order by score desc, created_at asc limit 20`;
    return json({ scores: rows });
  } catch (e) {
    return json({ error: "Could not load scores" }, 500);
  }
};
