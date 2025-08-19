import tkinter
import customtkinter
import os
from PIL import Image

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # configure window
        self.title("PhotoArchive UI")
        self.geometry(f"{1100}x{580}")

        # Load image
        self.preview_image = customtkinter.CTkImage(Image.open(os.path.join("images", "placeholder.jpg")), size=(4288/16, 2848/16))
        self.icon_home = customtkinter.CTkImage(Image.open(os.path.join("images", "icons", "media-image-list.png")), size=(20, 20))
        self.icon_import = customtkinter.CTkImage(Image.open(os.path.join("images", "icons", "media-image-plus.png")), size=(20, 20))
        self.icon_archive = customtkinter.CTkImage(Image.open(os.path.join("images", "icons", "media-image-folder.png")), size=(20, 20))

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        # create sidebar frame with widgets
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="PhotoArchive", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        self.home_button = customtkinter.CTkButton(
            self.sidebar_frame,
            corner_radius=0,
            height=40, border_spacing=10,
            text="Home",
            fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
            image=self.icon_home,
            anchor="w",
            command=self.home_button_event)
        self.home_button.grid(row=1, column=0, sticky="ew")
        self.import_button = customtkinter.CTkButton(
            self.sidebar_frame,
            corner_radius=0,
            height=40, border_spacing=10,
            text="Import",
            fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
            image=self.icon_import,
            anchor="w",
            command=self.import_button_event)
        self.import_button.grid(row=2, column=0, sticky="ew")
        self.archive_button = customtkinter.CTkButton(
            self.sidebar_frame,
            corner_radius=0,
            height=40, border_spacing=10,
            text="Archive",
            fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
            image=self.icon_archive,
            anchor="w",
            command=self.archive_button_event)
        self.archive_button.grid(row=3, column=0, sticky="ew")

        # Home Frame
        self.home_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.home_frame.grid_columnconfigure(0, weight=1)

        self.home_frame_large_image_label = customtkinter.CTkLabel(self.home_frame, text="", image=self.preview_image, compound="top")
        self.home_frame_large_image_label.grid(row=0, column=0, padx=20, pady=10)

        # Import Frame
        self.import_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.import_frame.grid_columnconfigure(0, weight=1)

        self.import_frame_label = customtkinter.CTkLabel(self.import_frame, text="Import Frame", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.import_frame_label.grid(row=0, column=0, padx=20, pady=10)

        # Archive Frame
        self.archive_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.archive_frame.grid_columnconfigure(0, weight=1)

        self.archive_frame_label = customtkinter.CTkLabel(self.archive_frame, text="Archive Frame", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.archive_frame_label.grid(row=0, column=0, padx=20, pady=10)

        # Default
        self.select_frame_by_name("home")

    def select_frame_by_name(self, name):

        frames_and_buttons_by_names = {
            "home": (self.home_frame, self.home_button),
            "import": (self.import_frame, self.import_button),
            "archive": (self.archive_frame, self.archive_button)
        }

        for frame_name, (frame, button) in frames_and_buttons_by_names.items():
            button.configure(fg_color=("gray75", "gray25") if frame_name == name else "transparent")
            if frame_name == name:
                frame.grid(row=0, column=1, sticky="nsew")
            else:
                frame.grid_forget()

    def home_button_event(self):
        self.select_frame_by_name("home")
    def import_button_event(self):
        self.select_frame_by_name("import")
    def archive_button_event(self):
        self.select_frame_by_name("archive")

    def open_input_dialog_event(self):
        dialog = customtkinter.CTkInputDialog(text="Type in a number:", title="CTkInputDialog")
        print("CTkInputDialog:", dialog.get_input())

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

    def sidebar_button_event(self):
        print("sidebar_button click")


if __name__ == "__main__":
    app = App()
    app.mainloop()