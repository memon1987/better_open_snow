import { StyleSheet, Text, View } from "react-native";

import { colors, radius, spacing } from "@/theme";

export type DailyPoint = {
  date: string;
  snow_in?: number | null;
  temp_hi_f?: number | null;
  temp_lo_f?: number | null;
};

export function ForecastBars({ daily }: { daily: DailyPoint[] }) {
  if (!daily.length) {
    return <Text style={styles.empty}>No forecast data.</Text>;
  }
  const max = Math.max(1, ...daily.map((d) => d.snow_in ?? 0));

  return (
    <View style={styles.row}>
      {daily.map((day) => {
        const v = day.snow_in ?? 0;
        const pct = (v / max) * 100;
        const weekday = new Date(`${day.date}T12:00:00Z`).toLocaleDateString("en-US", {
          weekday: "short",
        });
        return (
          <View key={day.date} style={styles.col}>
            <Text style={styles.value}>{v > 0 ? `${v.toFixed(1)}"` : "—"}</Text>
            <View style={styles.track}>
              <View style={[styles.bar, { height: `${Math.max(pct, v > 0 ? 6 : 0)}%` }]} />
            </View>
            <Text style={styles.day}>{weekday}</Text>
            <Text style={styles.temp}>
              {day.temp_hi_f != null ? Math.round(day.temp_hi_f) : "—"}°/
              {day.temp_lo_f != null ? Math.round(day.temp_lo_f) : "—"}°
            </Text>
          </View>
        );
      })}
    </View>
  );
}

const styles = StyleSheet.create({
  row: {
    flexDirection: "row",
    alignItems: "flex-end",
    height: 200,
    gap: spacing.xs,
  },
  col: {
    flex: 1,
    alignItems: "center",
    height: "100%",
  },
  value: { color: colors.text, fontSize: 11, fontWeight: "600", marginBottom: 2 },
  track: {
    flex: 1,
    width: "100%",
    justifyContent: "flex-end",
    backgroundColor: colors.bgSubtle,
    borderRadius: radius.sm,
    overflow: "hidden",
  },
  bar: {
    width: "100%",
    backgroundColor: colors.accent,
    borderTopLeftRadius: radius.sm,
    borderTopRightRadius: radius.sm,
  },
  day: { color: colors.textMuted, fontSize: 11, marginTop: 4, textTransform: "uppercase" },
  temp: { color: colors.textDim, fontSize: 11 },
  empty: { color: colors.textMuted, fontStyle: "italic" },
});
