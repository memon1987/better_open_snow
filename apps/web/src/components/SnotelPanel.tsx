import { StyleSheet, Text, View } from "react-native";

import { colors, radius, spacing } from "@/theme";

export type SnotelData = {
  station_triplet: string;
  observed_at: string;
  swe_in?: number | null;
  snow_depth_in?: number | null;
  snow_24h_in?: number | null;
  air_temp_f?: number | null;
};

export function SnotelPanel({ snotel }: { snotel: SnotelData | null | undefined }) {
  if (!snotel) {
    return (
      <View style={styles.card}>
        <Text style={styles.title}>SNOTEL</Text>
        <Text style={styles.empty}>
          No observation yet. Run `make ingest-snotel` with network access.
        </Text>
      </View>
    );
  }

  const observedAt = new Date(snotel.observed_at);
  const observedLabel = observedAt.toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });

  return (
    <View style={styles.card}>
      <View style={styles.titleRow}>
        <Text style={styles.title}>SNOTEL</Text>
        <Text style={styles.station}>{snotel.station_triplet}</Text>
      </View>
      <View style={styles.statsRow}>
        <Stat label="Depth" value={fmtIn(snotel.snow_depth_in)} />
        <Stat label="SWE" value={fmtIn(snotel.swe_in)} />
        <Stat label="24H" value={fmtIn(snotel.snow_24h_in)} />
        <Stat label="Temp" value={snotel.air_temp_f != null ? `${Math.round(snotel.air_temp_f)}°` : "—"} />
      </View>
      <Text style={styles.observed}>Observed {observedLabel}</Text>
    </View>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <View style={styles.stat}>
      <Text style={styles.statLabel}>{label}</Text>
      <Text style={styles.statValue}>{value}</Text>
    </View>
  );
}

function fmtIn(v: number | null | undefined): string {
  return v != null ? `${v.toFixed(1)}"` : "—";
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.bgElevated,
    borderRadius: radius.lg,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.lg,
    marginTop: spacing.lg,
  },
  titleRow: { flexDirection: "row", justifyContent: "space-between", alignItems: "center" },
  title: { color: colors.textMuted, fontSize: 11, letterSpacing: 2 },
  station: { color: colors.textDim, fontSize: 11 },
  statsRow: { flexDirection: "row", marginTop: spacing.md },
  stat: { flex: 1 },
  statLabel: { color: colors.textDim, fontSize: 11, letterSpacing: 1 },
  statValue: { color: colors.text, fontSize: 20, fontWeight: "600", marginTop: 2 },
  observed: { color: colors.textDim, fontSize: 11, marginTop: spacing.md },
  empty: { color: colors.textMuted, fontStyle: "italic", marginTop: spacing.sm },
});
