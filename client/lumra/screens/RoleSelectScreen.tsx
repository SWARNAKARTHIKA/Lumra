import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { RootStackParamList } from '../App';

export default function RoleSelectScreen() {
  const nav = useNavigation<NativeStackNavigationProp<RootStackParamList>>();

  return (
    <View style={s.container}>
      <Text style={s.title}>Choose Your Role</Text>
      <TouchableOpacity style={s.btn} onPress={() => nav.navigate('GuardianSignup')}>
        <Text style={s.btntxt}>Guardian</Text>
      </TouchableOpacity>
      <TouchableOpacity style={s.btn} onPress={() => nav.navigate('ElderlySignup')}>
        <Text style={s.btntxt}>Elderly</Text>
      </TouchableOpacity>
    </View>
  );
}

const s = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#f4f0ec' },
  title: { fontSize: 26, fontWeight: '700', color: '#403b36', marginBottom: 40 },
  btn: { backgroundColor: '#d1c2b0', paddingVertical: 15, paddingHorizontal: 60, borderRadius: 12, marginVertical: 10 },
  btntxt: { fontSize: 18, color: '#2e2720', fontWeight: '600' },
});
