import Constants from "expo-constants";
import createClient from "openapi-fetch";
import type { paths } from "@bos/shared";

function resolveBaseUrl(): string {
  // 1. Explicit override (EXPO_PUBLIC_API_BASE_URL in .env)
  const env =
    (process.env as Record<string, string | undefined>).EXPO_PUBLIC_API_BASE_URL ??
    (Constants.expoConfig?.extra as { apiBaseUrl?: string } | undefined)?.apiBaseUrl;
  if (env) return env;

  // 2. On web, infer from window.location so phones on the same LAN that
  //    load the app via http://<laptop-ip>:8081 will also find the API at
  //    http://<laptop-ip>:8000 — no manual env var needed.
  if (typeof window !== "undefined" && window.location?.hostname) {
    return `http://${window.location.hostname}:8000`;
  }

  return "http://localhost:8000";
}

export const apiBaseUrl = resolveBaseUrl();
export const api = createClient<paths>({ baseUrl: apiBaseUrl });
