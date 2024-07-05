import os.path
from dataclasses import dataclass
import PIL
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

@dataclass
class Coordinates:
    latitude: float
    longitude: float

    def __bool__(self):
        return bool(self.latitude) and bool(self.longitude)

    def __str__(self):
        return f'Coordinates(lat={self.latitude}, long={self.longitude})'

class ImageCoordinatesParser:
    def __init__(self, image_path:str, ignore_image_errors:bool=True):
        if not os.path.isfile(image_path):
            raise FileNotFoundError()
        self.ignore_image_errors = ignore_image_errors

        self.coordinates = Coordinates(None, None)
        try:
            image = Image.open(image_path)
        except PIL.UnidentifiedImageError as e:
            if not ignore_image_errors:
                raise e
            else:
                image = None
        exif_data = self._get_exif_data(image)
        geotagging = self._get_geotagging(exif_data)
        self.coordinates = self._get_coordinates_from_geotags(geotagging)

    def has_coordinates(self):
        return bool(self.coordinates)

    def _get_exif_data(self, image) -> dict:
        exif_data = {}
        if not image:
            if self.ignore_image_errors:
                return exif_data
            else:
                raise ValueError("Incorrect image object")

        info = image._getexif()
        if info:
            for tag, value in info.items():
                decoded = TAGS.get(tag, tag)
                exif_data[decoded] = value
        return exif_data

    def _get_geotagging(self, exif_data:dict) -> dict:
        geotagging = {}
        if not exif_data:
            if self.ignore_image_errors:
                return geotagging
            else:
                raise ValueError("No EXIF metadata found")

        for (key, val) in exif_data.items():
            if key == "GPSInfo":
                for t in val:
                    sub_decoded = GPSTAGS.get(t, t)
                    geotagging[sub_decoded] = val[t]

        return geotagging

    def _get_coordinates_from_geotags(self, geotags:dict) -> Coordinates:
        """Extract latitude and longitude from geotagging data."""
        def convert_to_degrees(value):
            d, m, s = value
            return d + (m / 60.0) + (s / 3600.0)

        if not geotags or 'GPSLatitude' not in geotags or 'GPSLongitude' not in geotags:
            return Coordinates(None, None)

        lat = convert_to_degrees(geotags["GPSLatitude"])
        lon = convert_to_degrees(geotags["GPSLongitude"])

        if geotags["GPSLatitudeRef"] != "N":
            lat = -lat
        if geotags["GPSLongitudeRef"] != "E":
            lon = -lon
        return Coordinates(lat, lon)


class MapUrlGenerator:
    def single(self, coordinates:Coordinates) -> str:
        raise NotImplementedError("This method should be implemented by subclasses")

    def multiple(self, coordinates_list:list[Coordinates], markers_limit:int) -> str:
        raise NotImplementedError("This method should be implemented by subclasses")

    def _find_center(self, coordinates_list:list[Coordinates], markers_limit:int|None=None) -> Coordinates:
        if markers_limit:
            limit = min(markers_limit, len(coordinates_list))
        else:
            limit = len(coordinates_list)
        lats, longs = [], []
        for coords in coordinates_list[:limit]:
            lats.append(coords.latitude)
            longs.append(coords.longitude)
        center_coord = Coordinates(latitude = sum(lats) / limit, longitude = sum(longs) / limit)
        return center_coord

class GoogleMapUrlGenerator(MapUrlGenerator):
    def single(self, coordinates:Coordinates) -> str:
        return f"https://www.google.com/maps?q={coordinates.latitude},{coordinates.longitude}"

    def multiple(self, coordinates_list:list[Coordinates], markers_limit:int=200, zoom:int=10) -> str:
        center_point = self._find_center(coordinates_list, markers_limit)
        map_url = "https://www.google.com/maps/dir/"
        for coords in coordinates_list[:markers_limit]:
            map_url += f"{coords.latitude},{coords.longitude}/"
        map_url = map_url + "/@"  # собака нужна, чтобы были точки, а не маршрут
        map_url += f"{center_point.latitude},{center_point.longitude},{zoom}z"  #центр обзора и зум
        return map_url

class YandexMapUrlGenerator(MapUrlGenerator):
    def single(self, coordinates:Coordinates, zoom:int=12) -> str:
        return f"https://yandex.ru/maps/?pt={coordinates.longitude}%2C{coordinates.latitude}&z={zoom}"

    def multiple(self, coordinates_list:list[Coordinates], markers_limit:int=200, zoom:int=12) -> str:
        # Описание синтаксиса Яндекс карт:
        # https://yandex.com/dev/yandex-apps-launch-maps/doc/en/concepts/yandexmaps-web#yandexmaps-web__section_b3b_cst_ngb

        center_point = self._find_center(coordinates_list, markers_limit)
        map_url = "https://yandex.ru/maps/?pt="
        for coords in coordinates_list[:markers_limit]:
            map_url += f"{coords.longitude},{coords.latitude}~"
        map_url = map_url.rstrip("~")
        map_url += f"&ll={center_point.longitude},{center_point.latitude}"   #центр экрана
        map_url += f"&z={zoom}"
        return map_url


class MapUrlGeneratorFactory:
    @staticmethod
    def create(engine:str):
        engine = engine.lower()
        if engine in ["google", "g"]:
            return GoogleMapUrlGenerator()
        elif engine in ["yandex", "y"]:
            return YandexMapUrlGenerator()
        else:
            raise ValueError(f"Unknown map engine: {engine}")
