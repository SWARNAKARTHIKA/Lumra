import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { RootStackParamList } from '../App'; // Adjust path if needed

// Typed props for the screen
type Props = NativeStackScreenProps<RootStackParamList, 'UserDetails'>;

export default function UserDetailsScreen({ route }: Props) {
  const { message, role, userId } = route.params;

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Login Successful 🎉</Text>

      <View style={styles.card}>
        <Text style={styles.data}>
          <Text style={styles.label}>Message: </Text>
          {message}
        </Text>
        <Text style={styles.data}>
          <Text style={styles.label}>Role: </Text>
          {role}
        </Text>
        <Text style={styles.data}>
          <Text style={styles.label}>User ID: </Text>
          {userId}
        </Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#f7f3f0',
  },
  title: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#4b413c',
    marginBottom: 20,
  },
  card: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 20,
    width: '90%',
    elevation: 3,
  },
  data: {
    fontSize: 16,
    color: '#333',
    marginVertical: 8,
  },
  label: {
    fontWeight: 'bold',
    color: '#4b413c',
  },
});
