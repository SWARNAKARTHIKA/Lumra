import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { RootStackParamList } from '../App';

export default function OTPScreen() {
  const nav = useNavigation<NativeStackNavigationProp<RootStackParamList>>();
  const [otp, setOtp] = useState('');

  return (
    <View style={s.container}>
      <Text style={s.title}>Enter OTP</Text>
      <TextInput
        placeholder="4-digit OTP"
        keyboardType="numeric"
        style={s.input}
        maxLength={4}
        value={otp}
        onChangeText={setOtp}
      />
      <TouchableOpacity style={s.btn}>
        <Text style={s.btntxt}>Verify</Text>
      </TouchableOpacity>
      <TouchableOpacity>
        <Text style={s.resend}>Resend OTP</Text>
      </TouchableOpacity>
    </View>
  );
}

const s = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#f6f1ed' },
  title: { fontSize: 24, fontWeight: '700', color: '#403a36', marginBottom: 20 },
  input: { width: '60%', backgroundColor: '#fff', borderRadius: 10, padding: 12, textAlign: 'center', fontSize: 18, letterSpacing: 5, marginBottom: 20, elevation: 1 },
  btn: { backgroundColor: '#c9b5a1', paddingVertical: 14, paddingHorizontal: 60, borderRadius: 10 },
  btntxt: { color: '#2b2520', fontWeight: '600', fontSize: 16 },
  resend: { marginTop: 15, color: '#6a5d52', fontSize: 14 },
});
