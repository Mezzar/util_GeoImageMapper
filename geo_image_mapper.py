import os
import webbrowser
import argparse
from tqdm.auto import tqdm

from utils import ImageCoordinatesParser, Coordinates, MapUrlGeneratorFactory

def parse_arguments():
    parser = argparse.ArgumentParser(description="Extract GPS coordinates from JPG image(s) and display in browser map.")
    parser.add_argument("path", help="Path to imagefile or folder with JPG images")
    parser.add_argument("-m", "--map",
                        default="yandex",
                        choices=["yandex", "google", "y", "g"],
                        help="Map engine: Yandex (default) or Google")
    parser.add_argument("-l", "--limit",
                        default=200,
                        type=int,
                        help="Maximum number of markers when processing folder (default: 200)")
    return parser.parse_args()

def parse_folder(folder_path:str) -> list[Coordinates]:
    images_coordinates = []
    for filename in tqdm(os.listdir(folder_path), leave=False):
        if filename.lower().endswith(".jpg") or filename.lower().endswith(".jpeg"):
            image_path = os.path.join(folder_path, filename)

            coords = ImageCoordinatesParser(image_path).coordinates
            if coords:
                images_coordinates.append(coords)
    return images_coordinates

def main():
    args = parse_arguments()
    path = args.path
    engine = args.map
    markers_limit = args.limit

    if os.path.isfile(path):
        coords = ImageCoordinatesParser(path).coordinates
        if not coords:
            print("Coordinates not found in the image file.")
            return

        print(f"Latitude: {coords.latitude}, Longitude: {coords.longitude}")
        map_url = MapUrlGeneratorFactory.create(engine).single(coords)
        print('Opening URL in browser:', map_url)
        webbrowser.open(map_url)
    elif os.path.isdir(path):
        coords_list = parse_folder(path)
        if coords_list:
            print(f'Found {len(coords_list)} images with GPS coordinates')
            map_url = MapUrlGeneratorFactory.create(engine).multiple(coords_list, markers_limit=markers_limit)
            print('Opening URL in browser:', map_url)
            if len(coords_list) > markers_limit:
                print(f'Warning: found  {len(coords_list)} > {markers_limit} images with GPS coordinates.',
                        f'Limited map to {markers_limit} markers.')
            webbrowser.open(map_url)
        else:
            print('No images with GPS coordinates found')
    else:
        print("Invalid path. Provide path to jpg file of folder with images.")


if __name__ == "__main__":
    main()
