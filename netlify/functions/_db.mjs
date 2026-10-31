// Shared database helper: the connection string lives only in Netlify's DATABASE_URL secret.
import { neon } from "@neondatabase/serverless";

let client;
export const sql = (strings, ...values) => {
  client ||= neon(process.env.DATABASE_URL);
  return client(strings, ...values);
};

export const json = (body, status = 200) =>
  new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json", "cache-control": "no-store" },
  });

export const cleanName = (n) =>
  String(n || "").replace(/[^\p{L}\p{N} _.'-]/gu, "").trim().slice(0, 20);
