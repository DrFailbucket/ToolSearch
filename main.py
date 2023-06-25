import json
import os
import shutil
import tkinter as tk
from collections import defaultdict
from tkinter import messagebox, filedialog, simpledialog

from PIL import Image, ImageTk

# TODO Making the Executable Program using:,
#  pyinstaller --add-data "image;image" --add-data "help;." --add-data "about;." --noconsole  main.py

# Global Variables
x = None
y = None
image_path_part = None


# TODO List"
# todo: Make the Program Automatically reloads the Image files when Added instead of to have Restart the Program
# fixme: Switch Image based on the Part Number
# todo: Save the last Used Image and load it at next Startup

# could be done via the Settings Menu Bar
# todo: Add Option to Display all Stored Part Numbers in a List,
#  make them Editable in the list, aka. "Edit","Add New","Delete"


# todo: Make a Usable Settings Menu
# todo: Revisit the Help_File aka How to Use


def save_coordinates(coordinates, image_path):
    try:
        with open('coordinates.json', 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        data = defaultdict(list)

    cords = data["coordinates"]
    found = False

    for cord in cords:
        if cord["number"] == coordinates["number"]:
            cord["x"] = coordinates["x"]
            cord["y"] = coordinates["y"]
            cord["image_path"] = image_path  # Store the image path
            found = True
            break

    if not found:
        coordinates["image_path"] = image_path  # Store the image path
        data["coordinates"].append(coordinates)

    with open('coordinates.json', 'w') as file:
        json.dump(data, file, indent=4)


def check_json(number):
    try:
        with open('coordinates.json', 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        data = defaultdict(list)

    if data == defaultdict(list):
        return False

    cords = data["coordinates"]

    for cord in cords:
        if cord["number"] == number:
            return True


def on_click(event):
    cord_x = event.x
    cord_y = event.y
    text_var = tk.StringVar()

    def ok():
        text = text_var.get()
        if text and photo_width is not None and photo_height is not None:
            # Calculate the photo coordinates based on the clicked position
            photo_x = cord_x * photo_width / canvas.winfo_width()
            photo_y = cord_y * photo_height / canvas.winfo_height()

            coordinates = {"number": text, 'x': photo_x, 'y': photo_y}

            if check_json(text):
                result = messagebox.askquestion("Confirmation",
                                                "This number already exists. Do you want to overwrite it?")
                if result == "yes":
                    save_coordinates(coordinates, canvas.image_path)  # Pass the image path

                    print(f"Clicked at coordinates: ({photo_x}, {photo_y})")
            else:
                save_coordinates(coordinates, canvas.image_path)
                print(f"Clicked at coordinates: ({photo_x}, {photo_y})")

        top.destroy()

    def cancel():
        top.destroy()

    top = tk.Toplevel(root)
    top.title("Edit Location")

    # Calculate the position to center the window on the screen
    top_width = 200
    top_height = 100
    screen_width = top.winfo_screenwidth()
    screen_height = top.winfo_screenheight()
    x_coordinate = (screen_width - top_width) // 2
    y_coordinate = (screen_height - top_height) // 2

    top.geometry(f"{top_width}x{top_height}+{x_coordinate}+{y_coordinate}")

    label = tk.Label(top, text="Please input part number", font=("Arial", 10))
    label.pack(pady=5)

    entry = tk.Entry(top, textvariable=text_var, font=("Arial", 10), width=20)
    entry.pack(pady=10)

    entry.focus_set()  # Set focus to the entry widget automatically

    button_frame = tk.Frame(top)
    button_frame.pack()

    ok_button = tk.Button(button_frame, text="OK", command=ok)
    ok_button.pack(side="left", padx=5)

    cancel_button = tk.Button(button_frame, text="Cancel", command=cancel)
    cancel_button.pack(side="left")

    top.transient(root)
    top.grab_set()
    root.wait_window(top)


def search_location():
    global x, y, image_path_part
    number = simpledialog.askstring("Search Location",
                                    "                             Enter Part Number:                             ")

    # Remove the last placed marker if any
    remove_last_marker()

    if check_json(number):
        with open('coordinates.json', 'r') as file:
            data = json.load(file)

        cords = data["coordinates"]
        found = False

        for cord in cords:
            if cord["number"] == number:
                x = cord["x"]
                y = cord["y"]
                image_path_part = cord["image_path"]
                found = True
                break

        if found:
            mark_position(x, y)  # Mark the position with a new marker
            # messagebox.showinfo("Search Result", f"Part Number: {number}\nX: {x}\nY: {y}")
        else:
            messagebox.showinfo("Search Result", f"No coordinates found for Part Number: {number}")
    else:
        messagebox.showinfo("Search Result", f"No coordinates found for Part Number: {number}")


def handle_image_loading():
    # FIXME: Try to load the last selected Image that is stored in the image_data.json
    # try:
    #     with open("image_data.json", "r") as file:
    #         image_data = json.load(file)
    #         last_image_path = image_data.get("last_image")
    #         if last_image_path and os.path.isfile(last_image_path):
    #             update_canvas_with_image(last_image_path)
    # except FileNotFoundError:
    #     pass
    # Set the image path using the image folder in the same directory as the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    image_folder = os.path.join(script_dir, 'image')
    image_files = []

    def get_image_files():
        return [file for file in os.listdir(image_folder) if file.lower().endswith((".png", ".jpg", ".jpeg", ".gif"))]

    def switch_image():
        # Check if there are images in the folder
        if not image_files:
            messagebox.showinfo("No Images", "No images found in the 'image' folder.")
            return

        # Get the current displayed image path
        current_image = canvas.image_path

        # Find the index of the current image in the image files list
        current_index = image_files.index(os.path.basename(current_image))

        # Calculate the index of the next image
        next_index = (current_index + 1) % len(image_files)

        # Get the path of the next image
        next_image_path = os.path.join(image_folder, image_files[next_index])

        # Update the canvas with the next image
        update_canvas_with_image(next_image_path)

        # Save the path of the next image to a JSON file
        image_data = {"last_image": next_image_path}
        with open("image_data.json", "w") as file:
            json.dump(image_data, file)

    # noinspection PyGlobalUndefined
    def update_canvas_with_image(new_image_path):
        # Load the image from the selected file
        image = Image.open(new_image_path)

        # Update the canvas dimensions
        canvas.update()
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()

        # Check if the canvas size is valid
        if canvas_width > 0 and canvas_height > 0:
            # Resize the image to fit the canvas without maintaining aspect ratio
            global photo_width, photo_height
            photo_width = canvas_width
            photo_height = canvas_height
            image = image.resize((photo_width, photo_height), Image.LANCZOS)

            # Convert the image to Tkinter format
            tk_image = ImageTk.PhotoImage(image)

            # Clear the canvas
            canvas.delete("all")

            # Add the image to the canvas
            canvas.create_image(0, 0, anchor=tk.NW, image=tk_image)
            canvas.image = tk_image
            canvas.image_path = new_image_path

    # Get the image files in the "image" folder
    image_files = get_image_files()

    if not image_files:
        return

    # Load the first image in the "image" folder
    image_path = os.path.join(image_folder, image_files[0])
    update_canvas_with_image(image_path)

    # Add Switch Image to the Menubar `Settings`
    settings_menu.add_command(label="Switch Image", command=switch_image)


def switch_menu_name():
    global menu_label, menubar
    if menu_label.get() == 'Edit Location':
        menu_label.set("Finish")
        menubar.delete(0, tk.END)
        menubar.add_command(label=menu_label.get(), command=switch_menu_name)
        menubar.add_command(label="Search Location", command=search_location)
        menubar.add_cascade(label="Help", menu=help_menu)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        canvas.bind('<Button-1>', on_click)
        status_label.configure(text="EDIT MODE", bg="red")
    else:
        menu_label.set("Edit Location")
        menubar.delete(0, tk.END)
        menubar.add_command(label=menu_label.get(), command=switch_menu_name)
        menubar.add_command(label="Search Location", command=search_location)
        menubar.add_cascade(label="Help", menu=help_menu)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        canvas.unbind('<Button-1>')
        status_label.configure(text="", bg="SystemButtonFace")


def mark_position(cord_x, cord_y):
    marker = canvas.create_oval(cord_x - 35, cord_y - 35, cord_x + 35, cord_y + 35, outline="yellow", width=5)
    markers.append(marker)


def remove_last_marker():
    if markers:
        last_marker = markers.pop()
        canvas.delete(last_marker)


def show_help():
    # Read the message text from the Help_File.py module
    with open("help", "r") as file:
        message_text = file.read()
    # Show the message box
    messagebox.showinfo("Help - How to Use", message_text)


def show_about():
    # Read the message text from the Help_File.py module
    with open("about", "r") as file:
        message_text = file.read()

    # Show the message box
    messagebox.showinfo("About Tool Search", message_text)


def add_image():
    # Open a file dialog to select an image file
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])

    # Check if a file was selected
    if file_path:
        # Get the filename and destination path
        filename = os.path.basename(file_path)
        destination = os.path.join("image", filename)

        try:
            # Copy the image file to the "images" folder
            shutil.copy2(file_path, destination)
            messagebox.showinfo("Success", "Image added successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add image: {str(e)}")


def delete_image():
    # Open a file dialog to select an image file for deletion
    file_path = filedialog.askopenfilename(initialdir="image", filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])

    # Check if a file was selected
    if file_path:
        try:
            # Delete the selected image file
            os.remove(file_path)
            messagebox.showinfo("Success", "Image deleted successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete image: {str(e)}")


def show_settings():
    messagebox.showinfo("Settings", "Blank Settings")


root = tk.Tk()
root.title("Tool Search")
root.geometry("1600x900")
root.resizable(False, False)

menubar = tk.Menu(root)
menu_label = tk.StringVar()
menu_label.set("Edit Location")
menubar.add_command(label=menu_label.get(), command=switch_menu_name)
menubar.add_command(label="Search Location", command=search_location)

# Help menu
help_menu = tk.Menu(menubar, tearoff=False)
help_menu.add_command(label="How to Use", command=show_help)
help_menu.add_command(label="About", command=show_about)
menubar.add_cascade(label="Help", menu=help_menu)

# Settings menu
settings_menu = tk.Menu(menubar, tearoff=False)
settings_menu.add_command(label="Settings", command=show_settings)
menubar.add_cascade(label="Settings", menu=settings_menu)

# Add a "Manage Images" submenu with "Add Image" and "Delete Image" options
manage_images_menu = tk.Menu(settings_menu, tearoff=0)
manage_images_menu.add_command(label="Add Image", command=add_image)
manage_images_menu.add_command(label="Delete Image", command=delete_image)
settings_menu.add_cascade(label="Manage Images", menu=manage_images_menu)

root.config(menu=menubar)
canvas = tk.Canvas(root, width=1600, height=900)
canvas.pack(fill=tk.BOTH, expand=True)

status_label = tk.Label(root, text="", bg="SystemButtonFace", font=("Arial", 12))
status_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

handle_image_loading()
markers = []
root.eval('tk::PlaceWindow . center')
root.mainloop()
