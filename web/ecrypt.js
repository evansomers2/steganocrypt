<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Test Encode Message</title>
</head>
<body>
  <script>
    /**
    * Generate a pseudorandom number generator (PRNG) based on a seed
    * @param {string} seed
    * @returns {function} PRNG function
    */
    function seedPRNG(seed) {
      let x = parseInt(seed.slice(0, 8), 16);
      return function () {
        x ^= x << 13;
        x ^= x >> 17;
        x ^= x << 5;
        return (x >>> 0) / 4294967296;
      };
    }
    
    /**
    * Encode the message into an image
    * @param {string} message - The message to encode
    * @param {string} password - The password for encoding
    * @returns {Promise<HTMLCanvasElement>} Promise resolving to a canvas with the encoded message
    */
    async function encodeMessage(message, password) {
      const canvas = document.createElement("canvas");
      canvas.width = 100;
      canvas.height = 100;
      const ctx = canvas.getContext("2d");
      const imageData = ctx.createImageData(100, 100);
      
      const hash = await hashPassword(password);
      const rng = seedPRNG(hash);
      
      // Convert message to binary
      const binaryMessage = Array.from(message).flatMap((char) =>
        char.charCodeAt(0).toString(2).padStart(8, "0").split("").map(Number)
      );
      
      // Add message length (16 bits for safety)
      const messageLength = message.length;
      const binaryLength = messageLength
      .toString(2)
      .padStart(16, "0")
      .split("")
      .map(Number);
      const binaryData = [...binaryLength, ...binaryMessage];
      
      // Generate shuffled pixel positions
      const positions = Array.from({ length: 10000 }, (_, i) => i);
      for (let i = positions.length - 1; i > 0; i--) {
        const j = Math.floor(rng() * (i + 1));
        [positions[i], positions[j]] = [positions[j], positions[i]];
      }
      
      // Encode the binary message into pixel data
      let dataIndex = 0;
      for (let i = 0; i < 10000; i++) {
        const pixelIndex = positions[i] * 4;
        
        if (dataIndex < binaryData.length) {
          // Encode message bit into the red channel (LSB)
          imageData.data[pixelIndex] = binaryData[dataIndex] ? 255 : 0;
          imageData.data[pixelIndex + 1] = 0; // Green (noise)
          imageData.data[pixelIndex + 2] = 0; // Blue (noise)
          imageData.data[pixelIndex + 3] = 255; // Alpha
          dataIndex++;
        } else {
          // Fill remaining pixels with noise
          imageData.data[pixelIndex] = Math.floor(rng() * 256);
          imageData.data[pixelIndex + 1] = Math.floor(rng() * 256);
          imageData.data[pixelIndex + 2] = Math.floor(rng() * 256);
          imageData.data[pixelIndex + 3] = 255; // Alpha
        }
      }
      
      ctx.putImageData(imageData, 0, 0);
      return canvas;
    }

    
    /**
    * Decode the message from an image
    * @param {ImageData} imageData - The ImageData to decode
    * @param {string} password - The password for decoding
    * @returns {Promise<string>} Decoded message
    */
    async function decodeMessage(imageData, password) {
      const hash = await hashPassword(password);
      const rng = seedPRNG(hash);
      
      // Generate shuffled pixel positions
      const positions = Array.from({ length: 10000 }, (_, i) => i);
      for (let i = positions.length - 1; i > 0; i--) {
        const j = Math.floor(rng() * (i + 1));
        [positions[i], positions[j]] = [positions[j], positions[i]];
      }
      
      // Extract binary data from pixel positions
      const binaryData = [];
      for (let i = 0; i < 10000; i++) {
        const pixelIndex = positions[i] * 4;
        const red = imageData.data[pixelIndex];
        binaryData.push(red === 255 ? 1 : 0);
      }
      
      // Decode message length (first 16 bits)
      const binaryLength = binaryData.slice(0, 16).join("");
      const messageLength = parseInt(binaryLength, 2);
      
      // Decode the message using the length
      const binaryMessage = binaryData.slice(16, 16 + messageLength * 8);
      const message = binaryMessage
      .join("")
      .match(/.{1,8}/g)
      .map((byte) => String.fromCharCode(parseInt(byte, 2)))
      .join("");
      
      return message;
    }

    async function hashPassword(password) {
      const encoder = new TextEncoder();
      const data = encoder.encode(password);
      const hashBuffer = await crypto.subtle.digest("SHA-256", data);
      return Array.from(new Uint8Array(hashBuffer))
      .map((byte) => byte.toString(16).padStart(2, "0"))
      .join("");
    }
    // Add the updated JavaScript code here
    async function test() {
      const message = "testing evan 1242u342748273482738472835yjgu23gt23g!";
      const password = "securepassword";
      
      // Encode the message
      const encodedCanvas = await encodeMessage(message, password);
      document.body.appendChild(encodedCanvas);
      
      // Decode the message
      const ctx = encodedCanvas.getContext("2d");
      const imageData = ctx.getImageData(0, 0, 100, 100);
      const decodedMessage = await decodeMessage(imageData, password);
      
      console.log("Decoded Message:", decodedMessage); // Should print: "Hello, world!"
    }
    
    // Call test function
    test();
  </script>
</body>
</html>
