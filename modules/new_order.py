import flet as ft
from database import Database, Order
import config
import re
from modules.dialog_manager import DialogManager

class NewOrderPage():
    def __init__(self, page: ft.Page, user):
        self.db = Database()
        self.user = user
        self.db.connect()
        self.page = page
        self.title = "Новый заказ"
        self.padding = 20
        self.spacing = 10
        self.build()

    def build(self):
        self.page.floating_action_button = None
        self.validation_text = ft.Text("", color=ft.Colors.RED, size=12)
        self.validation_view = ft.Row(
            controls=[
                ft.Icon(ft.Icons.ERROR, color=ft.Colors.RED),
                self.validation_text
            ],
            visible=False
        )
        self.article_input = ft.TextField(
            label="Артикул",
            on_change=self.validate_article,
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
            expand=1
        )
        self.address_input = ft.TextField(
            label="Адрес пункта выдачи", 
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
            color=ft.Colors.BLACK,
            border_color=ft.Colors.BLACK,
            focused_border_color=ft.Colors.BLACK,
            label_style=ft.TextStyle(color=ft.Colors.BLACK), 
            expand=True,
            cursor_color=ft.Colors.BLACK
            )
        self.submit_button = ft.ElevatedButton(
            text="Создать заказ", 
            on_click=self.create_order, 
            bgcolor="#2E8B57", 
            color="#FFFFFF",             
            )

        header = ft.Container(
            content=ft.Row(
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
                    ft.Text("Добавление нового заказа", size=24, weight=ft.FontWeight.BOLD),
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
                    self.submit_button,
                ],
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.START,
                spacing=15,
                scroll=ft.ScrollMode.AUTO
            ),
            bgcolor=ft.Colors.WHITE,
            padding=20
        )
 
    def validate_inputs(self):
        """Валидация всех полей формы"""
        return (
            self.validate_article(None) and
            self.validate_adress(None) and
            self.validate_date(None)
        )
            
    def validate_date(self, e):
        """Валидация поля даты заказа и даты выдачи"""
        try:
            date_order = self.date_order.value
            date_deliver = self.date_deliver.value        
            pattern = r'^\d{4}-\d{2}-\d{2}$'     

            if not date_order or not bool(re.match(pattern, date_order)):
                self.validation_text.value = "Неверный формат даты заказа. Используйте ГГГГ-ММ-ДД."                
                self.validation_view.visible = True
                self.page.update()
                return False
            
            if not date_deliver or not bool(re.match(pattern, date_deliver)):
                self.validation_text.value = "Неверный формат даты выдачи. Используйте ГГГГ-ММ-ДД."                
                self.validation_view.visible = True
                self.page.update()
                return False
            
            if date_deliver < date_order:
                self.validation_text.value = "Дата доставки не может быть раньше даты заказа."                
                self.validation_view.visible = True
                self.page.update()
                return False
            
            self.validation_view.visible = False
            self.page.update()
            return True
        except Exception as ex:
            self.validation_text.value = f"Ошибка при проверке даты: {str(ex)}"
            self.validation_view.visible = True
            self.page.update()
            return False

    def validate_adress(self, e):
        """Валидация поля адреса пункта выдачи заказа"""
        try:
            if not self.address_input.value or self.address_input.value.strip() == '':
                self.validation_text.value = "Укажите адрес пункта выдачи."                
                self.validation_view.visible = True
                self.page.update()
                return False
            
            pattern = r'^\d{6}, г\. [А-ЯЁ][а-яё]+, ул\. [0-9А-ЯЁ][0-9А-ЯЁа-яё\s]+, \d+$'     

            if not bool(re.match(pattern, self.address_input.value)):
                self.validation_text.value = "Неверный формат адреса. Пример: 123456, г. Город, ул. Улица, 12"                
                self.validation_view.visible = True
                self.page.update()
                return False
            
            self.validation_view.visible = False
            self.page.update()
            return True
        except Exception as ex:
            self.validation_text.value = f"Ошибка при проверке адреса: {str(ex)}"
            self.validation_view.visible = True
            self.page.update()
            return False

    def validate_article(self, e):
        """Валидация поля артикула заказа"""
        # try:
        #     if not self.article_input.value or self.article_input.value.strip() == '':
        #         self.validation_text.value = "Укажите артикул."                
        #         self.validation_view.visible = True
        #         self.page.update()
        #         return False
            
        #     self.article_input.value = self.article_input.value.upper()
        #     article = self.article_input.value
            
        #     pattern = r'^[A-Z]\d+[A-Z]\d\s*,\s*\d+\s*,\s*[A-Z]\d+[A-Z]\d\s*,\s*\d+$'
            
        #     if not re.match(pattern, article):
        #         self.validation_text.value = "Неверный формат артикула. Пример: А112Т4, 2, F635R4, 2"                
        #         self.validation_view.visible = True
        #         self.page.update()
        #         return False
            
        #     self.validation_view.visible = False
        #     self.page.update()
        #     return True
        # except Exception as ex:
        #     self.validation_text.value = f"Ошибка при проверке артикула: {str(ex)}"
        #     self.validation_view.visible = True
        #     self.page.update()
        #     return False

    def create_order(self, e):
        """Создание нового заказа с полной обработкой ошибок"""
        try:
            if not self.status_drop_down.value:
                DialogManager.show_error_dialog(
                    self.page,
                    "Ошибка валидации",
                    "Выберите статус заказа."
                )
                return
            
            if not self.address_input.value or self.address_input.value.strip() == '':
                DialogManager.show_error_dialog(
                    self.page,
                    "Ошибка валидации",
                    "Укажите адрес пункта выдачи."
                )
                return
            
            if not self.date_deliver.value or self.date_deliver.value.strip() == '':
                DialogManager.show_error_dialog(
                    self.page,
                    "Ошибка валидации",
                    "Укажите дату доставки."
                )
                return
            
            if not self.date_order.value or self.date_order.value.strip() == '':
                DialogManager.show_error_dialog(
                    self.page,
                    "Ошибка валидации",
                    "Укажите дату заказа."
                )
                return
            
            # if not self.validate_inputs():
            #     DialogManager.show_error_dialog(
            #         self.page,
            #         "Ошибка валидации",
            #         "Пожалуйста, проверьте заполнение всех полей.\n\nУбедитесь, что:\n• Номер заказа фоотвествует формату\n• Адрес введен корректно\n• Даты соответствуют формату\n• Дата доставки не раньше даты заказаn\n• Адрес пункта выдачи соответствует формату"
            #     )
            #     return
            
            result = self.db.add_order(
                self.article_input.value, 
                self.status_drop_down.value, 
                self.address_input.value, 
                self.date_order.value, 
                self.date_deliver.value
            )
            print(result)
            
            DialogManager.show_success_dialog(
                self.page,
                "Успешно",
                "Заказ успешно создан!",
                on_close=lambda: self.page.go("/orders")
            )
            
        except Exception as ex:
            DialogManager.show_error_dialog(
                self.page,
                "Ошибка при создании заказа",
                f"При сохранении заказа произошла ошибка:\n\n{str(ex)}"
            )