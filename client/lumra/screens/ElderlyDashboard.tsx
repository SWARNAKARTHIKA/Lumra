import React, { useEffect, useState } from "react";
import { View, Text, ScrollView, StyleSheet, ActivityIndicator, Alert } from "react-native";
import axios from "axios";
import { RouteProp, useRoute } from "@react-navigation/native";
import { RootStackParamList } from "../App";

type RouteProps = RouteProp<RootStackParamList, "ElderlyDashboard">;

const ElderlyDashboard = () => {
  const route = useRoute<RouteProps>();
  const { userId } = route.params;
  const [guardian, setGuardian] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  // Same: 10.0.2.2 to access FastAPI on port 8000
  const BASE_URL = "http://10.0.2.2:8000";

  useEffect(() => {
    axios
      .get(`${BASE_URL}/elderly/${userId}/guardian`)
      .then((res) => {
        setGuardian(res.data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Error:", err.message);
        Alert.alert("Error", "Unable to fetch guardian details.");
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#4b6cb7" />
        <Text>Loading...</Text>
      </View>
    );
  }

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.title}>Elderly Dashboard</Text>
      {guardian ? (
        <View style={styles.card}>
          <Text style={styles.name}>🧑‍🤝‍🧑 Guardian: {guardian.name}</Text>
          <Text>📧 {guardian.email}</Text>
          <Text>📞 {guardian.phone}</Text>
          <Text>🏠 {guardian.address}</Text>
          <Text>Relation: {guardian.relation}</Text>
        </View>
      ) : (
        <Text>No guardian connected yet.</Text>
      )}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: { padding: 20 },
  title: { fontSize: 22, fontWeight: "700", marginBottom: 10 },
  card: {
    backgroundColor: "#f4f7fb",
    padding: 15,
    marginBottom: 10,
    borderRadius: 10,
  },
  name: { fontWeight: "bold", fontSize: 18 },
  center: { flex: 1, justifyContent: "center", alignItems: "center" },
});

export default ElderlyDashboard;
