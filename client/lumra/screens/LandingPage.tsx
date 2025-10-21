// ...existing code...
import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { RootStackParamList } from '../App';
import { useFonts, Pacifico_400Regular } from '@expo-google-fonts/pacifico';

type NavProp = NativeStackNavigationProp<RootStackParamList, 'Landing'>;

const LandingPage: React.FC = () => {
  const navigation = useNavigation<NavProp>();
  const [fontsLoaded] = useFonts({ Pacifico_400Regular });

  if (!fontsLoaded) return null;

  return (
    <View style={styles.screen}>
      <View style={styles.card}>
        <View style={styles.logoRow}>
          <Text style={[styles.appName, { fontFamily: 'Pacifico_400Regular' }]}>
            Lumra
          </Text>
        </View>

        <Text style={styles.subtitle}>Care made simple</Text>

        <TouchableOpacity
          style={styles.primaryButton}
          onPress={() => navigation.navigate('Login')}
        >
          <Text style={styles.primaryText}>Login</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.secondaryButton}
          onPress={() => navigation.navigate('RoleSelect')}
        >
          <Text style={styles.secondaryText}>Signup</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    backgroundColor: '#f7f3f0', // subtle beige
    alignItems: 'center',
    justifyContent: 'center',
    padding: 24,
  },
  card: {
    width: '100%',
    maxWidth: 420,
    backgroundColor: '#fff',
    borderRadius: 14,
    paddingVertical: 36,
    paddingHorizontal: 28,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOpacity: 0.05,
    shadowRadius: 10,
    elevation: 3,
  },
  logoRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  appName: {
    fontSize: 48,
    letterSpacing: 2,
    color: '#4b413c',
  },
  subtitle: {
    marginTop: 4,
    marginBottom: 24,
    color: '#6a615a',
    fontSize: 14,
  },
  primaryButton: {
    width: '80%',
    backgroundColor: '#c8b39d', // beige button
    paddingVertical: 14,
    borderRadius: 10,
    alignItems: 'center',
    marginBottom: 12,
  },
  primaryText: {
    color: '#2b2520',
    fontSize: 16,
    fontWeight: '600',
  },
  secondaryButton: {
    width: '80%',
    backgroundColor: '#d1c2b0', // lighter beige
    paddingVertical: 14,
    borderRadius: 10,
    alignItems: 'center',
  },
  secondaryText: {
    color: '#2b2520',
    fontSize: 16,
    fontWeight: '600',
  },
});

export default LandingPage;
// ...existing code...