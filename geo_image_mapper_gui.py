import os
import webbrowser

import tkinter as tk
from tkinter import filedialog, messagebox

from utils import ImageCoordinatesParser, Coordinates, MapUrlGeneratorFactory

def main():
    def open_file():
        filepath = filedialog.askopenfilename()
        if filepath:
            engine = engine_var.get()
            coords = ImageCoordinatesParser(filepath).coordinates
            if not coords:
                msg = f"Файл не является изображением или не содержит GPS кооординат:\n\n{filepath}"
                messagebox.showinfo("Координаты не найдены", msg)
                return
            map_url = MapUrlGeneratorFactory.create(engine).single(coords)
            webbrowser.open(map_url)

    def open_folder():
        def parse_folder(folder_path: str, engine: str) -> list[Coordinates]:
            images_coordinates = []
            for filename in os.listdir(folder_path):
                if filename.lower().endswith(".jpg") or filename.lower().endswith(".jpeg"):
                    image_path = os.path.join(folder_path, filename)

                    coords = ImageCoordinatesParser(image_path).coordinates
                    if coords:
                        images_coordinates.append(coords)
            return images_coordinates

        folder = filedialog.askdirectory()
        engine = engine_var.get()
        if folder:
            coords_list = parse_folder(folder, engine)
            if coords_list:
                print(f'Found {len(coords_list)} images with GPS coordinates')
                map_url = MapUrlGeneratorFactory.create(engine).multiple(coords_list, markers_limit=MAX_MARKERS)
                print('Opening URL in browser:', map_url)
                if len(coords_list) > MAX_MARKERS:
                    msg = f"Найдено {len(coords_list)} > {MAX_MARKERS} изображений с GPSкоординатами. Огранививаем число меток до {MAX_POINTS_ON_MAP}"
                    messagebox.showinfo("Лимит числа меток", msg)
                    print(msg)
                webbrowser.open(map_url)
            else:
                print('Не найдено изображений с GPS координатами.')

    MAX_MARKERS: int = 200 #максимальное число маркеров на карте

    root = tk.Tk()
    root.title("GeoImageMapper")
    root.geometry("270x100")

    frame = tk.Frame(root, padx=10, pady=10)
    frame.pack(expand=True)

    engine_var = tk.StringVar(root)
    engine_var.set("Yandex")  # значение по умолчанию
    tk.Label(frame, text="Сервис карт").grid(row=1, column=1)
    tk.OptionMenu(frame, engine_var, "Yandex", "Google").grid(row=1, column=2)
    tk.Label(frame, text="").grid(row=2, column=1)
    tk.Label(frame, text="Выбрать источник").grid(row=3, column=1)
    tk.Button(frame, text="Файл", command=open_file).grid(row=3, column=2)
    tk.Button(frame, text="Папка", command=open_folder).grid(row=3, column=3)
    root.mainloop()


if __name__ == "__main__":
    main()