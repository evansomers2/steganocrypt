const express = require('express');
const { createCanvas } = require('canvas');
const crypto = require('crypto');
const app = express();
const port = 3000;

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Helper functions to convert string to binary, and handle random seed generation
function stringToBinary(str) {
  return str.split('').map(char => char.charCodeAt(0).toString(2).padStart(8, '0')).join('');
}

function cyrb128(str) {
  let h1 = 1779033703, h2 = 3144134277, h3 = 1013904242, h4 = 2773480762;
  for (let i = 0, k; i < str.length; i++) {
    k = str.charCodeAt(i);
    h1 = h2 ^ Math.imul(h1 ^ k, 597399067);
    h2 = h3 ^ Math.imul(h2 ^ k, 2869860233);
    h3 = h4 ^ Math.imul(h3 ^ k, 951274213);
    h4 = h1 ^ Math.imul(h4 ^ k, 2716044179);
  }
  return [h1 >>> 0, h2 >>> 0, h3 >>> 0, h4 >>> 0];
}

function mulberry32(a) {
  return function() {
    let t = a += 0x6D2B79F5;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  }
}

function generatePixelOrder(totalPixels, seed) {
  let indices = Array.from({length: totalPixels}, (_, i) => i);
  let rand = mulberry32(seed);
  for (let i = indices.length - 1; i > 0; i--) {
    let j = Math.floor(rand() * (i + 1));
    [indices[i], indices[j]] = [indices[j], indices[i]];
  }
  return indices;
}

app.post('/generate-image', (req, res) => {
  console.log(req.body)
  const { message, password } = req.body;

  if (!message || !password) {
    return res.status(400).json({ error: 'Message and password are required' });
  }

  // Create header: 16 bits representing message length (in characters)
  if (message.length > 65535) {
    return res.status(400).json({ error: 'Message too long. Maximum length is 65535 characters.' });
  }
  let header = message.length.toString(2).padStart(16, '0');
  let messageBin = stringToBinary(message);
  let fullBinary = header + messageBin;
  let totalBits = fullBinary.length;

  // Set up canvas and get its context
  const canvas = createCanvas(100, 100);
  const ctx = canvas.getContext('2d');
  const width = canvas.width;
  const height = canvas.height;
  const totalPixels = width * height;

  if (totalBits > totalPixels) {
    return res.status(400).json({ error: 'Message too long for the canvas size. Use a smaller message or a larger canvas.' });
  }

  // Use the password to seed the PRNG for generating random colors and pixel order
  let seedArray = cyrb128(password);
  let seed = seedArray[0];
  let rand = mulberry32(seed);

  // Create image data and fill with random colors
  let imageData = ctx.createImageData(width, height);
  let data = imageData.data;
  for (let i = 0; i < totalPixels; i++) {
    data[i * 4] = Math.floor(rand() * 256);       // Red
    data[i * 4 + 1] = Math.floor(rand() * 256);   // Green
    data[i * 4 + 2] = Math.floor(rand() * 256);   // Blue
    data[i * 4 + 3] = 255;                        // Alpha (opaque)
  }

  // Generate a pseudo-random order of pixel indices using the same seed
  let pixelOrder = generatePixelOrder(totalPixels, seed);

  // Encode the binary data into the alpha channel using LSB encoding
  for (let i = 0; i < totalBits; i++) {
    let pixelIndex = pixelOrder[i];
    let bit = fullBinary[i];
    // Set alpha channel: 255 for bit '1', 254 for bit '0'
    data[pixelIndex * 4 + 3] = (bit === '0') ? 254 : 255;
  }

  // Draw the modified image data to the canvas
  ctx.putImageData(imageData, 0, 0);

  // Set the response header for PNG image and send the image buffer
  res.set('Content-Type', 'image/png');
  canvas.pngStream().pipe(res);
});

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});
