This app is a simple steganography tool built with React Native and Expo that allows users to hide and retrieve secret messages within PNG images. 
The core idea is to embed the message into the image by modifying the least significant bits of the alpha channel in each pixel. 
A user-provided password is used to generate a unique sequence of pixel indices, ensuring that the encoding process is randomized and reversible only with the correct password.

On the encoding side, the app generates a 100×100 pixel image filled with random colors. 
The message is first converted to binary and prefixed with a 16-bit header indicating its length. 
The app then embeds the header and message bits into the image by altering the LSB of selected pixel alpha channels, following a randomized order determined by the password. 
The modified image is then encoded as a PNG and can be saved or shared as needed.

For decoding, users select an image and enter the corresponding password. 
The app recreates the same pixel order using the password, extracts the header to determine the message length, 
and then reads the embedded bits to reconstruct the original message. 
This process ensures that only someone with the correct password can successfully decode and retrieve the hidden text.

Overall, the application serves as an educational example of basic steganography techniques, 
demonstrating how digital images can be used to securely hide information. 
While the approach is simple and primarily suited for learning purposes, 
it provides a foundation for exploring more advanced data-hiding and encryption methods.