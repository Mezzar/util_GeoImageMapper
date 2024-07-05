Утилита для отображения геолокации фотографий на карте. Карта открывается в браузере, можно выбирать Yandex или Google. 

Версия для обработки одного файла и всех файлов в папкею

Есть консольная и GUI версия.

Синтаксис консольной: `python map_image.py image_filepath` для одного файла и `python map_folder.py folder_path` для папки.

По умолчанию отображается на карте Яндекса. Для выбора Google добавить параметр `-m g` (полная версия `--map google`)

GUI скрипты: `map_image_gui.py` и `map_folder_gui.py`. В них выбор файла/папки с помощью интерфейса.
