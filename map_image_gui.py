import tkinter as tk
from tkinter import filedialog, messagebox

from map_image import *


def main():
    def open_file():
        filepath = filedialog.askopenfilename()
        if filepath:
            engine = engine_var.get()
            coords = ImageCoordinatesParser(filepath).coordinates
            if not coords:
                messagebox.showinfo("Coordinates not found", f"Not image file or no GPS coordinates in image:\n\n{filepath}")
                return
            map_url = make_url_from_coordinates(coords.longitude, coords.latitude, engine)
            webbrowser.open(map_url)

    root = tk.Tk()
    root.title("Выбор файла")

    engine_var = tk.StringVar(root)
    engine_var.set("Yandex")  # значение по умолчанию
    tk.OptionMenu(root, engine_var, "Yandex", "Google").pack(pady=10)
    tk.Button(root, text="Выбрать jpg файл", command=open_file).pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    main()