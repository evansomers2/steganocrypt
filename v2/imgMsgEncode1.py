#!/usr/bin/env python3

import hashlib
import numpy as np
from PIL import Image, ImageTk
import random
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import scrolledtext
from tkinter import ttk

def generate_color_for_char_and_index(char, index, password):
    """ Generate a unique color for each character occurrence using the password. """
    hash_input = f"{password}{char}{index}".encode('utf-8')
    hash_object = hashlib.sha256(hash_input)
    hash_digest = hash_object.digest()
    return hash_digest[0] % 2, hash_digest[1] % 2, hash_digest[2] % 2  # Use only LSB

def encode_text_to_image(text, password, img_path, debug=False):
    """ Encode text into an existing image's LSBs. """
    img = Image.open(img_path).convert('RGB')
    pixels = np.array(img)
    img_size = pixels.shape[0], pixels.shape[1]
    message_length = len(text)
    binary_length = format(message_length, '032b')  # Store length as 32-bit binary
    binary_message = binary_length + ''.join([format(ord(char), '08b') for char in text])  # Full binary message
    pixel_positions = generate_pixel_positions(img_size, password, len(binary_message))
    for i, bit in enumerate(binary_message):
        pos = pixel_positions[i]
        row = pos // img_size[1]
        col = pos % img_size[1]
        channel = i % 3
        pixels[row, col, channel] = (pixels[row, col, channel] & 0xFE) | int(bit)  # Set LSB
    encoded_img = Image.fromarray(pixels)
    encoded_img.save('encoded_message.png')
    return 'encoded_message.png', encoded_img
    """ Encode text into an existing image's LSBs. """
    img = Image.open(img_path).convert('RGB')
    pixels = np.array(img)
    img_size = pixels.shape[0], pixels.shape[1]
    message_length = len(text)
    pixel_positions = generate_pixel_positions(img_size, password, message_length)
    
    for i, char in enumerate(text):
        color_bits = generate_color_for_char_and_index(char, i, password)
        pos = pixel_positions[i]
        row = pos // img_size[1]
        col = pos % img_size[1]
        for j in range(3):  # RGB channels
            pixels[row, col, j] = (pixels[row, col, j] & 0xFE) | color_bits[j]
    
    encoded_img = Image.fromarray(pixels)
    encoded_img.save('encoded_message.png')
    return 'encoded_message.png', encoded_img

def generate_pixel_positions(img_size, password, message_length):
    total_pixels = img_size[0] * img_size[1]
    hash_object = hashlib.sha256(password.encode())
    password_hash = hash_object.digest()
    random.seed(password_hash)
    all_positions = list(range(total_pixels))
    random.shuffle(all_positions)
    return all_positions[:message_length]

def encode_action():
    text = text_entry.get()
    password = encode_password_entry.get()
    if not text or not password or not selected_encode_image_path:
        messagebox.showerror("Error", "Please provide message, password, and image.")
        return
    debug_mode = debug_var.get()
    file_path, img = encode_text_to_image(text, password, selected_encode_image_path, debug=debug_mode)
    messagebox.showinfo("Success", f"Message encoded and saved as {file_path}")
    display_image(img)

def choose_encode_image_action():
    global selected_encode_image_path
    selected_encode_image_path = filedialog.askopenfilename(title="Select Image for Encoding", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg"), ("PNG Files", "*.png"), ("JPEG Files", "*.jpg;*.jpeg")])
    if selected_encode_image_path:
        encode_image_path_label.config(text=f"Selected Image: {selected_encode_image_path}")

root = tk.Tk()
root.title("Message Encoder/Decoder")
notebook = ttk.Notebook(root)
notebook.grid(row=0, column=0, padx=10, pady=10)
encode_tab = ttk.Frame(notebook)
notebook.add(encode_tab, text="Encode")
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
image_label = tk.Label(encode_tab)
image_label.grid(row=6, column=0, columnspan=2, pady=10)
selected_encode_image_path = None
def decode_text_from_image(password, img_path, debug=False):
    """ Decode text from an image's LSBs using the provided password. """
    img = Image.open(img_path).convert('RGB')
    pixels = np.array(img)
    img_size = pixels.shape[0], pixels.shape[1]
    pixel_positions = generate_pixel_positions(img_size, password, img_size[0] * img_size[1] * 3)  # Get all positions
    binary_length = ''
    for i in range(32):  # First 32 bits for length
        pos = pixel_positions[i]
        row = pos // img_size[1]
        col = pos % img_size[1]
        channel = i % 3
        binary_length += str(pixels[row, col, channel] & 0x01)
    message_length = int(binary_length, 2)  # Convert to integer
    binary_message = ''
    for i in range(32, 32 + message_length * 8):  # Message bits
        pos = pixel_positions[i]
        row = pos // img_size[1]
        col = pos % img_size[1]
        channel = i % 3
        binary_message += str(pixels[row, col, channel] & 0x01)
    message = ''.join([chr(int(binary_message[i:i+8], 2)) for i in range(0, len(binary_message), 8)])  # Decode to text
    return message
    img = Image.open(img_path).convert('RGB')
    pixels = np.array(img)
    img_size = pixels.shape[0], pixels.shape[1]
    pixel_positions = generate_pixel_positions(img_size, password, len(pixels) * 3)
    decoded_chars = []
    for i, pos in enumerate(pixel_positions):
        row = pos // img_size[1]
        col = pos % img_size[1]
        color_bits = [(pixels[row, col, j] & 0x01) for j in range(3)]
        decoded_chars.append(str(color_bits[0]) + str(color_bits[1]) + str(color_bits[2]))
    binary_string = ''.join(decoded_chars)
    message = ''.join([chr(int(binary_string[i:i+8], 2)) for i in range(0, len(binary_string), 8)])
    return message


def decode_action():
    password = decode_password_entry.get()
    if not password or not selected_decode_image_path:
        messagebox.showerror("Error", "Please provide password and encoded image.")
        return
    debug_mode = debug_var.get()
    try:
        message = decode_text_from_image(password, selected_decode_image_path, debug=debug_mode)
    except IndexError:
        messagebox.showerror("Error", "Decoding failed: Incorrect password or corrupted image.")
        return
    messagebox.showinfo("Decoded Message", f"Message: {message}")


def choose_decode_image_action():
    global selected_decode_image_path
    selected_decode_image_path = filedialog.askopenfilename(title="Select Encoded Image", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg"), ("PNG Files", "*.png"), ("JPEG Files", "*.jpg;*.jpeg")])
    if selected_decode_image_path:
        decode_image_path_label.config(text=f"Selected Image: {selected_decode_image_path}")


decode_tab = ttk.Frame(notebook)
notebook.add(decode_tab, text="Decode")
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

root.mainloop()
