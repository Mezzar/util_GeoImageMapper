import os
import os.path
import webbrowser
import argparse
from tqdm.auto import tqdm

from utils import ImageCoordinatesParser, Coordinates

def parse_arguments():
    parser = argparse.ArgumentParser(description="Extract GPS coordinates from all JPG images in folder and display them in browser map.")
    parser.add_argument("folder", help="Path to the folder with JPG images")
    parser.add_argument("-m", "--map",
                        default="yandex",
                        choices=["yandex", "google", "y", "g"],
                        help="Map engine: Yandex (default) or Google")
    return parser.parse_args()

def parse_folder(folder_path:str, engine:str) -> list[Coordinates]:
    images_coordinates = []
    for filename in tqdm(os.listdir(folder_path), leave=False):
        if filename.lower().endswith(".jpg") or filename.lower().endswith(".jpeg"):
            image_path = os.path.join(folder_path, filename)

            coords = ImageCoordinatesParser(image_path).coordinates
            if coords:
                images_coordinates.append(coords)
    return images_coordinates

def get_url(coords_list:list[Coordinates], engine:str) -> str:
    def get_yandex_url(coords_list: list[Coordinates], zoom: int = 12) -> str:
        # Описание синтаксиса Яндекс карт:
        # https://yandex.com/dev/yandex-apps-launch-maps/doc/en/concepts/yandexmaps-web#yandexmaps-web__section_b3b_cst_ngb

        mean_latitude, mean_longitude = 0, 0
        for coords in coords_list:
            mean_latitude += coords.latitude / len(coords_list)
            mean_longitude += coords.longitude / len(coords_list)

        map_url = "https://yandex.ru/maps/?pt="
        for coords in coords_list:
            map_url += f"{coords.longitude},{coords.latitude}~"
        map_url = map_url.rstrip("~")
        map_url += f"&ll={mean_longitude},{mean_latitude}"   #центр экрана
        map_url += f"&z={zoom}"
        return map_url

    def get_google_url(coords_list: list[Coordinates]) -> str:
        zoom = 10
        map_url = "https://www.google.com/maps/dir/"
        for coords in coords_list:
            map_url += f"{coords.latitude},{coords.longitude}/"
        map_url = map_url + "/@"  # собака нужна, чтобы были точки, а не маршрут
        map_url += f"{coords_list[0].latitude},{coords_list[0].longitude},{zoom}z"  #центр обзора и зум
        return map_url

    engine = engine.lower()
    if engine in ["yandex", "y"]:
        return get_yandex_url(coords_list)
    elif engine in ["google", "g"]:
        return get_google_url(coords_list)


def main():
    MAX_POINTS_ON_MAP:int = 200

    args = parse_arguments()
    folder_path:str = args.folder
    engine:str = args.map

    coords_list = parse_folder(folder_path, engine)
    if coords_list:
        print(f'Found {len(coords_list)} images with GPS coordinates')
        map_url = get_url(coords_list[:MAX_POINTS_ON_MAP], engine)
        print('Opening URL in browser:', map_url)
        if len(coords_list) > MAX_POINTS_ON_MAP:
            print(f'Warning: found > {MAX_POINTS_ON_MAP} images with GPS coordinates. Limiting to {MAX_POINTS_ON_MAP}.')
        webbrowser.open(map_url)
    else:
        print('No images with GPS coordinates found')


if __name__ == "__main__":
    main()