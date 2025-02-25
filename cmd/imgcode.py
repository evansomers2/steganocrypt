#!/usr/bin/env python3

import hashlib
import numpy as np
from PIL import Image
import os
import random
import argparse

def generate_color_map(password):
	""" Generate a color map using the password as a seed. """
	hash_object = hashlib.sha256(password.encode())
	password_hash = hash_object.digest()
	
	color_map = {}
	for i in range(26):
		r = (password_hash[i] + i) % 256
		g = (password_hash[(i + 1) % len(password_hash)] + i) % 256
		b = (password_hash[(i + 2) % len(password_hash)] + i) % 256
		color_map[chr(65 + i)] = (r, g, b)
		
	# Explicitly map space character to a unique color (e.g., black)
	color_map[' '] = (0, 0, 0)
	
	return color_map

def encode_text_to_image(text, password, img_size=(100, 100)):
	""" Encode a text message into an image using a password. """
	color_map = generate_color_map(password)
	
	# Prepare the text
	text = text.upper()
	
	# Create a list of pixel colors based on the text
	pixels = []
	for char in text:
		if char.isalpha() or char == ' ':  # Encode both letters and spaces
			pixels.append(color_map[char])
		
	# Fill the rest of the pixels with random colors (filler)
	grid_size = img_size[0] * img_size[1]
	while len(pixels) < grid_size:
		pixels.append(tuple(random.randint(0, 255) for _ in range(3)))
		
	# Convert the list of pixels to a NumPy array and reshape it
	pixels_array = np.array(pixels, dtype=np.uint8).reshape(img_size[1], img_size[0], 3)
	
	# Create and save the image
	img = Image.fromarray(pixels_array)
	img.save("encoded_message.png")
	print("Message encoded and saved as 'encoded_message.png'")
	
def decode_image_to_text(image_path, password):
	""" Decode the image back into the original text using a password. """
	color_map = generate_color_map(password)
	reverse_color_map = {v: k for k, v in color_map.items()}
	
	img = Image.open(image_path)
	img_array = np.array(img)
	
	# Extract the encoded letters from the image pixels, ignoring filler pixels
	decoded_text = []
	for row in img_array:
		for pixel in row:
			if tuple(pixel) in reverse_color_map:  # Only map valid colors
				decoded_text.append(reverse_color_map[tuple(pixel)])
			
	return ''.join(decoded_text).strip()

def main():
	parser = argparse.ArgumentParser(description="Encode/Decode messages to/from an image using a password.")
	
	# Arguments for encoding
	parser.add_argument("-e", "--encode", type=str, help="Text message to encode")
	parser.add_argument("-d", "--decode", type=str, help="Image path to decode")
	parser.add_argument("-p", "--password", type=str, required=True, help="Password for encoding/decoding")
	
	args = parser.parse_args()
	
	if args.encode:
		# Encoding mode
		encode_text_to_image(args.encode, args.password)
		
	elif args.decode:
		# Decoding mode
		if not os.path.exists(args.decode):
			print("Error: File not found.")
		else:
			decoded_text = decode_image_to_text(args.decode, args.password)
			print(f"Decoded text: {decoded_text}")
			
	else:
		print("Error: You must specify either -e (encode) or -d (decode).")
		
if __name__ == "__main__":
	main()
	