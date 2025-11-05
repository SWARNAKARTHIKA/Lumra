import React, { useState, useEffect } from "react";
import { View, Text, TextInput, Button, Alert, StyleSheet, FlatList } from "react-native";
import axios from "axios";
import { NativeStackScreenProps } from "@react-navigation/native-stack";
import { RootStackParamList } from "../App";
import { BASE_URL } from "../apiConfig";

type Props = NativeStackScreenProps<RootStackParamList, "GuardianDashboard">;

type Elderly = {
  elderly_id: number;
  elderly_name: string;
  phone: string;
};

export default function GuardianDashboard({ route }: Props) {
  const { userId } = route.params;
  const [elderlyPhone, setElderlyPhone] = useState("");
  const [elderlies, setElderlies] = useState<Elderly[]>([]);

  // Fetch elderlies when screen opens
  useEffect(() => {
    fetchElderlies();
  }, []);

  const fetchElderlies = async () => {
    try {
      const res = await axios.get(`${BASE_URL}/guardian/${userId}/elderlies`);
      setElderlies(res.data);
    } catch (err) {
      console.error("Error fetching elderlies:", err);
    }
  };

  const sendRequest = async () => {
    if (!elderlyPhone.trim()) {
      Alert.alert("Validation", "Please enter an elderly phone number.");
      return;
    }

    try {
      const res = await axios.post(`${BASE_URL}/guardian/request`, {
        guardian_id: userId,
        elderly_phone: elderlyPhone,
      });

      Alert.alert("Success", res.data.message || "Request sent successfully!");
      setElderlyPhone("");

      // Refresh accepted elderlies after sending a request
      fetchElderlies();

    } catch (err: any) {
      console.error(err);
      Alert.alert("Error", err.response?.data?.detail || "Something went wrong");
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Send Request to Elderly</Text>

      <TextInput
        value={elderlyPhone}
        onChangeText={setElderlyPhone}
        placeholder="Enter Elderly Phone"
        keyboardType="number-pad"
        style={styles.input}
      />

      <Button title="Send Request" onPress={sendRequest} />

      <Text style={[styles.title, { marginTop: 20 }]}>Connected Elderlies</Text>

      <FlatList
        data={elderlies}
        keyExtractor={(item) => item.elderly_id.toString()}
        renderItem={({ item }) => (
          <View style={styles.elderlyCard}>
            <Text style={styles.elderlyName}>{item.elderly_name}</Text>
            <Text style={styles.elderlyPhone}>📞 {item.phone}</Text>
          </View>
        )}
        ListEmptyComponent={<Text style={styles.emptyText}>No accepted elderlies yet.</Text>}
      />

      <Button title="Refresh List" onPress={fetchElderlies} color="#4b413c" />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20, backgroundColor: "#f7f3f0" },
  title: { fontSize: 18, marginBottom: 10, color: "#4b413c", fontWeight: "bold" },
  input: {
    borderWidth: 1,
    borderColor: "#ccc",
    padding: 10,
    marginBottom: 15,
    borderRadius: 8,
    backgroundColor: "#fff",
  },
  elderlyCard: {
    backgroundColor: "#fff",
    padding: 12,
    marginVertical: 6,
    borderRadius: 10,
    borderColor: "#ddd",
    borderWidth: 1,
  },
  elderlyName: { fontSize: 16, color: "#333", fontWeight: "500" },
  elderlyPhone: { fontSize: 14, color: "#777" },
  emptyText: { textAlign: "center", marginTop: 10, color: "#999" },
});
