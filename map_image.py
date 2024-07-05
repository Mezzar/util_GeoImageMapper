import webbrowser
import argparse

from utils import ImageCoordinatesParser

def parse_arguments():
    parser = argparse.ArgumentParser(description="Extract GPS coordinates from JPG image and display in browser map.")
    parser.add_argument("file", help="Path to the JPG image file")
    parser.add_argument("-m", "--map",
                        default="yandex",
                        choices=["yandex", "google", "y", "g"],
                        help="Map engine: Yandex (default) or Google")
    return parser.parse_args()

def make_url_from_coordinates(latitude:float, longitude:float, engine:str) -> str:
    engine = engine.lower()
    if engine in ["google", "g"]:
        return f"https://www.google.com/maps?q={longitude},{latitude}"
    elif engine in ["yandex", "y"]:
        zoom = 12
        return f"https://yandex.ru/maps/?pt={latitude}%2C{longitude}&z={zoom}"
    else:
        raise ValueError("Unknown map engine.")


def main():
    args = parse_arguments()

    image_path = args.file
    engine = args.map
    coords = ImageCoordinatesParser(image_path).coordinates

    if not coords:
        print("Coordinates not found in the image file.")
        return

    print(f"Latitude: {coords.latitude}, Longitude: {coords.longitude}")

    map_url = make_url_from_coordinates(coords.longitude, coords.latitude, engine)
    print('Opening URL in browser:', map_url)
    webbrowser.open(map_url)

if __name__ == "__main__":
    main()