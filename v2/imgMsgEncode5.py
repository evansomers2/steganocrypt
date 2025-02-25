#!/usr/bin/env python3
# added comments

import hashlib  # Import hashlib for generating hashes
import numpy as np  # Import numpy for handling image data arrays
from PIL import Image, ImageTk  # Import PIL for image handling and conversion
import random  # Import random for generating random positions
import tkinter as tk  # Import tkinter for GUI elements
from tkinter import filedialog, messagebox  # Import dialog boxes and messageboxes
from tkinter import scrolledtext  # Import scrolledtext for displaying large text
from tkinter import ttk  # Import ttk for styled widgets

def generate_color_for_char_and_index(char, index, password):
	"""Generate a unique color for each character occurrence using the password."""
	# Combine the password, character, and its index into a single string
	hash_input = f"{password}{char}{index}".encode('utf-8')
	# Create a SHA256 hash from the combined string
	hash_object = hashlib.sha256(hash_input)
	hash_digest = hash_object.digest()
	# Return the least significant bit (LSB) of the first three hash bytes as RGB color values
	return hash_digest[0] % 2, hash_digest[1] % 2, hash_digest[2] % 2  # Use only LSB

def encode_text_to_image(text, password, img_path, debug=False):
	"""Encode text into an existing image's LSBs while preserving transparency if present."""
	img = Image.open(img_path)  # Open the image from the provided path
	# If the image is not already in RGB or RGBA, convert it
	if img.mode not in ["RGB", "RGBA"]:
		img = img.convert("RGB")
	pixels = np.array(img)  # Convert the image into a numpy array of pixels
	img_size = pixels.shape[0], pixels.shape[1]  # Get image dimensions
	message_length = len(text)  # Get the length of the message to encode
	binary_length = format(message_length, '032b')  # Convert the message length to a 32-bit binary string
	binary_message = binary_length + ''.join([format(ord(char), '08b') for char in text])  # Convert each character to binary
	pixel_positions = generate_pixel_positions(img_size, password, len(binary_message))  # Generate pixel positions to embed the message
	# Iterate through the binary message and embed each bit into the image
	for i, bit in enumerate(binary_message):
		pos = pixel_positions[i]  # Get the pixel position for this bit
		row = pos // img_size[1]  # Calculate the row position from the pixel index
		col = pos % img_size[1]  # Calculate the column position
		channel = i % 3  # Cycle through RGB channels (don't modify alpha)
		# Modify the LSB of the selected pixel channel to encode the bit
		pixels[row, col, channel] = (pixels[row, col, channel] & 0xFE) | int(bit)
	encoded_img = Image.fromarray(pixels)  # Convert the modified numpy array back to an image
	encoded_img.save('encoded_message.png')  # Save the encoded image
	return 'encoded_message.png', encoded_img  # Return the path and the encoded image object

def generate_pixel_positions(img_size, password, message_length):
	"""Generate a list of random pixel positions to store the encoded message."""
	total_pixels = img_size[0] * img_size[1]  # Calculate total number of pixels in the image
	hash_object = hashlib.sha256(password.encode())  # Generate a hash of the password for randomness
	password_hash = hash_object.digest()  # Get the byte digest of the hash
	random.seed(password_hash)  # Use the password hash as a seed for randomness
	all_positions = list(range(total_pixels))  # List all pixel indices
	random.shuffle(all_positions)  # Shuffle the list of pixel indices
	return all_positions[:message_length]  # Return the first 'message_length' positions

def show_loading_message(message):
	"""Display a modal loading message during processing."""
	loading = tk.Toplevel(root)  # Create a new top-level window for the loading message
	loading.title("Please Wait")  # Set the title of the loading window
	tk.Label(loading, text=message, padx=20, pady=20).pack()  # Add a label with the loading message
	loading.geometry("300x100")  # Set the window size
	loading.transient(root)  # Make the loading window transient (stays above main window)
	loading.grab_set()  # Prevent interaction with other windows while loading
	root.update()  # Force update to display the window immediately
	return loading  # Return the loading window

def encode_action():
	"""Handle the action to encode a message into an image."""
	text = text_entry.get()  # Get the text entered by the user
	password = encode_password_entry.get()  # Get the password entered by the user
	# Ensure text, password, and image path are provided
	if not text or not password or not selected_encode_image_path:
		messagebox.showerror("Error", "Please provide message, password, and image.")
		return
	# Display a loading message before encoding starts
	loading_window = show_loading_message("Encoding in progress, please wait...")
	debug_mode = debug_var.get()  # Get the debug mode setting
	file_path, img = encode_text_to_image(text, password, selected_encode_image_path, debug=debug_mode)  # Encode the text
	loading_window.destroy()  # Remove the loading window
	messagebox.showinfo("Success", f"Message encoded and saved as {file_path}")  # Inform the user of success
	display_image(img)  # Optionally, display the encoded image
	
def choose_encode_image_action():
	"""Prompt the user to choose an image for encoding."""
	global selected_encode_image_path
	selected_encode_image_path = filedialog.askopenfilename(
		title="Select Image for Encoding", 
		filetypes=[("Image Files", "*.png;*.jpg;*.jpeg"), ("PNG Files", "*.png"), ("JPEG Files", "*.jpg;*.jpeg")]
	)  # Open file dialog to choose an image
	if selected_encode_image_path:
		encode_image_path_label.config(text=f"Selected Image: {selected_encode_image_path}")  # Update the label with the selected image path
		
root = tk.Tk()  # Create the main window
root.title("Message Encoder/Decoder")  # Set the window title
notebook = ttk.Notebook(root)  # Create a notebook (tabbed) interface
notebook.grid(row=0, column=0, padx=10, pady=10)  # Add notebook to the window
encode_tab = ttk.Frame(notebook)  # Create a tab for encoding
notebook.add(encode_tab, text="Encode")  # Add the encode tab to the notebook

# Create and place various GUI elements (labels, entries, buttons) for encoding
text_label = tk.Label(encode_tab, text="Message to Encode:")
text_label.grid(row=0, column=0, padx=10, pady=5)
text_entry = tk.Entry(encode_tab, width=50)
text_entry.grid(row=0, column=1, padx=10, pady=5)
encode_password_label = tk.Label(encode_tab, text="Password:")
encode_password_label.grid(row=1, column=0, padx=10, pady=5)
encode_password_entry = tk.Entry(encode_tab, width=50, show="*")
encode_password_entry.grid(row=1, column=1, padx=10, pady=5)
debug_var = tk.BooleanVar()
debug_checkbox = tk.Checkbutton(encode_tab, text="Debug Mode", variable=debug_var)
debug_checkbox.grid(row=2, column=0, columnspan=2, pady=5)
choose_image_button = tk.Button(encode_tab, text="Choose Image", command=choose_encode_image_action)
choose_image_button.grid(row=3, column=0, columnspan=2, pady=5)
encode_image_path_label = tk.Label(encode_tab, text="Selected Image: None")
encode_image_path_label.grid(row=4, column=0, columnspan=2, pady=5)
encode_button = tk.Button(encode_tab, text="Encode", command=encode_action)
encode_button.grid(row=5, column=0, columnspan=2, pady=10)

selected_encode_image_path = None  # Initialize the selected image path as None

def decode_text_from_image(password, img_path, debug=False):
	"""Decode text from an image's LSBs using the provided password."""
	img = Image.open(img_path)  # Open the image from the provided path
	# If the image is not in RGB or RGBA, convert it
	if img.mode not in ["RGB", "RGBA"]:
		img = img.convert("RGB")
	pixels = np.array(img)  # Convert the image into a numpy array
	img_size = pixels.shape[0], pixels.shape[1]  # Get image dimensions
	pixel_positions = generate_pixel_positions(img_size, password, img_size[0] * img_size[1] * 3)  # Generate pixel positions
	binary_length = ''
	# Extract the first 32 bits for the message length
	for i in range(32):
		pos = pixel_positions[i]
		row = pos // img_size[1]
		col = pos % img_size[1]
		channel = i % 3
		binary_length += str(pixels[row, col, channel] & 0x01)  # Get LSB of pixel channel
	message_length = int(binary_length, 2)  # Convert binary length to an integer
	binary_message = ''
	# Extract the message bits based on the calculated message length
	for i in range(32, 32 + message_length * 8):
		pos = pixel_positions[i]
		row = pos // img_size[1]
		col = pos % img_size[1]
		channel = i % 3
		binary_message += str(pixels[row, col, channel] & 0x01)  # Get LSB of pixel channel
	# Convert the binary message back into text
	message = ''.join([chr(int(binary_message[i:i+8], 2)) 
						for i in range(0, len(binary_message), 8)])
	return message  # Return the decoded message

def decode_action():
	"""Handle the action to decode a message from an image."""
	password = decode_password_entry.get()  # Get the password entered by the user
	# Ensure password and image path are provided
	if not password or not selected_decode_image_path:
		messagebox.showerror("Error", "Please provide password and encoded image.")
		return
	# Display a loading message before decoding starts
	loading_window = show_loading_message("Decoding in progress, please wait...")
	debug_mode = debug_var.get()  # Get the debug mode setting
	try:
		message = decode_text_from_image(password, selected_decode_image_path, debug=debug_mode)  # Decode the message
	except IndexError:
		loading_window.destroy()  # Remove the loading window if decoding fails
		messagebox.showerror("Error", "Decoding failed: Incorrect password or corrupted image.")
		return
	loading_window.destroy()  # Remove the loading window after decoding completes
	# Create a new window to display the decoded message
	decoded_window = tk.Toplevel(root)
	decoded_window.title("Decoded Message")
	decoded_window.geometry("500x300")  # Set a fixed window size, or make it resizable
	
	# Add a ScrolledText widget to display the message
	text_widget = scrolledtext.ScrolledText(decoded_window, wrap=tk.WORD, width=60, height=15)
	text_widget.insert(tk.END, message)  # Insert the decoded message
	text_widget.config(state=tk.DISABLED)  # Make the widget read-only
	text_widget.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
	
	decoded_window.mainloop()  # Start the main loop for the decoded window
	
def choose_decode_image_action():
	"""Prompt the user to choose an image for decoding."""
	global selected_decode_image_path
	selected_decode_image_path = filedialog.askopenfilename(
		title="Select Encoded Image", 
		filetypes=[("Image Files", "*.png;*.jpg;*.jpeg"), ("PNG Files", "*.png"), ("JPEG Files", "*.jpg;*.jpeg")]
	)  # Open file dialog to choose an image
	if selected_decode_image_path:
		decode_image_path_label.config(text=f"Selected Image: {selected_decode_image_path}")  # Update the label with the selected image path
		
decode_tab = ttk.Frame(notebook)  # Create a tab for decoding
notebook.add(decode_tab, text="Decode")  # Add the decode tab to the notebook

# Create and place various GUI elements (labels, entries, buttons) for decoding
decode_password_label = tk.Label(decode_tab, text="Password:")
decode_password_label.grid(row=0, column=0, padx=10, pady=5)
decode_password_entry = tk.Entry(decode_tab, width=50, show="*")
decode_password_entry.grid(row=0, column=1, padx=10, pady=5)
choose_decode_image_button = tk.Button(decode_tab, text="Choose Encoded Image", command=choose_decode_image_action)
choose_decode_image_button.grid(row=1, column=0, columnspan=2, pady=5)
decode_image_path_label = tk.Label(decode_tab, text="Selected Image: None")
decode_image_path_label.grid(row=2, column=0, columnspan=2, pady=5)
decode_button = tk.Button(decode_tab, text="Decode", command=decode_action)
decode_button.grid(row=3, column=0, columnspan=2, pady=10)

root.mainloop()  # Run the main event loop
