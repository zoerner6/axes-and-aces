// POST /.netlify/functions/save-game  {code, data}
import { sql, json, preflight } from "./_db.mjs";

export default async (req) => {
  const pre = preflight(req); if (pre) return pre;
  if (req.method !== "POST") return json({ error: "Use POST" }, 405);
  let b;
  try { b = await req.json(); } catch { return json({ error: "Bad request" }, 400); }
  const code = String(b.code || "");
  if (!/^[A-Za-z0-9]{12,64}$/.test(code) || typeof b.data !== "object" || !b.data) return json({ error: "Bad save" }, 400);
  const data = JSON.stringify(b.data);
  if (data.length > 400000) return json({ error: "Save too large" }, 413);
  try {
    await sql`select save_game(${code}, ${data}::jsonb)`;
    return json({ ok: true });
  } catch (e) {
    return json({ error: "Could not save" }, 500);
  }
};
