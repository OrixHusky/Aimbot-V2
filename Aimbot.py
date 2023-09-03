import tkinter as tk
import ctypes
import threading
import time
import keyboard
import numpy as np
from PIL import ImageGrab
import pyautogui

# Global variables
target_color = (0, 0, 0)
hotkey_combination = ["shift"]  # Default hotkey
color_picking_mode = False
screenshot = None
cursor_smoothing = 5  # Default cursor smoothing value

# Load user32.dll for cursor movement
user32 = ctypes.windll.user32

# Function to capture the screen
def capture_screen():
    global screenshot
    screenshot = np.array(ImageGrab.grab())

# Initial screen capture
capture_screen()

# Function to find the closest location of the target color to the cursor
def find_closest_target_color():
    time.sleep(0.0001)  # Sleep for 1 millisecond (adjust as needed)

    # Use ctypes to call GetCursorPos and retrieve cursor position
    cursor_pos = ctypes.wintypes.POINT()
    user32.GetCursorPos(ctypes.byref(cursor_pos))

    search_radius = 50  # Adjust this value to limit the search area

    cursor_x, cursor_y = cursor_pos.x, cursor_pos.y

    # Define the search area boundaries
    left = max(0, cursor_x - search_radius)
    right = min(screenshot.shape[1], cursor_x + search_radius)
    top = max(0, cursor_y - search_radius)
    bottom = min(screenshot.shape[0], cursor_y + search_radius)

    min_distance = float('inf')
    closest_x, closest_y = None, None

    for x in range(left, right):
        for y in range(top, bottom):
            pixel_color = screenshot[y, x, :3]
            distance = np.linalg.norm(np.array(pixel_color) - np.array(target_color))
            if distance < min_distance:
                min_distance = distance
                closest_x, closest_y = x, y

    return closest_x, closest_y

# Function to set the target color
def set_target_color():
    global target_color
    target_color = (
        int(red_var.get()),
        int(green_var.get()),
        int(blue_var.get())
    )
    status_label.config(text=f"Target color set to {target_color}")

# Function to perform the action when the hotkey is pressed
def hotkey_action():
    capture_screen()  # Refresh the screenshot
    target_x, target_y = find_closest_target_color()

    # Move the cursor smoothly to the target position
    move_cursor_smooth(target_x, target_y)

    print("Hotkey activated")  # Debug line

# Function to listen for the hotkey combination
def hotkey_listener():
    keyboard.add_hotkey("shift", hotkey_action)
    keyboard.wait('esc')  # Wait for the 'esc' key to exit

# Function to handle color picker button click
def pick_color():
    global color_picking_mode
    color_picking_mode = not color_picking_mode
    if color_picking_mode:
        pick_color_button.config(text="Picking Color")
        pick_color_button.config(state=tk.DISABLED)  # Disable the button while picking
        monitor_mouse_thread = threading.Thread(target=monitor_mouse)
        monitor_mouse_thread.daemon = True
        monitor_mouse_thread.start()
    else:
        pick_color_button.config(text="Pick Color")
        pick_color_button.config(state=tk.NORMAL)  # Enable the button after picking

def monitor_mouse():
    while color_picking_mode:
        if keyboard.is_pressed('esc'):
            break
        if keyboard.is_pressed('shift'): # Exit picking mode if shift key is pressed
            pick_color()
            break
        if keyboard.is_pressed('ctrl'): # Capture the color when Ctrl is pressed
            x, y = pyautogui.position()
            on_color_picked(x, y)
            time.sleep(0.2)  # Sleep to prevent capturing multiple times while Ctrl is held

def on_color_picked(x, y):
    pixel_color = pyautogui.pixel(x, y)
    target_color = pixel_color[:3]  # Get the RGB values
    red_var.set(target_color[0])
    green_var.set(target_color[1])
    blue_var.set(target_color[2])
    status_label.config(text=f"Target color set to {target_color}")

# Function to move the cursor smoothly to a target position
def move_cursor_smooth(target_x, target_y):
    steps = cursor_smoothing

    for step in range(steps):
        # Calculate the next cursor position
        alpha = (step + 1) / steps
        cursor_pos = ctypes.wintypes.POINT()
        user32.GetCursorPos(ctypes.byref(cursor_pos))
        current_x = int((1 - alpha) * cursor_pos.x + alpha * target_x)
        current_y = int((1 - alpha) * cursor_pos.y + alpha * target_y)

        # Set the cursor position
        user32.SetCursorPos(current_x, current_y)

        time.sleep(0.001)  # Sleep for 1 millisecond (adjust as needed)

# Create the main window
window = tk.Tk()
window.title("Color Finder")

# Make the GUI stay on top of all other apps
window.attributes('-topmost', 1)

window.title("Color Finder")

# Create RGB input fields using StringVar variables
red_var = tk.StringVar()
green_var = tk.StringVar()
blue_var = tk.StringVar()

red_label = tk.Label(window, text="Red:")
red_entry = tk.Entry(window, textvariable=red_var)
green_label = tk.Label(window, text="Green:")
green_entry = tk.Entry(window, textvariable=green_var)
blue_label = tk.Label(window, text="Blue:")
blue_entry = tk.Entry(window, textvariable=blue_var)

# Create Set Color button
set_color_button = tk.Button(window, text="Set Color", command=set_target_color)

# Create color picker button
pick_color_button = tk.Button(window, text="Pick Color", command=pick_color)

# Create cursor smoothing slider
cursor_smoothing_label = tk.Label(window, text="Cursor Smoothing:")
cursor_smoothing_scale = tk.Scale(window, from_=1, to=20, orient=tk.HORIZONTAL, variable=cursor_smoothing)

# Create status label
status_label = tk.Label(window, text=f"Target color set to {target_color}")

# Layout widgets
red_label.grid(row=0, column=0)
red_entry.grid(row=0, column=1)
green_label.grid(row=1, column=0)
green_entry.grid(row=1, column=1)
blue_label.grid(row=2, column=0)
blue_entry.grid(row=2, column=1)
set_color_button.grid(row=3, column=0, columnspan=2)
pick_color_button.grid(row=4, column=0, columnspan=2)
cursor_smoothing_label.grid(row=5, column=0)
cursor_smoothing_scale.grid(row=5, column=1)
status_label.grid(row=6, column=0, columnspan=2)

# Create a thread for the hotkey listener
hotkey_thread = threading.Thread(target=hotkey_listener)
hotkey_thread.daemon = True
hotkey_thread.start()

# Start the GUI main loop
window.mainloop()
