import flet as ft
import os
from pathlib import Path
from database import Database, Product
import config
from PIL import Image
from modules.dialog_manager import DialogManager

class EditProductPage():
    def __init__(self, page: ft.Page, user, tovar_id):
        self.db = Database()
        self.user = user
        self.tovar_id = tovar_id
        self.db.connect()
        self.page = page
        self.title = "Редактирование товара"
        self.padding = 20
        self.spacing = 10
        self.product = None
        self.photo_path = None
        self.file_picker = ft.FilePicker(on_result=self.on_file_picker_result)
        self.page.overlay.append(self.file_picker)
        self.page.update()
        self.build()

    def load_product(self):
        try:
            return self.db.get_product(self.tovar_id)
        except Exception as ex:
            DialogManager.show_error_dialog(
                self.page,
                "Ошибка загрузки",
                f"Не удалось загрузить товар (ID: {self.tovar_id}):\n\n{str(ex)}"
            )
            return None

    def build(self):
        self.page.floating_action_button = None
        self.validation_text = ft.Text("", color=ft.Colors.RED, size=12)
        self.validation_view = ft.Row(
            controls=[
                ft.Icon(ft.Icons.ERROR, color=ft.Colors.RED),
                self.validation_text
            ],
            alignment=ft.MainAxisAlignment.END,
            expand=1,
            visible=False
        )

        self.product = self.load_product()
        if not self.product:
            self.validation_text.value = "Товар не найден."
            self.validation_view.visible = True
            DialogManager.show_error_dialog(
                self.page,
                "Товар не найден",
                f"Товар с идентификатором {self.tovar_id} не найден в базе данных. Вернитесь к каталогу.",
                on_close=lambda: self.page.go("/catalog")
            )
            return ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text("Редактирование товара", size=24, weight=ft.FontWeight.BOLD),
                        self.validation_view,
                        ft.ElevatedButton(
                            "Назад",
                            on_click=lambda e: self.page.go("/catalog"),
                            bgcolor="#00FA9A",
                            color="#FFFFFF"
                        )
                    ],
                    spacing=15
                ),
                padding=20
            )

        self.photo_path = self.product.photo or None
        self.photo_image = ft.Image(
            src=os.path.join(config.TOVAR_IMAGES_DIR, self.photo_path) if self.photo_path else config.PLACEHOLDER_IMAGE,
            width=150,
            height=150,
            fit=ft.ImageFit.CONTAIN,
        )
        self.upload_photo_button = ft.ElevatedButton(
            on_click=lambda e: self.file_picker.pick_files(
                allow_multiple=False,
                file_type=ft.FilePickerFileType.IMAGE
            ),
            text="Загрузить фото",
            bgcolor="#4CAF50",
            color="#FFFFFF",
            style = ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(5)
            )
        )
        photo_section = ft.Column(
            controls=[
                ft.Text("Фото товара", weight=ft.FontWeight.BOLD),
                self.photo_image,
                self.upload_photo_button
            ],
            spacing=10
        )

        self.name_input = ft.TextField(
            label="Наименование товара",
            value=self.product.name or "",
            on_change=self.validate_name,
            color=ft.Colors.BLACK,
            border_color=ft.Colors.BLACK,
            focused_border_color=ft.Colors.BLACK,
            label_style=ft.TextStyle(color=ft.Colors.BLACK),
            expand=True,
            cursor_color=ft.Colors.BLACK
        )
        self.category_dropdown = ft.Dropdown(
            label="Категория товара",
            options=[
                ft.dropdown.Option("Мужская обувь"),
                ft.dropdown.Option("Женская обувь"),
            ],
            expand=1,
            value=self.product.category
        )
        self.description_input = ft.TextField(
            label="Описание товара",
            multiline=True,
            min_lines=3,
            max_lines=5,
            value=self.product.description or "",
            on_change=self.validate_description,
            color=ft.Colors.BLACK,
            border_color=ft.Colors.BLACK,
            focused_border_color=ft.Colors.BLACK,
            label_style=ft.TextStyle(color=ft.Colors.BLACK),
            expand=True,
            cursor_color=ft.Colors.BLACK
        )
        self.manufacturer_dropdown = ft.Dropdown(
            label="Производитель",
            options=[
                ft.dropdown.Option("Rieker"),
                ft.dropdown.Option("Kari"),
                ft.dropdown.Option("CROSBY"),
                ft.dropdown.Option("Alessio Nesca"),
                ft.dropdown.Option("Marco Tozzi"),
                ft.dropdown.Option("Рос"),
            ],
            expand=1,
            value=self.product.manufacturer
        )
        self.supplier_input = ft.TextField(
            label="Поставщик",
            value=self.product.supplier or "",
            on_change=self.validate_supplier,
            color=ft.Colors.BLACK,
            border_color=ft.Colors.BLACK,
            focused_border_color=ft.Colors.BLACK,
            label_style=ft.TextStyle(color=ft.Colors.BLACK),
            expand=True,
            cursor_color=ft.Colors.BLACK
        )
        self.price_input = ft.TextField(
            label="Цена",
            value=str(self.product.price) if self.product.price is not None else "",
            on_change=self.validate_price,
            helper_text="Формат: 100.50",
            keyboard_type=ft.KeyboardType.NUMBER,
            color=ft.Colors.BLACK,
            border_color=ft.Colors.BLACK,
            focused_border_color=ft.Colors.BLACK,
            label_style=ft.TextStyle(color=ft.Colors.BLACK),
            expand=True,
            cursor_color=ft.Colors.BLACK
        )
        self.unit_input = ft.TextField(
            label="Единица измерения",
            value=self.product.unit or "",
            on_change=self.validate_unit,
            helper_text="Пример: шт.",
            color=ft.Colors.BLACK,
            border_color=ft.Colors.BLACK,
            focused_border_color=ft.Colors.BLACK,
            label_style=ft.TextStyle(color=ft.Colors.BLACK),
            expand=True,
            cursor_color=ft.Colors.BLACK
        )
        self.stock_input = ft.TextField(
            label="Количество на складе",
            value=str(self.product.stock) if self.product.stock is not None else "",
            on_change=self.validate_stock,
            keyboard_type=ft.KeyboardType.NUMBER,
            color=ft.Colors.BLACK,
            border_color=ft.Colors.BLACK,
            focused_border_color=ft.Colors.BLACK,
            label_style=ft.TextStyle(color=ft.Colors.BLACK),
            expand=True,
            cursor_color=ft.Colors.BLACK,
            helper_text="Не меньше нуля"
        )
        self.discount_input = ft.TextField(
            label="Действующая скидка (%)",
            value=str(self.product.discount) if self.product.discount is not None else "",
            on_change=self.validate_discount,
            keyboard_type=ft.KeyboardType.NUMBER,
            helper_text="Диапазон: 0-100",
            color=ft.Colors.BLACK,
            border_color=ft.Colors.BLACK,
            focused_border_color=ft.Colors.BLACK,
            label_style=ft.TextStyle(color=ft.Colors.BLACK),
            expand=True,
            cursor_color=ft.Colors.BLACK
        )

        self.submit_button = ft.ElevatedButton(
            text="Сохранить изменения",
            on_click=self.save_product,
            bgcolor="#4CAF50",
            color="#FFFFFF",
            expand=1,
            style = ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(5)
            )
        )
        self.delete_button = ft.ElevatedButton(
            text="Удалить товар",
            on_click=self.delete_product,
            bgcolor="#4CAF50",
            color="#FFFFFF",
            expand=1,
            style = ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(5)
            )
        )

        header = ft.Container(
            content=ft.Row(
                controls=[
                    ft.IconButton(
                        icon=ft.Icons.ARROW_BACK,
                        tooltip="Назад",
                        on_click=lambda e: self.page.go("/catalog"),
                        icon_color=ft.Colors.BLACK
                    ),
                    ft.Container(expand=True),
                    ft.Text(f"{self.user.name}"),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            padding=10
        )

        return ft.Container(
            content=ft.Column(
                controls=[
                    header,
                    ft.Text("Редактирование товара", size=24, weight=ft.FontWeight.BOLD),
                    photo_section,
                    ft.Row(
                        controls = [
                            self.name_input,
                            self.category_dropdown,
                        ]
                    ),
                    self.description_input,
                    ft.Row(
                        controls=[
                            self.manufacturer_dropdown,
                            self.supplier_input,
                        ]
                    ),
                    ft.Row(
                        controls = [
                            self.price_input,
                            self.unit_input,
                        ]
                    ),
                    ft.Row(
                        controls = [
                            self.stock_input,
                            self.discount_input,
                        ]
                    ),
                    ft.Row(
                        controls=[
                            self.submit_button,
                            self.delete_button
                        ],
                        spacing=10
                    )
                ],
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.START,
                spacing=15,
                scroll=ft.ScrollMode.AUTO
            ),
            bgcolor=ft.Colors.WHITE,
            padding=20
        )

    def on_file_picker_result(self, e: ft.FilePickerResultEvent):
        if e.files:
            selected_file = e.files[0]
            original_path = selected_file.path

            try:
                image = Image.open(original_path)
                image = image.resize((300, 200), Image.Resampling.LANCZOS)
                filename = os.path.basename(original_path)
                destination_path = os.path.join(config.TOVAR_IMAGES_DIR, filename)
                os.makedirs(config.TOVAR_IMAGES_DIR, exist_ok=True)

                # Удалить старое фото, если оно есть
                if self.photo_path:
                    old_path = os.path.join(config.TOVAR_IMAGES_DIR, self.photo_path)
                    if os.path.exists(old_path):
                        try:
                            os.remove(old_path)
                        except Exception as ex:
                            print(f"Ошибка удаления старого фото: {ex}")

                image.save(destination_path, quality=85)
                self.photo_path = filename
                self.photo_image.src = destination_path
            except Exception as ex:
                DialogManager.show_error_dialog(
                    self.page,
                    "Ошибка обработки изображения",
                    f"Не удалось обработать изображение: {str(ex)}"
                )
        else:
            print("File selection cancelled.")
        self.page.update()

    def validate_name(self, e):
        if not self.name_input.value or self.name_input.value.strip() == "":
            self.validation_text.value = "Укажите наименование товара."
            self.validation_view.visible = True
            self.page.update()
            return False
        self.validation_view.visible = False
        self.page.update()
        return True

    def validate_description(self, e):
        if not self.description_input.value or self.description_input.value.strip() == "":
            self.validation_text.value = "Укажите описание товара."
            self.validation_view.visible = True
            self.page.update()
            return False
        self.validation_view.visible = False
        self.page.update()
        return True

    def validate_supplier(self, e):
        if not self.supplier_input.value or self.supplier_input.value.strip() == "":
            self.validation_text.value = "Укажите поставщика."
            self.validation_view.visible = True
            self.page.update()
            return False
        self.validation_view.visible = False
        self.page.update()
        return True

    def validate_price(self, e):
        try:
            if not self.price_input.value or self.price_input.value.strip() == "":
                self.validation_text.value = "Укажите цену товара."
                self.validation_view.visible = True
                self.page.update()
                return False
            float(self.price_input.value)
            self.validation_view.visible = False
            self.page.update()
            return True
        except ValueError:
            self.validation_text.value = "Цена должна быть числом. Пример: 100.50"
            self.validation_view.visible = True
            self.page.update()
            return False

    def validate_unit(self, e):
        if not self.unit_input.value or self.unit_input.value.strip() == "":
            self.validation_text.value = "Укажите единицу измерения."
            self.validation_view.visible = True
            self.page.update()
            return False
        self.validation_view.visible = False
        self.page.update()
        return True

    def validate_stock(self, e):
        try:
            if not self.stock_input.value:
                raise ValueError()
            stock = int(self.stock_input.value)
            if stock < 0:
                self.validation_text.value = "Количество на складе не может быть отрицательным."
                self.validation_view.visible = True
                self.page.update()
                return False
            self.validation_view.visible = False
            self.page.update()
            return True
        except ValueError:
            self.validation_text.value = "Неверный формат количества. Используйте целые числа."
            self.validation_view.visible = True
            self.page.update()
            return False

    def validate_discount(self, e):
        try:
            if not self.discount_input.value:
                self.validation_view.visible = False
                self.page.update()
                return True
            discount = float(self.discount_input.value)
            if discount < 0 or discount > 100:
                self.validation_text.value = "Скидка должна быть в диапазоне 0-100%."
                self.validation_view.visible = True
                self.page.update()
                return False
            self.validation_view.visible = False
            self.page.update()
            return True
        except ValueError:
            self.validation_text.value = "Неверный формат скидки."
            self.validation_view.visible = True
            self.page.update()
            return False

    def validate_inputs(self):
        return (
            self.validate_name(None) and
            self.validate_description(None) and
            self.validate_supplier(None) and
            self.validate_price(None) and
            self.validate_unit(None) and
            self.validate_stock(None) and
            self.validate_discount(None)
        )

    def save_product(self, e):
        """Сохранить изменения товара с обработкой ошибок и диалогами"""
        try:
            if not self.category_dropdown.value:
                DialogManager.show_error_dialog(
                    self.page,
                    "Ошибка валидации",
                    "Выберите категорию товара."
                )
                return
            if not self.manufacturer_dropdown.value:
                DialogManager.show_error_dialog(
                    self.page,
                    "Ошибка валидации",
                    "Выберите производителя товара."
                )
                return
            if not self.validate_inputs():
                DialogManager.show_error_dialog(
                    self.page,
                    "Ошибка валидации",
                    "Пожалуйста, проверьте заполнение всех полей."
                )
                return

            # Обновление товара в базе данных
            self.db.update_product(
                tovar_id=self.tovar_id,
                name=self.name_input.value,
                unit=self.unit_input.value,
                price=float(self.price_input.value),
                supplier=self.supplier_input.value,
                manufacturer=self.manufacturer_dropdown.value,
                category=self.category_dropdown.value,
                discount=float(self.discount_input.value) if self.discount_input.value else 0,
                stock=int(self.stock_input.value),
                description=self.description_input.value,
                photo_path=self.photo_path
            )

            DialogManager.show_success_dialog(
                self.page,
                "Сохранено",
                "Изменения успешно сохранены.",
                on_close=lambda: self.page.go("/catalog")
            )
        except Exception as ex:
            DialogManager.show_error_dialog(
                self.page,
                "Ошибка сохранения",
                f"Не удалось сохранить изменения товара:\n\n{str(ex)}"
            )

    def delete_product(self, e):
            """Удаление товара с подтверждением и обработкой ошибок"""
            def on_confirm():
                try:
                    self.db.delete_product(self.tovar_id)
                    if self.photo_path:
                        photo_file = os.path.join(config.TOVAR_IMAGES_DIR, self.photo_path)
                        if os.path.exists(photo_file):
                            try:
                                os.remove(photo_file)
                            except Exception as ex:
                                print(f"Ошибка удаления фото: {ex}")
                    DialogManager.show_success_dialog(
                        self.page,
                        "Удалено",
                        "Товар успешно удалён.",
                        on_close=lambda: self.page.go("/catalog")
                    )
                except Exception as ex:
                    DialogManager.show_error_dialog(
                        self.page,
                        "Ошибка удаления",
                        f"Не удалось удалить товар:\n\n{str(ex)}"
                    )

            DialogManager.show_warning_dialog(
                self.page,
                "Подтверждение удаления",
                "Вы уверены, что хотите удалить этот товар? Действие нельзя будет отменить.",
                on_confirm=on_confirm
            )