import { Link } from "expo-router";
import { Pressable, StyleSheet, Text, View } from "react-native";

import { colors, radius, spacing } from "@/theme";

export type ResortCardData = {
  resort_id: string;
  name: string;
  pass: "epic" | "ikon";
  state: string;
  base_elevation_ft: number;
  summit_elevation_ft: number;
  latest_snow_24h_in?: number | null;
  snow_depth_in?: number | null;
};

export function ResortCard({ resort }: { resort: ResortCardData }) {
  const passColor = resort.pass === "epic" ? colors.epic : colors.ikon;
  return (
    <Link href={{ pathname: "/resort/[id]", params: { id: resort.resort_id } }} asChild>
      <Pressable style={({ pressed }) => [styles.card, pressed && styles.cardPressed]}>
        <View style={styles.headerRow}>
          <Text style={styles.name}>{resort.name}</Text>
          <View style={[styles.passChip, { borderColor: passColor }]}>
            <Text style={[styles.passChipText, { color: passColor }]}>
              {resort.pass.toUpperCase()}
            </Text>
          </View>
        </View>
        <Text style={styles.sub}>
          {resort.state} · {resort.base_elevation_ft.toLocaleString()}–
          {resort.summit_elevation_ft.toLocaleString()} ft
        </Text>

        <View style={styles.stats}>
          <Stat
            label="24H"
            value={resort.latest_snow_24h_in != null ? `${resort.latest_snow_24h_in}"` : "—"}
            emphasized={(resort.latest_snow_24h_in ?? 0) > 0}
          />
          <Stat
            label="Depth"
            value={resort.snow_depth_in != null ? `${resort.snow_depth_in}"` : "—"}
          />
        </View>
      </Pressable>
    </Link>
  );
}

function Stat({
  label,
  value,
  emphasized,
}: {
  label: string;
  value: string;
  emphasized?: boolean;
}) {
  return (
    <View style={styles.stat}>
      <Text style={styles.statLabel}>{label}</Text>
      <Text style={[styles.statValue, emphasized && styles.statValueAccent]}>{value}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.bgElevated,
    borderRadius: radius.lg,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.lg,
    marginBottom: spacing.md,
  },
  cardPressed: { opacity: 0.75 },
  headerRow: { flexDirection: "row", alignItems: "center", justifyContent: "space-between" },
  name: { color: colors.text, fontSize: 20, fontWeight: "600" },
  sub: { color: colors.textMuted, marginTop: spacing.xs, fontSize: 13 },
  passChip: {
    borderWidth: 1,
    borderRadius: radius.sm,
    paddingHorizontal: spacing.sm,
    paddingVertical: 2,
  },
  passChipText: { fontSize: 11, fontWeight: "700", letterSpacing: 1 },
  stats: {
    flexDirection: "row",
    marginTop: spacing.md,
    borderTopWidth: 1,
    borderTopColor: colors.border,
    paddingTop: spacing.md,
  },
  stat: { flex: 1 },
  statLabel: { color: colors.textDim, fontSize: 11, letterSpacing: 1 },
  statValue: { color: colors.text, fontSize: 22, fontWeight: "600", marginTop: 2 },
  statValueAccent: { color: colors.accent },
});
