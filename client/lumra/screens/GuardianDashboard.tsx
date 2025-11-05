import React, { useState, useEffect } from "react";
import { View, Text, TextInput, Button, Alert, StyleSheet, FlatList } from "react-native";
import MapView, { Marker, Circle } from "react-native-maps";
import { NativeStackScreenProps } from "@react-navigation/native-stack";
import axios from "axios";
import { RootStackParamList } from "../App";

type Props = NativeStackScreenProps<RootStackParamList, "GuardianDashboard">;

type Elderly = {
  elderly_id: number;
  elderly_name: string;
  phone: string;
};

export default function GuardianDashboard({ route }: Props) {
  const { userId } = route.params;

  // Request input
  const [elderlyPhone, setElderlyPhone] = useState("");
  const [elderlies, setElderlies] = useState<Elderly[]>([]);

  // Geofence input
  const [radius, setRadius] = useState(""); // in meters
  const latitude = 12.9716; // Hardcoded location
  const longitude = 77.5946;

  const BASE_URL = "http://10.0.2.2:8000"; // Android emulator localhost

  // Fetch accepted elderlies
  useEffect(() => {
    fetchElderlies();
  }, []);

  const fetchElderlies = async () => {
    try {
      const res = await axios.get(`${BASE_URL}/guardian/${userId}/elderlies`);
      setElderlies(res.data);
    } catch (err: any) {
      console.log("Error fetching elderlies:", err.message);
    }
  };

  // Send request to elderly
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
      Alert.alert("Success", res.data.message);
      setElderlyPhone("");
      fetchElderlies(); // Refresh accepted elderlies
    } catch (err: any) {
      Alert.alert("Error", err.response?.data?.detail || "Something went wrong");
    }
  };

  // Save geofence
  const saveGeofence = async () => {
    if (!radius.trim()) {
      Alert.alert("Validation", "Please enter a radius");
      return;
    }

    try {
      await axios.post(`${BASE_URL}/geofence/set`, {
        elderly_id: elderlies[0]?.elderly_id || 1, // demo, first elderly
        latitude,
        longitude,
        radius: parseFloat(radius),
      });
      Alert.alert("Success", "Geofence saved!");
    } catch (err: any) {
      Alert.alert("Error", err.response?.data?.detail || "Failed to save geofence");
    }
  };

  return (
    <View style={styles.container}>
      {/* Request Section */}
      <Text style={styles.title}>Send Request to Elderly</Text>
      <TextInput
        value={elderlyPhone}
        onChangeText={setElderlyPhone}
        placeholder="Enter Elderly Phone"
        style={styles.input}
      />
      <Button title="Send Request" onPress={sendRequest} />

      {/* Accepted Elderlies */}
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

      {/* Geofence Section */}
      <Text style={[styles.title, { marginTop: 20 }]}>Set Geofence</Text>
      <TextInput
        value={radius}
        onChangeText={setRadius}
        placeholder="Enter radius (meters)"
        keyboardType="numeric"
        style={styles.input}
      />
      <Button title="Save Geofence" onPress={saveGeofence} color="#4b413c" />

      {/* Map Display */}
      <Text style={[styles.title, { marginTop: 20 }]}>Geofence Map</Text>
      <MapView
        style={{ width: "100%", height: 300 }}
        initialRegion={{
          latitude,
          longitude,
          latitudeDelta: 0.01,
          longitudeDelta: 0.01,
        }}
      >
        <Marker coordinate={{ latitude, longitude }} />
        {radius ? (
          <Circle
            center={{ latitude, longitude }}
            radius={parseFloat(radius)}
            fillColor="rgba(0, 150, 255, 0.2)"
            strokeColor="blue"
          />
        ) : null}
      </MapView>
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
