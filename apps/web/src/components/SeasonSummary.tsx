import { StyleSheet, Text, View } from "react-native";

import { monthDay } from "@/lib/format";
import { colors, radius, spacing } from "@/theme";

export type DailySnowData = {
  date: string;
  snow_in_24h?: number | null;
};

export function SeasonSummary({
  seasonStart,
  seasonToDate,
  daily,
  timezone,
}: {
  seasonStart: string;
  seasonToDate: number;
  daily: DailySnowData[];
  timezone?: string;
}) {
  const withSnow = daily.filter((d) => (d.snow_in_24h ?? 0) > 0);
  const lastStorm = withSnow[withSnow.length - 1];
  const biggest = [...daily].sort(
    (a, b) => (b.snow_in_24h ?? 0) - (a.snow_in_24h ?? 0),
  )[0];

  return (
    <View style={styles.wrap}>
      <View style={styles.statsRow}>
        <Stat
          label="Season total"
          value={`${seasonToDate.toFixed(0)}"`}
          sub={`since ${monthDay(seasonStart, timezone)}`}
          big
        />
        <Stat
          label="Last storm"
          value={
            lastStorm?.snow_in_24h != null ? `${lastStorm.snow_in_24h.toFixed(1)}"` : "—"
          }
          sub={lastStorm ? monthDay(lastStorm.date, timezone) : undefined}
        />
        <Stat
          label="Biggest day"
          value={
            biggest?.snow_in_24h != null ? `${biggest.snow_in_24h.toFixed(1)}"` : "—"
          }
          sub={biggest ? monthDay(biggest.date, timezone) : undefined}
        />
      </View>
      <SeasonBars daily={daily} />
    </View>
  );
}

function Stat({
  label,
  value,
  sub,
  big,
}: {
  label: string;
  value: string;
  sub?: string;
  big?: boolean;
}) {
  return (
    <View style={styles.stat}>
      <Text style={styles.statLabel}>{label}</Text>
      <Text style={[styles.statValue, big && styles.statValueBig]}>{value}</Text>
      {sub ? <Text style={styles.statSub}>{sub}</Text> : null}
    </View>
  );
}

function SeasonBars({ daily }: { daily: DailySnowData[] }) {
  const max = Math.max(1, ...daily.map((d) => d.snow_in_24h ?? 0));
  // Each bar is 1 day — on a phone ~200 days gets ~1.5px each, fine visually.
  return (
    <View style={styles.barsRow}>
      {daily.map((d) => {
        const v = d.snow_in_24h ?? 0;
        const pct = v > 0 ? Math.max(4, (v / max) * 100) : 0;
        return (
          <View key={d.date} style={styles.barCol}>
            <View
              style={[styles.bar, { height: `${pct}%` }, v === 0 && styles.barEmpty]}
            />
          </View>
        );
      })}
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: {
    backgroundColor: colors.bgElevated,
    borderRadius: radius.lg,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.lg,
    marginTop: spacing.lg,
  },
  statsRow: { flexDirection: "row", marginBottom: spacing.lg },
  stat: { flex: 1 },
  statLabel: { color: colors.textDim, fontSize: 11, letterSpacing: 1 },
  statValue: { color: colors.text, fontSize: 20, fontWeight: "600", marginTop: 2 },
  statValueBig: { fontSize: 28, color: colors.accent },
  statSub: { color: colors.textDim, fontSize: 11, marginTop: 2 },
  barsRow: {
    flexDirection: "row",
    alignItems: "flex-end",
    height: 64,
    gap: 1,
  },
  barCol: { flex: 1, height: "100%", justifyContent: "flex-end" },
  bar: {
    width: "100%",
    backgroundColor: colors.accent,
    borderRadius: 1,
  },
  barEmpty: { backgroundColor: colors.bgSubtle, height: 2 },
});
