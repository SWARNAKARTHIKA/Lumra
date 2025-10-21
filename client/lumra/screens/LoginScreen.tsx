// ...existing code...
import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  Alert,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { RootStackParamList } from '../App';

type NavProp = NativeStackNavigationProp<RootStackParamList, 'Login'>;

const LoginScreen: React.FC = () => {
  const navigation = useNavigation<NavProp>();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleLogin = () => {
    if (!username.trim() || !password) {
      Alert.alert('Validation', 'Please enter username and password.');
      return;
    }
    setSubmitting(true);
    // simulate login
    setTimeout(() => {
      setSubmitting(false);
      // on success navigate to Landing (or change to desired route)
      navigation.navigate('Landing');
    }, 700);
  };

  return (
    <KeyboardAvoidingView
      style={styles.screen}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      <View style={styles.card}>
        <Text style={styles.title}>Welcome back</Text>

        <TextInput
          style={styles.input}
          placeholder="Username or email"
          value={username}
          onChangeText={setUsername}
          autoCapitalize="none"
          keyboardType="email-address"
          placeholderTextColor="#8b8580"
        />

        <TextInput
          style={styles.input}
          placeholder="Password"
          value={password}
          onChangeText={setPassword}
          secureTextEntry
          placeholderTextColor="#8b8580"
        />

        <TouchableOpacity
          style={[styles.button, submitting && styles.buttonDisabled]}
          onPress={handleLogin}
          disabled={submitting}
        >
          <Text style={styles.buttonText}>{submitting ? 'Signing in...' : 'Login'}</Text>
        </TouchableOpacity>

        <TouchableOpacity onPress={() => navigation.navigate('RoleSelect')}>
          <Text style={styles.link}>Create an account</Text>
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    backgroundColor: '#f7f3f0',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 24,
  },
  card: {
    width: '100%',
    maxWidth: 420,
    backgroundColor: '#fff',
    borderRadius: 12,
    paddingVertical: 32,
    paddingHorizontal: 20,
    alignItems: 'center',
    elevation: 3,
  },
  title: {
    fontSize: 22,
    color: '#4b413c',
    fontWeight: '700',
    marginBottom: 18,
  },
  input: {
    width: '90%',
    backgroundColor: '#faf7f5',
    borderRadius: 10,
    paddingVertical: 12,
    paddingHorizontal: 14,
    marginVertical: 8,
    color: '#2b2520',
    elevation: 1,
  },
  button: {
    width: '90%',
    backgroundColor: '#c8b39d',
    paddingVertical: 14,
    borderRadius: 10,
    alignItems: 'center',
    marginTop: 14,
  },
  buttonDisabled: {
    opacity: 0.7,
  },
  buttonText: {
    color: '#2b2520',
    fontSize: 16,
    fontWeight: '600',
  },
  link: {
    marginTop: 12,
    color: '#6a615a',
    textDecorationLine: 'underline',
  },
});

export default LoginScreen;
// ...existing code...