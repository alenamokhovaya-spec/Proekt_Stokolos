import os

DB_CONFIG = {
    'host': 'localhost',
    'database': 'postgres',
    'user': 'postgres',
    'password': '123',
    'port': '5432'
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
IMAGES_DIR = os.path.join(ASSETS_DIR, 'images')
TOVAR_IMAGES_DIR = os.path.join(IMAGES_DIR, 'tovar')

APP_TITLE = "ООО «Обувь» - Магазин обуви"
APP_ICON = os.path.join(IMAGES_DIR, "icon.ico")
PLACEHOLDER_IMAGE = os.path.join(IMAGES_DIR, "picture.png")
LOGO_IMAGE = os.path.join(IMAGES_DIR, "icon.png")

