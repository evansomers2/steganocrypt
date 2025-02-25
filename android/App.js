import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import SteganographyScreen from './steganocryptScreen';
import DecodeScreen from './decodeScreen';
import EncodeScreen from './encodeScreen';

const Tab = createBottomTabNavigator();

export default function App() {
  return (
    <NavigationContainer>
      <Tab.Navigator>
        <Tab.Screen name="Download" component={EncodeScreen} />
        <Tab.Screen name="Decode" component={DecodeScreen} />
      </Tab.Navigator>
    </NavigationContainer>
  );
}
