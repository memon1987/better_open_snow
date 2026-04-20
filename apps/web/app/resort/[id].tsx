import { useQuery } from "@tanstack/react-query";
import { Stack, useLocalSearchParams } from "expo-router";
import { Pressable, StyleSheet, Text, View } from "react-native";

import { ForecastBars } from "@/components/ForecastBars";
import { NarrativeList } from "@/components/NarrativeList";
import { Screen } from "@/components/Screen";
import { SeasonSummary } from "@/components/SeasonSummary";
import { SnotelPanel } from "@/components/SnotelPanel";
import { api } from "@/lib/api";
import { colors, radius, spacing } from "@/theme";

export default function ResortDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();

  const resortQ = useQuery({
    queryKey: ["resort", id],
    queryFn: async () => {
      const { data, error } = await api.GET("/resorts/{resort_id}", {
        params: { path: { resort_id: id } },
      });
      if (error) throw new Error(JSON.stringify(error));
      return data;
    },
    enabled: !!id,
  });

  const forecastQ = useQuery({
    queryKey: ["forecast", id],
    queryFn: async () => {
      const { data, error } = await api.GET("/resorts/{resort_id}/forecast", {
        params: { path: { resort_id: id } },
      });
      if (error) throw new Error(JSON.stringify(error));
      return data;
    },
    enabled: !!id,
    retry: false,
  });

  const obsQ = useQuery({
    queryKey: ["observations", id],
    queryFn: async () => {
      const { data, error } = await api.GET("/resorts/{resort_id}/observations", {
        params: { path: { resort_id: id } },
      });
      if (error) throw new Error(JSON.stringify(error));
      return data;
    },
    enabled: !!id,
  });

  const historyQ = useQuery({
    queryKey: ["history", id],
    queryFn: async () => {
      const { data, error } = await api.GET("/resorts/{resort_id}/history", {
        params: { path: { resort_id: id } },
      });
      if (error) throw new Error(JSON.stringify(error));
      return data;
    },
    enabled: !!id,
  });

  const resort = resortQ.data;
  const tz = resort?.timezone;
  const isDemo = forecastQ.data?.is_demo || obsQ.data?.is_demo;

  const refetchAll = () => {
    forecastQ.refetch();
    obsQ.refetch();
    historyQ.refetch();
  };

  return (
    <Screen>
      <Stack.Screen options={{ title: resort?.name ?? "" }} />

      {resort && (
        <View style={styles.header}>
          <View style={{ flex: 1 }}>
            <Text style={styles.name}>{resort.name}</Text>
            <Text style={styles.sub}>
              {resort.state} · {resort.pass.toUpperCase()} ·{" "}
              {resort.base.elevation_ft.toLocaleString()}–
              {resort.summit.elevation_ft.toLocaleString()} ft
            </Text>
          </View>
          <Pressable onPress={refetchAll} style={({ pressed }) => [styles.refresh, pressed && styles.refreshPressed]}>
            <Text style={styles.refreshText}>↻</Text>
          </Pressable>
        </View>
      )}

      {isDemo && (
        <View style={styles.demoBanner}>
          <Text style={styles.demoText}>
            Demo data · BOS_USE_DEMO_DATA=1 · values are synthetic. Unset for real data.
          </Text>
        </View>
      )}

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>10-day snow</Text>
        {forecastQ.isLoading && <Text style={styles.muted}>Loading forecast…</Text>}
        {forecastQ.error && (
          <Text style={styles.muted}>
            No forecast yet. Run `make ingest-once` and refresh.
          </Text>
        )}
        {forecastQ.data && <ForecastBars daily={forecastQ.data.daily} />}
      </View>

      {forecastQ.data && forecastQ.data.narrative.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>NWS narrative</Text>
          <NarrativeList periods={forecastQ.data.narrative} />
        </View>
      )}

      <SnotelPanel snotel={obsQ.data?.snotel} />

      {historyQ.data && historyQ.data.daily.length > 0 && (
        <SeasonSummary
          seasonStart={historyQ.data.season_start}
          seasonToDate={historyQ.data.season_to_date_in}
          daily={historyQ.data.daily}
          timezone={tz}
        />
      )}
    </Screen>
  );
}

const styles = StyleSheet.create({
  header: {
    marginBottom: spacing.lg,
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.md,
  },
  name: { color: colors.text, fontSize: 28, fontWeight: "700" },
  sub: { color: colors.textMuted, marginTop: spacing.xs, fontSize: 13 },
  refresh: {
    width: 40,
    height: 40,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: colors.border,
    alignItems: "center",
    justifyContent: "center",
  },
  refreshPressed: { opacity: 0.6 },
  refreshText: { color: colors.textMuted, fontSize: 20 },
  section: {
    backgroundColor: colors.bgElevated,
    borderRadius: radius.lg,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.lg,
    marginBottom: spacing.md,
  },
  sectionTitle: {
    color: colors.textMuted,
    fontSize: 11,
    letterSpacing: 2,
    marginBottom: spacing.md,
  },
  muted: { color: colors.textMuted, fontStyle: "italic" },
  demoBanner: {
    backgroundColor: "rgba(255, 182, 77, 0.15)",
    borderLeftWidth: 3,
    borderLeftColor: colors.demoWarn,
    padding: spacing.md,
    marginBottom: spacing.lg,
    borderRadius: radius.sm,
  },
  demoText: { color: colors.demoWarn, fontSize: 12 },
});
