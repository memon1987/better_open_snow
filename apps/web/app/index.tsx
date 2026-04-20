import { useQuery } from "@tanstack/react-query";
import { StyleSheet, Text, View } from "react-native";

import { ResortCard } from "@/components/ResortCard";
import { Screen } from "@/components/Screen";
import { api, apiBaseUrl } from "@/lib/api";
import { colors, spacing } from "@/theme";

export default function ResortListScreen() {
  const { data, isLoading, error } = useQuery({
    queryKey: ["resorts"],
    queryFn: async () => {
      const { data, error } = await api.GET("/resorts");
      if (error) throw new Error(JSON.stringify(error));
      return data;
    },
  });

  return (
    <Screen>
      <Text style={styles.tagline}>
        Free snow tracker for Epic + Ikon · v0 MVP
      </Text>

      {isLoading && <Text style={styles.status}>Loading…</Text>}
      {error && (
        <View style={styles.errorBox}>
          <Text style={styles.errorTitle}>Couldn't reach the API</Text>
          <Text style={styles.errorBody}>Tried {apiBaseUrl}</Text>
          <Text style={styles.errorHint}>
            Is the emulator + `make api` running? On phone: same WiFi as the laptop?
          </Text>
        </View>
      )}

      {data?.resorts.map((r) => (
        <ResortCard
          key={r.resort_id}
          resort={{
            resort_id: r.resort_id,
            name: r.name,
            pass: r.pass as "epic" | "ikon",
            state: r.state,
            base_elevation_ft: r.base_elevation_ft,
            summit_elevation_ft: r.summit_elevation_ft,
            latest_snow_24h_in: r.latest_snow_24h_in,
            snow_depth_in: r.snow_depth_in,
          }}
        />
      ))}
    </Screen>
  );
}

const styles = StyleSheet.create({
  tagline: { color: colors.textMuted, marginBottom: spacing.lg, fontSize: 13 },
  status: { color: colors.textMuted, marginTop: spacing.md },
  errorBox: {
    borderWidth: 1,
    borderColor: colors.border,
    backgroundColor: colors.bgElevated,
    borderRadius: 10,
    padding: spacing.lg,
    marginTop: spacing.md,
  },
  errorTitle: { color: colors.text, fontWeight: "600", marginBottom: spacing.xs },
  errorBody: { color: colors.textMuted, fontSize: 13, fontFamily: "monospace" },
  errorHint: { color: colors.textDim, fontSize: 12, marginTop: spacing.sm },
});
