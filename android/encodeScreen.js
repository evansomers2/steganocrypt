import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  Button,
  Image,
  StyleSheet,
  Alert,
  ScrollView,
} from 'react-native';
import * as FileSystem from 'expo-file-system';
import * as MediaLibrary from 'expo-media-library';
import UPNG from 'upng-js';

// --- Helper Functions ---

// Hash function (cyrb128) to generate four 32-bit seeds from a string.
const cyrb128 = (str) => {
  let h1 = 1779033703,
    h2 = 3144134277,
    h3 = 1013904242,
    h4 = 2773480762;
  for (let i = 0, k; i < str.length; i++) {
    k = str.charCodeAt(i);
    h1 = h2 ^ Math.imul(h1 ^ k, 597399067);
    h2 = h3 ^ Math.imul(h2 ^ k, 2869860233);
    h3 = h4 ^ Math.imul(h3 ^ k, 951274213);
    h4 = h1 ^ Math.imul(h4 ^ k, 2716044179);
  }
  return [h1 >>> 0, h2 >>> 0, h3 >>> 0, h4 >>> 0];
};

// Pseudo-random number generator seeded with a 32-bit integer.
const mulberry32 = (a) => {
  return function () {
    var t = a += 0x6D2B79F5;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
};

// Generate a randomized pixel order array based on the total pixels and a seed.
const generatePixelOrder = (totalPixels, seed) => {
  let indices = Array.from({ length: totalPixels }, (_, i) => i);
  let rand = mulberry32(seed);
  for (let i = indices.length - 1; i > 0; i--) {
    let j = Math.floor(rand() * (i + 1));
    [indices[i], indices[j]] = [indices[j], indices[i]];
  }
  return indices;
};

// Converts a text string to its binary representation (8 bits per character).
const stringToBinary = (str) => {
  let binary = '';
  for (let i = 0; i < str.length; i++) {
    let bin = str.charCodeAt(i).toString(2);
    binary += bin.padStart(8, '0');
  }
  return binary;
};

// Converts an ArrayBuffer to a Base64 string.
const arrayBufferToBase64 = async (buffer) => {
  let binary = '';
  const bytes = new Uint8Array(buffer);
  for (let i = 0; i < bytes.byteLength; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return btoa(binary);
};

// --- EncodeScreen Component ---

const EncodeScreen = () => {
  const [message, setMessage] = useState('');
  const [password, setPassword] = useState('');
  const [encodedImageUri, setEncodedImageUri] = useState(null);
  const [loading, setLoading] = useState(false);

  const width = 100;
  const height = 100;
  const totalPixels = width * height;

  const generateImage = async () => {
    if (!message || !password) {
      Alert.alert('Error', 'Please provide both a message and a password.');
      return;
    }
    setLoading(true);

    try {
      // Generate random RGB colors for each pixel
      const pixelData = new Uint8Array(totalPixels * 4);
      const seedArray = cyrb128(password);
      const rand = mulberry32(seedArray[1]);

      for (let i = 0; i < totalPixels; i++) {
        pixelData[i * 4] = Math.floor(rand() * 256);     // R
        pixelData[i * 4 + 1] = Math.floor(rand() * 256); // G
        pixelData[i * 4 + 2] = Math.floor(rand() * 256); // B
        pixelData[i * 4 + 3] = 254;                     // A (default even)
      }

      // Prepare header and message binary strings.
      const messageLength = message.length;
      if (messageLength > 65535) {
        Alert.alert('Error', 'Message is too long. Maximum length is 65,535 characters.');
        setLoading(false);
        return;
      }
      const headerBinary = messageLength.toString(2).padStart(16, '0');
      const messageBinary = stringToBinary(message);

      if (16 + messageBinary.length > totalPixels) {
        Alert.alert('Error', 'Message is too long for a 100x100 image.');
        setLoading(false);
        return;
      }

      const pixelOrder = generatePixelOrder(totalPixels, seedArray[0]);

      // --- Encode the Header ---
      for (let i = 0; i < 16; i++) {
        const pixelIndex = pixelOrder[i];
        const alphaIndex = pixelIndex * 4 + 3;
        const bit = parseInt(headerBinary[i], 10);
        pixelData[alphaIndex] = (pixelData[alphaIndex] & 0xFE) | bit;
      }

      // --- Encode the Message ---
      for (let i = 0; i < messageBinary.length; i++) {
        const pixelIndex = pixelOrder[16 + i];
        const alphaIndex = pixelIndex * 4 + 3;
        const bit = parseInt(messageBinary[i], 10);
        pixelData[alphaIndex] = (pixelData[alphaIndex] & 0xFE) | bit;
      }

      // --- Re-encode the Image as PNG ---
      const pngBuffer = UPNG.encode([pixelData.buffer], width, height, 0);
      const base64Encoded = await arrayBufferToBase64(pngBuffer);
      const imageUri = `data:image/png;base64,${base64Encoded}`;
      setEncodedImageUri(imageUri);
      Alert.alert('Success', 'Image generated with encoded message!');
    } catch (error) {
      console.error('Encoding Error:', error);
      Alert.alert('Error', 'An error occurred while generating the image.');
    }
    setLoading(false);
  };

  // Save the generated image to the device's gallery.
  const saveImage = async () => {
    if (!encodedImageUri) {
      Alert.alert('Error', 'No encoded image to save.');
      return;
    }
    try {
      const fileUri = `${FileSystem.cacheDirectory}encoded-image.png`;
      // Remove the URI header.
      const base64Data = encodedImageUri.split(',')[1];
      await FileSystem.writeAsStringAsync(fileUri, base64Data, {
        encoding: FileSystem.EncodingType.Base64,
      });
      const { status } = await MediaLibrary.requestPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Permission Denied', 'Cannot save image without permission.');
        return;
      }
      const asset = await MediaLibrary.createAssetAsync(fileUri);
      await MediaLibrary.createAlbumAsync('Encoded Images', asset, false);
      Alert.alert('Success', 'Encoded image saved to gallery!');
    } catch (error) {
      console.error('Save Error:', error);
      Alert.alert('Error', 'An error occurred while saving the image.');
    }
  };

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.title}>Encode Hidden Message</Text>
      <TextInput
        style={styles.input}
        placeholder="Enter Secret Message"
        value={message}
        onChangeText={setMessage}
        multiline
      />
      <TextInput
        style={styles.input}
        placeholder="Enter Password"
        value={password}
        onChangeText={setPassword}
        secureTextEntry
      />
      <Button
        title={loading ? 'Generating...' : 'Generate Image'}
        onPress={generateImage}
        disabled={loading}
      />
      {encodedImageUri && (
        <>
          <Text style={styles.subtitle}>Generated Image:</Text>
          <Image source={{ uri: encodedImageUri }} style={styles.image} />
          <Button title="Save Image" onPress={saveImage} />
        </>
      )}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flexGrow: 1,
    padding: 20,
    alignItems: 'center',
  },
  title: {
    fontSize: 24,
    textAlign: 'center',
    marginVertical: 10,
  },
  input: {
    width: '100%',
    borderWidth: 1,
    padding: 10,
    marginVertical: 10,
    borderRadius: 5,
  },
  image: {
    width: 200,
    height: 200,
    resizeMode: 'contain',
    marginVertical: 10,
  },
});

export default EncodeScreen;
