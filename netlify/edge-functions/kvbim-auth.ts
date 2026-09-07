// KV BIM Web teszt — jelszóvédelem a /kvbim-teszt/ aloldalra (HTTP Basic Auth, Netlify Edge Function).
//
// Miért edge function: ezen a Netlify-fiókon (2025-09 után létrehozott, ingyenes csomag) a beépített
// jelszóvédelem és a `_headers` fájlos `Basic-Auth` csak Pro csomagban érhető el. Az edge function
// minden csomagban fut, és a jelszó nem kerül a (nyilvános) git repóba: a Netlify környezeti
// változóban él (`KVBIM_TESZT_AUTH`, formátum: `felhasznalo:jelszo`; több fiók szóközzel elválasztva).
//
// Megjegyzés: az edge function által kiszolgált útvonalakon a `_headers` szabályok NEM érvényesülnek,
// ezért a noindex/CSP/cache fejléceket itt állítjuk be.

import type { Config, Context } from "@netlify/edge-functions";

const REALM = "KV BIM teszt";
const CSP = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; " +
  "connect-src 'self'; worker-src 'self' blob:; font-src 'self'; object-src 'none'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'";

function constantTimeEqual(a: string, b: string): boolean {
  const ea = new TextEncoder().encode(a), eb = new TextEncoder().encode(b);
  let diff = ea.length ^ eb.length;
  for (let i = 0; i < Math.max(ea.length, eb.length); i++) diff |= (ea[i] ?? 0) ^ (eb[i] ?? 0);
  return diff === 0;
}

function decodeBasic(header: string | null): string | null {
  if (!header) return null;
  const [scheme, encoded] = header.trim().split(/\s+/, 2);
  if (!scheme || scheme.toLowerCase() !== "basic" || !encoded) return null;
  try {
    const bytes = Uint8Array.from(atob(encoded), (c) => c.charCodeAt(0));
    return new TextDecoder().decode(bytes);
  } catch {
    return null;
  }
}

function unauthorized(message: string, status = 401): Response {
  const headers = new Headers({
    "Content-Type": "text/plain; charset=utf-8",
    "Cache-Control": "no-store",
    "X-Robots-Tag": "noindex, nofollow, noarchive, nosnippet",
    "Referrer-Policy": "no-referrer",
  });
  if (status === 401) headers.set("WWW-Authenticate", `Basic realm="${REALM}", charset="UTF-8"`);
  return new Response(message, { status, headers });
}

export default async (request: Request, context: Context) => {
  const configured = (Netlify.env.get("KVBIM_TESZT_AUTH") ?? "").split(/\s+/).filter(Boolean);
  if (!configured.length) {
    return unauthorized("A KV BIM tesztfelület hozzáférése még nincs beállítva (KVBIM_TESZT_AUTH).", 503);
  }
  const supplied = decodeBasic(request.headers.get("authorization"));
  // Minden konfigurált párral összehasonlítunk, hogy az időzítés ne áruljon el semmit.
  let ok = false;
  for (const credential of configured) if (supplied !== null && constantTimeEqual(supplied, credential)) ok = true;
  if (!ok) return unauthorized("KV BIM teszt — felhasználónév és jelszó szükséges.");

  const response = await context.next();
  const headers = new Headers(response.headers);
  const pathname = new URL(request.url).pathname;
  const longLived = /\.(js|css|bin|png|jpg|jpeg|webp|woff2?)$/i.test(pathname) || pathname.includes("/data/");
  headers.set("Cache-Control", longLived ? "private, max-age=86400" : "private, no-cache, must-revalidate");
  headers.set("X-Robots-Tag", "noindex, nofollow, noarchive, nosnippet");
  headers.set("Referrer-Policy", "no-referrer");
  headers.set("X-Content-Type-Options", "nosniff");
  headers.set("X-Frame-Options", "DENY");
  headers.set("Content-Security-Policy", CSP);
  headers.set("Cross-Origin-Resource-Policy", "same-origin");
  if (pathname.endsWith(".bin")) headers.set("Content-Type", "application/octet-stream");
  return new Response(response.body, { status: response.status, statusText: response.statusText, headers });
};

export const config: Config = {
  path: ["/kvbim-teszt", "/kvbim-teszt/*"],
};
