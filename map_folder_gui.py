import tkinter as tk
from tkinter import filedialog, messagebox

from map_folder import *


def main():
    def open_folder():
        folder = filedialog.askdirectory()
        engine = engine_var.get()
        if folder:
            coords_list = parse_folder(folder, engine)
            if coords_list:
                print(f'Found {len(coords_list)} images with GPS coordinates')
                map_url = get_url(coords_list[:MAX_POINTS_ON_MAP], engine)
                print('Opening URL in browser:', map_url)
                if len(coords_list) > MAX_POINTS_ON_MAP:
                    msg = f"found {len(coords_list)} > {MAX_POINTS_ON_MAP} images with GPS coordinates. Limiting to {MAX_POINTS_ON_MAP}"
                    messagebox.showinfo("Limit", msg)
                    print(msg)
                webbrowser.open(map_url)
            else:
                print('No images with GPS coordinates found')

    MAX_POINTS_ON_MAP: int = 200

    root = tk.Tk()
    root.title("Выбор файла")

    engine_var = tk.StringVar(root)
    engine_var.set("Yandex")  # значение по умолчанию
    tk.OptionMenu(root, engine_var, "Yandex", "Google").pack(pady=10)
    tk.Button(root, text="Выбрать папку", command=open_folder).pack(pady=20)
    root.mainloop()


if __name__ == "__main__":
    main()