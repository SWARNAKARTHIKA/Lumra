import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import LandingPage from './screens/LandingPage';
import LoginScreen from './screens/LoginScreen';
import RoleSelectScreen from './screens/RoleSelectScreen';
import GuardianSignupScreen from './screens/GuardianSignupScreen';
import ElderlySignupScreen from './screens/ElderlySignupScreen';
import OTPScreen from './screens/OTPScreen';
import UserDetailsScreen from './screens/UserDetailsScreen';
import GuardianDashboard from './screens/GuardianDashboard';
import ElderlyDashboard from './screens/ElderlyDashboard';

export type RootStackParamList = {
  Landing: undefined;
  Login: undefined;
  RoleSelect: undefined;
  GuardianSignup: undefined;
  ElderlySignup: undefined;
  OTP: undefined;
  UserDetails: { message:string; userId: number; role: string};
   GuardianDashboard: { userId: number };
   ElderlyDashboard: { userId: number }; 
};

const Stack = createNativeStackNavigator<RootStackParamList>();


export default function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        <Stack.Screen name="Landing" component={LandingPage} />
        <Stack.Screen name="Login" component={LoginScreen} />
        <Stack.Screen name="RoleSelect" component={RoleSelectScreen} />
        <Stack.Screen name="GuardianSignup" component={GuardianSignupScreen} />
        <Stack.Screen name="ElderlySignup" component={ElderlySignupScreen} />
        <Stack.Screen name="OTP" component={OTPScreen} />
        <Stack.Screen name="UserDetails" component={UserDetailsScreen} />
        <Stack.Screen name="GuardianDashboard" component={GuardianDashboard} />
        <Stack.Screen name="ElderlyDashboard" component={ElderlyDashboard} />


      </Stack.Navigator>
    </NavigationContainer>
  );
}
