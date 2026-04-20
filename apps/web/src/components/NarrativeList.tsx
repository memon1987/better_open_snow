import { StyleSheet, Text, View } from "react-native";

import { colors, radius, spacing } from "@/theme";

export type NarrativePeriodData = {
  name: string;
  start: string;
  end: string;
  temp_f?: number | null;
  wind?: string | null;
  short: string;
  detailed?: string | null;
  is_daytime: boolean;
};

export function NarrativeList({ periods }: { periods: NarrativePeriodData[] }) {
  if (!periods.length) {
    return <Text style={styles.empty}>No narrative forecast yet.</Text>;
  }
  return (
    <View>
      {periods.slice(0, 6).map((p) => (
        <View
          key={`${p.name}-${p.start}`}
          style={[styles.row, !p.is_daytime && styles.rowNight]}
        >
          <View style={styles.nameCol}>
            <Text style={styles.name}>{p.name}</Text>
            <Text style={styles.temp}>
              {p.temp_f != null ? `${Math.round(p.temp_f)}°` : "—"}
            </Text>
          </View>
          <View style={styles.bodyCol}>
            <Text style={styles.short}>{p.short}</Text>
            {p.wind ? <Text style={styles.wind}>Wind {p.wind}</Text> : null}
          </View>
        </View>
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  row: {
    flexDirection: "row",
    paddingVertical: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
    alignItems: "flex-start",
  },
  rowNight: { opacity: 0.85 },
  nameCol: { width: 90 },
  bodyCol: { flex: 1 },
  name: { color: colors.textMuted, fontSize: 12, letterSpacing: 1 },
  temp: { color: colors.text, fontSize: 22, fontWeight: "600", marginTop: 2 },
  short: { color: colors.text, fontSize: 14, lineHeight: 20 },
  wind: { color: colors.textDim, fontSize: 12, marginTop: spacing.xs },
  empty: { color: colors.textMuted, fontStyle: "italic" },
  container: { borderRadius: radius.md },
});
