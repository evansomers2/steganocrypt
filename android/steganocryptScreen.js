import React, { useState } from 'react';
import { View, Text, TextInput, Button, Image, Alert } from 'react-native';
import * as FileSystem from 'expo-file-system';
import * as MediaLibrary from 'expo-media-library';

const SteganographyScreen = () => {
  const [message, setMessage] = useState('');
  const [password, setPassword] = useState('');
  const [image, setImage] = useState(null);
  const [loading, setLoading] = useState(false);

  const generateImage = async (message, password) => {
    const url = `http://192.168.2.13:3000/generate-image`;
  
    const data = {
      message: message,
      password: password
    };
  console.log(JSON.stringify(data))
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });
  
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      const blob = await response.blob();
      const fileUri = `${FileSystem.documentDirectory}downloaded-image.png`;
      // Convert blob to base64
      const base64Data = await new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onloadend = () => resolve(reader.result.split(',')[1]);
        reader.onerror = (error) => reject(error);
        reader.readAsDataURL(blob);
      });

      // Save the file to the phone
      await FileSystem.writeAsStringAsync(fileUri, base64Data, {
        encoding: FileSystem.EncodingType.Base64,
      });

      // Save the file to cache first
      await FileSystem.writeAsStringAsync(fileUri, base64Data, {
        encoding: FileSystem.EncodingType.Base64,
      });

      // Request permission to access media library
      const { status } = await MediaLibrary.requestPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Permission Denied', 'Cannot save image without permission.');
        return;
      }

      // Save to gallery
      const asset = await MediaLibrary.createAssetAsync(fileUri);
      await MediaLibrary.createAlbumAsync('Download', asset, false);
      // Handle the response as needed
    } catch (error) {
      console.error('Request failed', error);
    }
  };

  return (
    <View style={{ padding: 20 }}>
      <Text style={{ fontSize: 24, fontWeight: 'bold' }}>Steganography Image Generator</Text>

      {/* Message and Password Fields */}
      <View style={{ marginTop: 10 }}>
        <Text>Message:</Text>
        <TextInput
          value={message}
          onChangeText={(msg) => {
            setMessage(msg)
          }}
          placeholder="Enter message"
          multiline
          style={{
            height: 100,
            borderColor: '#ccc',
            borderWidth: 1,
            padding: 10,
            marginBottom: 10,
            textAlignVertical: 'top',
          }}
        />
      </View>

      <View style={{ marginTop: 10 }}>
        <Text>Password:</Text>
        <TextInput
          value={password}
          onChangeText={(event) => {
            setPassword(event)
          }}
          placeholder="Enter password"
          secureTextEntry
          style={{
            height: 40,
            borderColor: '#ccc',
            borderWidth: 1,
            padding: 10,
          }}
        />
      </View>

      {/* Generate Image Button */}
      <View style={{ marginTop: 20 }}>
        <Button
          title={loading ? 'Generating Image...' : 'Generate Image'}
          onPress={() => generateImage(message, password)}
          disabled={loading}
        />
      </View>

      {/* Display Image */}
      {image && (
        <View style={{ marginTop: 20 }}>
          <Text style={{ fontSize: 18, fontWeight: 'bold' }}>Generated Image</Text>
          <Image source={{ uri: image }} style={{ width: 100, height: 100, marginTop: 10 }} />
        </View>
      )}
    </View>
  );
};

export default SteganographyScreen;
