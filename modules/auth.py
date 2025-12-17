import flet as ft
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import Database, User
from modules.dialog_manager import DialogManager

class LoginPage:
    def __init__(self, page: ft.Page):
        self.page = page
        self.db = Database()
        try:
            self.db.connect()
        except Exception as ex:
            DialogManager.show_error_dialog(
                self.page,
                "Ошибка подключения",
                f"Не удалось подключиться к базе данных: {str(ex)}"
            )
        
        self.username_field = ft.TextField(
            label="Логин",
            width=300,
            autofocus=True,
            color=ft.Colors.BLACK,
            border_color=ft.Colors.BLACK,
            focused_border_color=ft.Colors.BLACK,
            label_style=ft.TextStyle(color=ft.Colors.BLACK),
            cursor_color=ft.Colors.BLACK
        )
        self.password_field = ft.TextField(
            label="Пароль",
            width=300,
            password=True,
            can_reveal_password=True,
            color=ft.Colors.BLACK,
            border_color=ft.Colors.BLACK,
            focused_border_color=ft.Colors.BLACK,
            label_style=ft.TextStyle(color=ft.Colors.BLACK), 
            cursor_color=ft.Colors.BLACK
        )
    
    def build(self):
        """Построение интерфейса страницы входа"""
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Вход в систему", size=24, weight=ft.FontWeight.BOLD),
                    ft.Container(height=20),
                    self.username_field,
                    self.password_field,
                    ft.ElevatedButton(                           
                        text="Войти",
                        on_click=self.login_click,
                        bgcolor="#00FA9A",
                        color="#ffffff",
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(5)
                        ),
                        width=300
                    ),
                    ft.ElevatedButton(
    text="Войти как гость",
    on_click=self.guest_login_click,
    bgcolor="#00FA9A",
    color="#ffffff",
    style=ft.ButtonStyle(
        shape=ft.RoundedRectangleBorder(5)
    ),
    width=300
)
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            padding=50,
            alignment=ft.alignment.center
        )
    
    
    def login_click(self, e):
        """Обработка входа по логину/паролю"""
        try:
            username = self.username_field.value.strip()
            password = self.password_field.value
            
            # Валидация входных данных
            if not username:
                DialogManager.show_error_dialog(
                    self.page,
                    "Ошибка входа",
                    "Пожалуйста, введите логин."
                )
                return
            
            if not password:
                DialogManager.show_error_dialog(
                    self.page,
                    "Ошибка входа",
                    "Пожалуйста, введите пароль."
                )
                return
            
            # Попытка получить пользователя
            user_data = self.db.get_user_with_credentials(username, password)
            
            if not user_data:
                DialogManager.show_error_dialog(
                    self.page,
                    "Ошибка входа",
                    "Неверный логин или пароль.\n\nПожалуйста, проверьте введенные данные и попробуйте снова."
                )
                # Очищаем поля
                self.password_field.value = ""
                self.page.update()
                return
            
            user = User(user_data)
            
            # Показываем сообщение об успешном входе
            DialogManager.show_success_dialog(
                self.page,
                "Успешный вход",
                f"Добро пожаловать, {user.name}!",
                on_close=lambda: self.navigate_to_main_app(user)
            )
            
        except Exception as ex:
            DialogManager.show_error_dialog(
                self.page,
                "Ошибка при входе",
                f"При попытке входа произошла непредвиденная ошибка:\n\n{str(ex)}"
            )
    
    def guest_login_click(self, e):
        """Обработка входа как гостя"""
        try:
            user = User({
                'Роль сотрудника': 'Гость',
                'ФИО': 'Гость',
                'Логин': 'guest',
                'Пароль': ''
            })
            
            DialogManager.show_info_dialog(
                self.page,
                "Вход как гость",
                "Вы вошли в режиме гостя.\n\nВ этом режиме доступны только просмотр товаров.",
                on_close=lambda: self.navigate_to_main_app(user)
            )
            
        except Exception as ex:
            DialogManager.show_error_dialog(
                self.page,
                "Ошибка входа как гость",
                f"При входе как гость произошла ошибка:\n\n{str(ex)}"
            )
    
    def navigate_to_main_app(self, user):
        """Переход к главному приложению"""
        try:
            from modules.product_list import ProductListPage
            
            self.page.client_storage.set("current_user", user.to_dict())
            
            self.page.clean()
            product_page = ProductListPage(self.page, user)
            self.page.add(product_page.build())
            self.page.update()
            
        except Exception as ex:
            DialogManager.show_error_dialog(
                self.page,
                "Ошибка навигации",
                f"При переходе к главному приложению произошла ошибка:\n\n{str(ex)}"
            )

