// GET /.netlify/functions/load-game?code=XXXX  -> {data}
import { sql, json, preflight } from "./_db.mjs";

export default async (req) => {
  const pre = preflight(req); if (pre) return pre;
  const code = new URL(req.url).searchParams.get("code") || "";
  if (!/^[A-Za-z0-9]{12,64}$/.test(code)) return json({ error: "Bad code" }, 400);
  try {
    const rows = await sql`select load_game(${code}) as data`;
    const data = rows[0] && rows[0].data;
    return data ? json({ data }) : json({ error: "No save found for that code" }, 404);
  } catch (e) {
    return json({ error: "Could not load" }, 500);
  }
};
