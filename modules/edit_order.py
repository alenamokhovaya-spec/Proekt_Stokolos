import flet as ft
from database import Database, Order
import config
import re
from modules.dialog_manager import DialogManager

class EditOrderPage():
    def __init__(self, page: ft.Page, user, order_id):
        self.db = Database()
        self.user = user
        self.order_id = order_id
        self.db.connect()
        self.page = page
        self.title = "Редактирование заказа"
        self.padding = 20
        self.spacing = 10
        self.order = None
        self.build()

    def load_order(self):
        try:
            return self.db.get_order(self.order_id)
        except Exception as ex:
            DialogManager.show_error_dialog(
                self.page,
                "Ошибка загрузки",
                f"Не удалось загрузить заказ (ID: {self.order_id}):\n\n{str(ex)}"
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

        self.order = self.load_order()
        if not self.order:
            self.validation_text.value = "Заказ не найден."
            self.validation_view.visible = True
            DialogManager.show_error_dialog(
                self.page,
                "Заказ не найден",
                f"Заказ с идентификатором {self.order_id} не найден в базе данных. Вернитесь к списку заказов.",
                on_close=lambda: self.page.go("/orders")
            )
            return ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text("Редактирование заказа", size=24, weight=ft.FontWeight.BOLD),
                        self.validation_view,
                        ft.ElevatedButton(
                        "Назад",
                        on_click=lambda e: self.page.go("/orders"),
                        bgcolor="#4CAF50",
                        color="#FFFFFF"
                        )
                    ],
                    spacing=15
                ),
                padding=20
            )

        self.article_input = ft.TextField(
            label="Артикул",
            value=self.order.article or "",
            helper_text="Формат: А112Т4, 2, F635R4, 2",
            color=ft.Colors.BLACK,
            border_color=ft.Colors.BLACK,
            focused_border_color=ft.Colors.BLACK,
            label_style=ft.TextStyle(color=ft.Colors.BLACK),
            expand=True,
            cursor_color=ft.Colors.BLACK
        )
        self.status_drop_down = ft.Dropdown(
            label="Статус заказа",
            options=[
                ft.dropdown.Option("Новый"),
                ft.dropdown.Option("Завершен"),
                ft.dropdown.Option("Отменен"),
            ],
            helper_text="Выберите один",
            expand=1,
            value=self.order.status
        )
        self.address_input = ft.TextField(
            label="Адрес пункта выдачи",
            value=self.order.pick_up_point or "",
            on_change=self.validate_adress,
            helper_text="Формат: 123456, г. Город, ул. Улица, 12",
            color=ft.Colors.BLACK,
            border_color=ft.Colors.BLACK,
            focused_border_color=ft.Colors.BLACK,
            label_style=ft.TextStyle(color=ft.Colors.BLACK),
            expand=True,
            cursor_color=ft.Colors.BLACK
        )
        self.date_order = ft.TextField(
            label="Дата заказа",
            helper_text="Формат: ГГГГ-ММ-ДД",
            on_change=self.validate_date,
            value=self.order.date_order or "",
            color=ft.Colors.BLACK,
            border_color=ft.Colors.BLACK,
            focused_border_color=ft.Colors.BLACK,
            label_style=ft.TextStyle(color=ft.Colors.BLACK),
            expand=True,
            cursor_color=ft.Colors.BLACK
        )
        self.date_deliver = ft.TextField(
            label="Дата выдачи",
            helper_text="Формат: ГГГГ-ММ-ДД",
            on_change=self.validate_date,
            keyboard_type=ft.KeyboardType.NUMBER,
            value=self.order.date_delivery or "",
            color=ft.Colors.BLACK,
            border_color=ft.Colors.BLACK,
            focused_border_color=ft.Colors.BLACK,
            label_style=ft.TextStyle(color=ft.Colors.BLACK),
            expand=True,
            cursor_color=ft.Colors.BLACK
        )
        self.submit_button = ft.ElevatedButton(
            text="Сохранить изменения",
            on_click=self.save_order,
            bgcolor="#4CAF50",
            color="#FFFFFF",
            expand=1,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(5)
            )
        )

        self.delete_button = ft.ElevatedButton(
            text="Удалить заказ",
            on_click=self.delete_order,
            bgcolor="#4CAF50",
            color="#FFFFFF",
            expand=1,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(5)
            )
        )

        header = ft.Container(
            content =
            ft.Row(
                controls=[
                    ft.IconButton(
                        icon=ft.Icons.ARROW_BACK,
                        tooltip="Назад",
                        on_click=lambda e: self.page.go("/orders"),
                        icon_color=ft.Colors.BLACK
                    ),
                    ft.Container(expand=True),
                    ft.Text(f"Пользователь: {self.user.name}"),
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
                    ft.Text("Редактирование заказа", size=24, weight=ft.FontWeight.BOLD),
                    ft.Row(
                        controls =[
                            self.article_input,
                            self.status_drop_down,
                        ]
                    ),
                    self.address_input,
                    ft.Row(
                        controls = [
                            self.date_deliver,
                            self.date_order,
                        ]
                    ),
                    
                    self.validation_view,
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
                spacing=15
            ),
            bgcolor=ft.Colors.WHITE,
            padding=20
        )

    def validate_inputs(self):
        self.validate_adress(None)
        if self.validation_view.visible:
            return
        self.validate_date(None)
        if self.validation_view.visible:
            return

    def validate_date(self, e):
        date_order = str(self.date_order.value)
        date_deliver = str(self.date_deliver.value)     
        pattern = r'^\d{4}-\d{2}-\d{2}$'     

        if not bool(re.match(pattern, date_order)):
            self.validation_text.value = "Неверный формат даты заказа."
            self.validation_view.visible = True
            self.page.update()
            return

        if not bool(re.match(pattern, date_deliver)):
            self.validation_text.value = "Неверный формат даты выдачи."
            self.validation_view.visible = True
            self.page.update()
            return

        if date_deliver < date_order:
            self.validation_text.value = "Дата доставки не может быть раньше даты заказа."
            self.validation_view.visible = True
            self.page.update()
            return

        self.validation_view.visible = False
        self.page.update()

    def validate_adress(self, e):
        pattern = r'^\d{6}, г\. [А-ЯЁ][а-яё]+, ул\. [0-9А-ЯЁ][0-9А-ЯЁа-яё\s]+, \d+$'

        if not bool(re.match(pattern, (self.address_input.value or ""))):
            self.validation_text.value = "Неверный формат адреса."
            self.validation_view.visible = True
            self.page.update()
            return
        if (self.address_input.value or "").strip() == '':
            self.validation_text.value = "Неверный формат адреса."
            self.validation_view.visible = True
            self.page.update()
            return
        self.validation_view.visible = False
        self.page.update()
    
    def delete_order(self, e):
        """Удаление заказа с подтверждением и обработкой ошибок"""
        def on_confirm():
            try:
                if self.db.delete_order(self.order_id):
                    DialogManager.show_success_dialog(
                        self.page,
                        "Удалено",
                        "Заказ успешно удалён.",
                        on_close=lambda: self.page.go("/orders")
                    )
                else:
                    DialogManager.show_error_dialog(
                        self.page,
                        "Ошибка удаления",
                        "Не удалось удалить заказ. Возможно, он уже был удалён."
                    )
            except Exception as ex:
                DialogManager.show_error_dialog(
                    self.page,
                    "Ошибка удаления",
                    f"Не удалось удалить заказ:\n\n{str(ex)}"
                )

        DialogManager.show_warning_dialog(
            self.page,
            "Подтверждение удаления",
            "Вы уверены, что хотите удалить этот заказ? Действие нельзя будет отменить.",
            on_confirm=on_confirm
        )

    def save_order(self, e):
        """Сохранить заказ с диалогами об ошибках и подтверждением успеха"""

        if self.status_drop_down.value is None:
            DialogManager.show_error_dialog(
                self.page,
                "Ошибка валидации",
                "Укажите статус заказа."
            )
            return
        if (self.address_input.value or "") == '':
            DialogManager.show_error_dialog(
                self.page,
                "Ошибка валидации",
                "Укажите адрес пункта выдачи."
            )
            return
        if (self.date_deliver.value or "") == '':
            DialogManager.show_error_dialog(
                self.page,
                "Ошибка валидации",
                "Укажите дату доставки."
            )
            return
        if (self.date_order.value or "") == '':
            DialogManager.show_error_dialog(
                self.page,
                "Ошибка валидации",
                "Укажите дату заказа."
            )
            return


        self.validate_inputs()
        if self.validation_view.visible:
            DialogManager.show_error_dialog(
                self.page,
                "Ошибка валидации",
                f"{self.validation_text.value}\n\nИсправьте данные и попробуйте снова."
            )
            return

        try:
            pick_up_point_adress = self.address_input.value

            self.db.update_order(
                order_id=self.order_id,
                article=self.article_input.value,
                status=self.status_drop_down.value,
                date_order=self.date_order.value,
                date_delivery=self.date_deliver.value,
                pick_up_point_adress=pick_up_point_adress
            )
            DialogManager.show_success_dialog(
                self.page,
                "Сохранено",
                "Изменения успешно сохранены.",
                on_close=lambda: self.page.go("/orders")
            )
        except Exception as ex:
            DialogManager.show_error_dialog(
                self.page,
                "Ошибка сохранения",
                f"Не удалось сохранить изменения заказа:\n\n{str(ex)}"
            )