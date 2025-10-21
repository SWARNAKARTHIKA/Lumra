// ...existing code...
import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, ScrollView, StyleSheet, Alert } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { RootStackParamList } from '../App';

export default function GuardianSignupScreen() {
  const nav = useNavigation<NativeStackNavigationProp<RootStackParamList>>();
  const [form, setForm] = useState({ name: '', email: '', phone: '', password: '', confirm: '', address: '', relation: '' });

  const isComplete = Object.values(form).every((v) => v.trim() !== '');
  const passwordsMatch = form.password === form.confirm;

  const handleContinue = () => {
    if (!isComplete) {
      Alert.alert('Validation', 'Please fill all fields.');
      return;
    }
    if (!passwordsMatch) {
      Alert.alert('Validation', 'Passwords do not match.');
      return;
    }
    nav.navigate('OTP');
  };

  const fields = ['name','email','phone','password','confirm','address','relation'] as const;
  const secureFields = new Set(['password', 'confirm']);

  return (
    <ScrollView contentContainerStyle={s.container}>
      <Text style={s.title}>Guardian Details</Text>
      {fields.map((f) => (
        <TextInput
          key={f}
          placeholder={f.charAt(0).toUpperCase() + f.slice(1)}
          secureTextEntry={secureFields.has(f)}
          style={s.input}
          value={form[f as keyof typeof form]}
          onChangeText={(t) => setForm({ ...form, [f]: t })}
          autoCapitalize={f === 'email' ? 'none' : 'sentences'}
          keyboardType={f === 'email' ? 'email-address' : f === 'phone' ? 'phone-pad' : 'default'}
        />
      ))}
      <TouchableOpacity
        style={[s.btn, !isComplete || !passwordsMatch ? { opacity: 0.6 } : null]}
        onPress={handleContinue}
        disabled={!isComplete || !passwordsMatch}
      >
        <Text style={s.btntxt}>Continue</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

const s = StyleSheet.create({
  container: { flexGrow: 1, alignItems: 'center', justifyContent: 'center', backgroundColor: '#f7f3f0', paddingVertical: 30 },
  title: { fontSize: 24, fontWeight: '700', color: '#4b413c', marginBottom: 20 },
  input: { width: '80%', backgroundColor: '#fff', borderRadius: 10, padding: 12, marginVertical: 8, elevation: 1 },
  btn: { backgroundColor: '#c8b39d', paddingVertical: 14, paddingHorizontal: 60, borderRadius: 10, marginTop: 20 },
  btntxt: { color: '#2b2520', fontWeight: '600', fontSize: 16 },
});
// ...existing code...