import type { ReactNode } from "react";
import { ScrollView, StyleSheet, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

import { colors, spacing } from "@/theme";

// On wide desktop browsers we still want the phone-style column (resorts are
// tall cards; a giant content area would just add whitespace). Cap the inner
// content width and center it.
const MAX_CONTENT_WIDTH = 720;

export function Screen({ children, scroll = true }: { children: ReactNode; scroll?: boolean }) {
  const inner = <View style={styles.inner}>{children}</View>;
  const body = scroll ? (
    <ScrollView contentContainerStyle={styles.scrollBody}>{inner}</ScrollView>
  ) : (
    <View style={styles.body}>{inner}</View>
  );
  return <SafeAreaView style={styles.root}>{body}</SafeAreaView>;
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: colors.bg },
  body: { flex: 1, padding: spacing.lg, alignItems: "center" },
  scrollBody: { padding: spacing.lg, paddingBottom: spacing.xxl, alignItems: "center" },
  inner: { width: "100%", maxWidth: MAX_CONTENT_WIDTH },
});
