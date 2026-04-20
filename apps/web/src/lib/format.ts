export function inches(v: number | null | undefined, empty = "—"): string {
  return v == null ? empty : `${Number(v).toFixed(1)}"`;
}

export function tempF(v: number | null | undefined, empty = "—"): string {
  return v == null ? empty : `${Math.round(Number(v))}°`;
}

export function weekday(iso: string, tz?: string): string {
  const d = new Date(iso.length === 10 ? `${iso}T12:00:00Z` : iso);
  return d.toLocaleDateString("en-US", {
    weekday: "short",
    timeZone: tz,
  });
}

export function monthDay(iso: string, tz?: string): string {
  const d = new Date(iso.length === 10 ? `${iso}T12:00:00Z` : iso);
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric", timeZone: tz });
}

export function clockLocal(iso: string, tz?: string): string {
  const d = new Date(iso);
  return d.toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
    timeZone: tz,
  });
}
