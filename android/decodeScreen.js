// DecodeScreen.js
import React, { useState } from 'react';
import { View, Text, TextInput, Button, Image, StyleSheet, Alert, ScrollView } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import UPNG from 'upng-js';

// Helper Functions
const cyrb128 = (str) => {
  let h1 = 1779033703, h2 = 3144134277, h3 = 1013904242, h4 = 2773480762;
  for (let i = 0, k; i < str.length; i++) {
      k = str.charCodeAt(i);
      h1 = h2 ^ Math.imul(h1 ^ k, 597399067);
      h2 = h3 ^ Math.imul(h2 ^ k, 2869860233);
      h3 = h4 ^ Math.imul(h3 ^ k, 951274213);
      h4 = h1 ^ Math.imul(h4 ^ k, 2716044179);
  }
  return [h1 >>> 0, h2 >>> 0, h3 >>> 0, h4 >>> 0];
};

const mulberry32 = (a) => {
  return function() {
    var t = a += 0x6D2B79F5;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  }
};

const generatePixelOrder = (totalPixels, seed) => {
  let indices = Array.from({ length: totalPixels }, (_, i) => i);
  let rand = mulberry32(seed);
  for (let i = indices.length - 1; i > 0; i--) {
    let j = Math.floor(rand() * (i + 1));
    [indices[i], indices[j]] = [indices[j], indices[i]];
  }
  return indices;
};

const binaryToString = (binStr) => {
  let text = '';
  for (let i = 0; i < binStr.length; i += 8) {
    let byte = binStr.substr(i, 8);
    text += String.fromCharCode(parseInt(byte, 2));
  }
  return text;
};

const DecodeScreen = () => {
  const [imageUri, setImageUri] = useState(null);
  const [password, setPassword] = useState('');
  const [decodedMessage, setDecodedMessage] = useState('');
  const [imageData, setImageData] = useState(null);

  const pickImage = async () => {
    let result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      quality: 1,
    });
    if (!result.canceled) {
      setImageUri(result.assets[0].uri);
        getImagePixelData(result.assets[0].uri).then(res => {
            setImageData(res.data)
        })
    }
  };

  async function getImagePixelData(uri) {
    try {
      // Fetch the image as an ArrayBuffer.
      const response = await fetch(uri);
      if (!response.ok) {
        throw new Error(`Network response was not ok, status: ${response.status}`);
      }
      const arrayBuffer = await response.arrayBuffer();
      console.log("ArrayBuffer byteLength:", arrayBuffer.byteLength);
  
      if (arrayBuffer.byteLength === 0) {
        throw new Error("Fetched ArrayBuffer is empty.");
      }
  
      // Decode the PNG image.
      const pngData = UPNG.decode(arrayBuffer);
  
      // Convert the decoded data to RGBA frames.
      const frames = UPNG.toRGBA8(pngData);
      if (!frames || frames.length === 0) {
        throw new Error("No frames decoded from PNG image.");
      }
      const pixelData = frames[0]; // For non-animated PNGs, only one frame is expected.
      console.log("Pixel data length:", pngData.data.length);
  
      const { width, height } = pngData;
      console.log("Width:", width, "Height:", height);
  
      // Check if pixelData length is as expected: width * height * 4
      if (pixelData.length !== width * height * 4) {
        console.warn("Unexpected pixel data length:", pixelData.length);
      }
      return { width, height, data: pngData.data };
    } catch (error) {
      console.error("Error fetching or decoding PNG image:", error);
      return null;
    }
  }

  const decodeMessage = async () => {
    if (!imageData || !password) {
      Alert.alert("Error", "Please provide both image data and a password.");
      return;
    }
  
    try {
      // Destructure the image data
      const width = 100;
      const height = 100;

      console.log("Image dimensions:", width, height);
    //   console.log("Pixel data length:", imageData);
  
      const totalPixels = width * height;
  
      // Generate the seed and pixel order from the provided password.
      const seedArray = cyrb128(password);
      const seed = seedArray[0];
      const pixelOrder = generatePixelOrder(totalPixels, seed);
  
      // Decode the header (first 16 pixels) to determine the message length.
      let headerBits = "";
      for (let i = 0; i < 16; i++) {
        const pixelIndex = pixelOrder[i];
        const alpha = imageData[pixelIndex * 4 + 3];
        headerBits += alpha % 2 === 0 ? "0" : "1";
      }
      const messageLength = parseInt(headerBits, 2);
      console.log("Message length (in bytes):", messageLength);
  
      // Calculate total bits for the actual message.
      const totalMessageBits = messageLength * 8;
      let messageBits = "";
  
      // Decode the message bits from the subsequent pixels.
      for (let i = 16; i < 16 + totalMessageBits; i++) {
        const pixelIndex = pixelOrder[i];
        const alpha = imageData[pixelIndex * 4 + 3];
        messageBits += alpha % 2 === 0 ? "0" : "1";
      }
  
      // Convert the binary string to a text message.
      const message = binaryToString(messageBits);
      console.log("Decoded Message:", message);
      Alert.alert("Decoded Message:", message);

      // You can now use your message (e.g., set it to state or return it)
      return message;
    } catch (error) {
      console.error("Decoding Error:", error);
      Alert.alert("Error", "An error occurred during decoding.");
    }
  };

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.title}>Decode Hidden Message</Text>
      <Button title="Pick Image" onPress={pickImage} />
      {imageUri && <Image source={{ uri: imageUri }} style={styles.image} />}
      <TextInput style={styles.input} placeholder="Enter Password" value={password} onChangeText={setPassword} secureTextEntry />
      <Button title="Decode" onPress={decodeMessage} />
      <Text style={styles.message}>{decodedMessage}</Text>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: { flexGrow: 1, padding: 20 },
  title: { fontSize: 24, textAlign: 'center', marginVertical: 10 },
  input: { borderWidth: 1, padding: 10, marginVertical: 10, borderRadius: 5 },
  image: { width: '100%', height: 300, resizeMode: 'contain', marginVertical: 10 },
  message: { marginVertical: 10, fontSize: 18, color: 'green' }
});

export default DecodeScreen;
