// Shared database helper: the connection string lives only in Netlify's DATABASE_URL secret.
import { neon } from "@neondatabase/serverless";

let client;
export const sql = (strings, ...values) => {
  client ||= neon(process.env.DATABASE_URL);
  return client(strings, ...values);
};

// The iPhone app serves the game from inside the app, on capacitor://, so every
// call to these functions is cross-origin and the browser blocks it without
// these headers. Nothing here reads a cookie or a session: scores are public and
// a cloud save is only as private as its own code, so allowing any origin gives
// away nothing that a plain HTTP request could not already reach.
const cors = {
  "access-control-allow-origin": "*",
  "access-control-allow-headers": "content-type",
  "access-control-allow-methods": "GET,POST,OPTIONS",
};

export const json = (body, status = 200) =>
  new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json", "cache-control": "no-store", ...cors },
  });

// A POST carrying JSON is preflighted, so every function answers OPTIONS first.
export const preflight = (req) =>
  req.method === "OPTIONS" ? new Response(null, { status: 204, headers: cors }) : null;

export const cleanName = (n) =>
  String(n || "").replace(/[^\p{L}\p{N} _.'-]/gu, "").trim().slice(0, 20);
