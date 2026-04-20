import type { ReactNode } from "react";
import { ScrollView, StyleSheet, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

import { colors, spacing } from "@/theme";

export function Screen({ children, scroll = true }: { children: ReactNode; scroll?: boolean }) {
  const body = scroll ? (
    <ScrollView contentContainerStyle={styles.scrollBody}>{children}</ScrollView>
  ) : (
    <View style={styles.body}>{children}</View>
  );
  return <SafeAreaView style={styles.root}>{body}</SafeAreaView>;
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: colors.bg },
  body: { flex: 1, padding: spacing.lg },
  scrollBody: { padding: spacing.lg, paddingBottom: spacing.xxl },
});
