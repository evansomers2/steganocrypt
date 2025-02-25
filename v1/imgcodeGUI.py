import hashlib
import numpy as np
from PIL import Image, ImageTk
import os
import random
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import scrolledtext
from tkinter import ttk

def generate_color_map(password):
    """ Generate a color map using the password as a seed. Now includes all printable characters. """
    # List all printable characters (letters, numbers, punctuation, and space)
    printable_chars = [chr(i) for i in range(32, 127)]
    
    # Create a hash based on the password
    hash_object = hashlib.sha256(password.encode())
    password_hash = hash_object.digest()

    color_map = {}
    for i, char in enumerate(printable_chars):
        r = (password_hash[i % len(password_hash)] + i) % 256
        g = (password_hash[(i + 1) % len(password_hash)] + i) % 256
        b = (password_hash[(i + 2) % len(password_hash)] + i) % 256
        color_map[char] = (r, g, b)
    print(color_map)
    return color_map

def encode_text_to_image(text, password, img_size=(100, 100)):
    """ Encode a text message into an image using a password. Now includes all printable characters. """
    color_map = generate_color_map(password)
    
    # Prepare the text
    text = text
    
    # Create a list of pixel colors based on the text
    pixels = []
    for char in text:
        if char in color_map:  # Ensure all characters, including special characters, are encoded
            pixels.append(color_map[char])
    
    # Fill the rest of the pixels with random colors (filler)
    grid_size = img_size[0] * img_size[1]
    while len(pixels) < grid_size:
        pixels.append(tuple(random.randint(0, 255) for _ in range(3)))
    
    # Convert the list of pixels to a NumPy array and reshape it
    pixels_array = np.array(pixels, dtype=np.uint8).reshape(img_size[1], img_size[0], 3)
    
    # Create and save the image
    img_path = "encoded_message.png"
    img = Image.fromarray(pixels_array)
    img.save(img_path)
    
    return img_path, img

def decode_image_to_text(image_path, password):
    """ Decode the image back into the original text using a password. """
    color_map = generate_color_map(password)
    reverse_color_map = {v: k for k, v in color_map.items()}
    
    try:
        # Open the image correctly with PIL
        img = Image.open(image_path)
        img_array = np.array(img)
    
        # Extract the encoded letters from the image pixels, ignoring filler pixels
        decoded_text = []
    
        for row in img_array:
            for pixel in row:
                pixel_tuple = tuple(pixel)
                if pixel_tuple in reverse_color_map:  # Only map valid colors
                    decoded_text.append(reverse_color_map[pixel_tuple])
    
        return ''.join(decoded_text).strip()

    except Exception as e:
        print(f"Error decoding image: {e}")
        return ""

def encode_action():
    """ Handle encoding action from the GUI. """
    text = text_entry.get()
    password = encode_password_entry.get()
    
    if not text or not password:
        messagebox.showerror("Error", "Please provide both message and password.")
        return
    
    # Encode the message
    file_path, img = encode_text_to_image(text, password)
    messagebox.showinfo("Success", f"Message encoded and saved as {file_path}")
    
    # Display the image in the GUI (encode tab)
    display_image(img)

def display_image(img):
    """ Display the generated image in the Tkinter window. """
    img.thumbnail((250, 250))  # Resize for display
    img_tk = ImageTk.PhotoImage(img)
    
    # Update the label with the image
    image_label.config(image=img_tk)
    image_label.image = img_tk  # Keep a reference to the image

def choose_file_action():
    """ Handle file selection action from the GUI. """
    image_path = filedialog.askopenfilename(title="Select Encoded Image", filetypes=[("PNG files", "*.png")])
    if not image_path:
        return
    
    # Update the selected file path label
    file_path_label.config(text=f"Selected Image: {image_path}")
    global selected_image_path
    selected_image_path = image_path
    
    # Display the selected image in the decoding tab
    img = Image.open(image_path)
    display_decoded_image(img)

def display_decoded_image(img):
    """ Display the loaded image in the Decoding tab. """
    img.thumbnail((250, 250))  # Resize for display
    img_tk = ImageTk.PhotoImage(img)
    
    # Update the label with the image
    decode_image_label.config(image=img_tk)
    decode_image_label.image = img_tk  # Keep a reference to the image

def decode_action():
    """ Handle decoding action from the GUI. """
    password = decode_password_entry.get()
    
    if not password:
        messagebox.showerror("Error", "Please provide a password for decoding.")
        return
    
    if not selected_image_path:
        messagebox.showerror("Error", "Please select an image file first.")
        return
    
    # Decode the image
    decoded_text = decode_image_to_text(selected_image_path, password)
    
    # Display the decoded message
    output_text.delete(1.0, tk.END)
    output_text.insert(tk.END, f"Decoded Message: {decoded_text}")

# Set up the main window
root = tk.Tk()
root.title("Message Encoder/Decoder")

# Create Notebook (tabs)
notebook = ttk.Notebook(root)
notebook.grid(row=0, column=0, padx=10, pady=10)

# Encoding Tab
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

encode_button = tk.Button(encode_tab, text="Encode", command=encode_action)
encode_button.grid(row=2, column=0, columnspan=2, pady=10)

# Image display area for encoding
image_label = tk.Label(encode_tab)
image_label.grid(row=3, column=0, columnspan=2, pady=10)

# Decoding Tab
decode_tab = ttk.Frame(notebook)
notebook.add(decode_tab, text="Decode")

choose_file_button = tk.Button(decode_tab, text="Choose File", command=choose_file_action)
choose_file_button.grid(row=0, column=0, padx=10, pady=5)

file_path_label = tk.Label(decode_tab, text="Selected Image: None")
file_path_label.grid(row=0, column=1, padx=10, pady=5)

decode_password_label = tk.Label(decode_tab, text="Password for Decoding:")
decode_password_label.grid(row=1, column=0, padx=10, pady=5)

decode_password_entry = tk.Entry(decode_tab, width=50, show="*")
decode_password_entry.grid(row=1, column=1, padx=10, pady=5)

decode_button = tk.Button(decode_tab, text="Decode", command=decode_action)
decode_button.grid(row=2, column=0, columnspan=2, pady=10)

# Image display area for decoding
decode_image_label = tk.Label(decode_tab)
decode_image_label.grid(row=3, column=0, columnspan=2, pady=10)

output_label = tk.Label(decode_tab, text="Decoded Message:")
output_label.grid(row=4, column=0, padx=10, pady=5)

output_text = scrolledtext.ScrolledText(decode_tab, width=50, height=10)
output_text.grid(row=5, column=0, columnspan=2, padx=10, pady=5)

# Global variable for selected image path
selected_image_path = None

# Start the GUI loop
root.mainloop()