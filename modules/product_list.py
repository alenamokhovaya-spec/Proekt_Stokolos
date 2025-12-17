import flet as ft
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import Database
from modules.dialog_manager import DialogManager
import config

class ProductListPage:
    def __init__(self, page: ft.Page, user):
        self.page = page
        self.user = user
        self.db = Database()
        self.db.connect()
        self.products = []
        self.search_query = ""
        self.page.title = "ООО «Обувь» - магазин по продаже обуви"
        self.filter_by_manufacturer = 'Все производители'
        self.filter_by_supplier = 'Все поставщики'
        self.sort_by_stock = 'Нет'

    def build(self):
        """Построение интерфейса списка товаров"""
        self.load_products()
        self.filtered_products = self.products.copy()
        self.products_grid_ref = ft.Ref[ft.Column]()
        allow_manager_features = self.user.role in ['Менеджер', 'Администратор']
        self.allow_admin_features = self.user.role == 'Администратор'

        self.page.floating_action_button = ft.FloatingActionButton(
            text="Добавить товар",
            tooltip="Новый товар",
            on_click=lambda e: self.create_new_product_click(e),
            focus_color="#00FA9A",
            foreground_color="#FFFFFF",
            bgcolor="#00FA9A",
            width=180,
        ) if self.allow_admin_features else None

        header = ft.Container(
            content = 
            ft.Row(
                controls=[
                    ft.Image(src=config.LOGO_IMAGE, width=40, height=40, fit=ft.ImageFit.CONTAIN,),
                    ft.Text("Каталог", size=24, weight=ft.FontWeight.BOLD) ,
                    
                    ft.Container(expand=True),
                    ft.Text(self.user.name),
                    ft.TextButton(
                        icon=ft.Icons.LOGOUT,
                        icon_color=ft.Colors.BLACK,
                        on_click=self.logout_click,
                    )
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            padding=10
        )
      
        products_grid = self.create_products_grid()
        search_bar = self.search_bar() if allow_manager_features else ft.Container()
        return ft.Container(
            bgcolor="#FFFFFF",
            content=ft.Column(
                controls=[
                    header,
                    ft.Divider(),
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.TextButton(      
                                on_click=lambda e: self.page.go("/orders"),
                                content=ft.Text("Перейти к заказам", color="#2E8B57", size=24),
                                expand=1,
                                
                                ) if allow_manager_features else ft.Container(),  
                            ]
                        )
                    ),
                    search_bar,
                    products_grid
                ],
                scroll=ft.ScrollMode.ALWAYS
            ),            
           
        )
    def edit_product(self, product):
        if self.allow_admin_features:
            self.page.go(f"/catalog/{product.tovar_id}")
        else:
            pass

    def create_new_product_click(self, e):
         """Переход на страницу создания нового продукта"""
         self.page.go("/catalog/new")

    def set_filter_by_supplier(self, option):
        self.filter_by_supplier = option
        self.filter_products()
    
    def set_sort_by_stock(self, option):
        self.sort_by_stock = option
        self.filter_products()

    def filter_products(self, e=None):
        """Фильтрация товаров и поиск"""
        self.search_query = e.control.value if e else self.search_query
        self.filtered_products = self.products.copy()
        
        if self.search_query:
            search_words = self.search_query.lower().split()
            
            self.filtered_products = [
                product for product in self.products
                if all(
                    any(
                        word in (getattr(product, field) or "").lower()
                        for field in ['name', 'category', 'manufacturer', 'supplier', 'description', 'article']
                    )
                    for word in search_words
                )
            ]
        
        if self.filter_by_supplier != "Все поставщики":
            self.filtered_products = [
                p for p in self.filtered_products
                if p.supplier == self.filter_by_supplier
            ]
        
        if self.sort_by_stock == "По возрастанию":
            self.filtered_products.sort(key=lambda p: p.stock)
        elif self.sort_by_stock == "По убыванию":
            self.filtered_products.sort(key=lambda p: p.stock, reverse=True)
        
        self.update_products_grid()


    def load_products(self):
        """Загрузка товаров из БД"""
        try:
            self.products = self.db.get_all_products()
            if not self.products:
                DialogManager.show_info_dialog(
                    self.page,
                    "Информация",
                    "В каталоге нет товаров."
                )
        except Exception as ex:
            DialogManager.show_error_dialog(
                self.page,
                "Ошибка загрузки товаров",
                f"Не удалось загрузить товары из базы данных: {str(ex)}"
            )
    
    def search_bar(self):
        """Создание строки поиска и фильтрации"""
        suppliers_ = [p.supplier for p in self.products]
        suppliers = []
        suppliers.append("Все поставщики")
        for supplier in suppliers_:
            if supplier not in suppliers:
                suppliers.append(supplier)

        return ft.Container(
            content=(
                ft.Row(
                    controls=[
                        ft.TextField(
                            label="Поиск товаров",
                            value=self.search_query,
                            on_change=lambda e: self.filter_products(e),
                            hint_text="Введите название или категорию товара",
                            color=ft.Colors.BLACK,
                            border_color=ft.Colors.BLACK,
                            focused_border_color=ft.Colors.BLACK,
                            label_style=ft.TextStyle(color=ft.Colors.BLACK), 
                            expand=True,
                            cursor_color=ft.Colors.BLACK
                        ),
                        ft.DropdownM2(
                        width=180,
                        value=self.sort_by_stock,
                        options=[
                            ft.dropdown.Option("Нет"),
                            ft.dropdown.Option("По возрастанию"),
                            ft.dropdown.Option("По убыванию")
                        ],
                        on_change=lambda e: self.set_sort_by_stock(e.control.value),
                        label="По количеству на складе",
                        expand=True, 
                        color=ft.Colors.BLACK,
                        border_color=ft.Colors.BLACK,
                        focused_border_color=ft.Colors.BLACK,
                        label_style=ft.TextStyle(color=ft.Colors.BLACK),    
                        ),
                        ft.DropdownM2(
                        width=180,
                        value=self.filter_by_supplier,
                        options=[ft.dropdown.Option(v) for v in suppliers],
                        on_change=lambda e: self.set_filter_by_supplier(e.control.value),
                        label="Фильтр по поставщику",
                        expand=True,
                        color=ft.Colors.BLACK,
                        border_color=ft.Colors.BLACK,
                        focused_border_color=ft.Colors.BLACK,
                        label_style=ft.TextStyle(color=ft.Colors.BLACK),    
                    
                        ),
                    ]
                )
               
            ),
            padding=10
        )
         
    
    def update_products_grid(self):
        """Обновление отображаемой сетки товаров"""
        if self.products_grid_ref.current:
            self.products_grid_ref.current.controls.clear()
            
            if not self.filtered_products:
                self.products_grid_ref.current.controls.append(
                    ft.Container(
                        content=ft.Text("Товары не найдены", size=16),
                        alignment=ft.alignment.center,
                        padding=20
                    )
                )
            else:
                for product in self.filtered_products:
                    card = self.create_product_card(product)
                    self.products_grid_ref.current.controls.append(card)
            
            self.products_grid_ref.current.update()
        
    def create_products_grid(self):
        """Создание сетки товаров"""
        if not self.products:
            return ft.Text("Товары не найдены")

        product_cards = []
        if not self.filtered_products:
            product_cards.append(
                ft.Container(
                    content=ft.Text("Товары не найдены", size=16),
                    alignment=ft.alignment.center,
                    padding=20
                )
            )
        else:
            for product in self.filtered_products:
                card = self.create_product_card(product)
                product_cards.append(card)
        
        return ft.Column(
            ref=self.products_grid_ref,
            controls=product_cards,
            spacing=10,
            run_spacing=10,
        )
    
    def create_product_card(self, product):
        """Создание карточки товара"""
        bg_color = None
        if product.discount > 15:
            bg_color = "#2E8B57" 
        
        # Обработка изображения
        image_widget = self.create_image_widget(product)
        
        return ft.Card(
            content=ft.Container(
                content=ft.Row(
                    controls=[
                        image_widget,
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text(
                                        f'{product.category} | {product.name}',
                                        size=16,
                                        weight=ft.FontWeight.BOLD,
                                        overflow=ft.TextOverflow.ELLIPSIS,
                                         color=ft.Colors.BLACK,
                                        max_lines=2
                                    ),
                                    ft.Text(
                                        f"Описание товара: {product.description}",
                                        size=14,
                                        weight=ft.FontWeight.NORMAL,
                                        color=ft.Colors.BLACK
                                    ),
                                     ft.Text(
                                        f"Производитель: {product.manufacturer}",
                                        size=14,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.Colors.BLACK
                                    ),
                                    ft.Text(
                                        f"Поставщик: {product.supplier}",
                                        size=14,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.Colors.BLACK
                                    ),
                                   
                                    self.price_widget(product),

                                    ft.Text(
                                        f"Единица измерения: {product.unit}",
                                        size=14,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.Colors.BLACK
                                   ),
                                   ft.Text(
                                        f"Количество на складе: {product.stock}",
                                        size=14,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.Colors.BLACK if product.stock > 0 else ft.Colors.BLUE_ACCENT_400
                                   ),
                                    
                                ],
                                spacing=5,
                                width=400
                            ),
                            padding=10,
                            expand=1
                        ),
                        ft.Text(
                            f"{product.discount}%",
                            size=28,
                            weight=ft.FontWeight.BOLD,
                            color= ft.Colors.BLACK,
                            expand=0,
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                padding=10,
                on_hover=lambda e: (
                    setattr(e.control, "bgcolor", "#7FFF00") if e.data == "true" else setattr(e.control, "bgcolor", bg_color),
                    e.control.update()
                ),
                bgcolor=bg_color,
                border_radius=0,
                on_click=lambda e, product=product: self.edit_product(product)
            ),
            shape=ft.RoundedRectangleBorder(0),
            elevation=5,
            color="#FFFFFF",
            margin=10

        )
    
    def price_widget(self, product):
        if product.discount > 0:
            return ft.Row(
                controls=[
                    ft.Text(
                        spans=[
                            ft.TextSpan(
                                text=f"Цена: ",
                                style=ft.TextStyle(
                                    size=12,
                                    color=ft.Colors.BLACK,
                                )
                            ),
                            ft.TextSpan(
                                text=f"{product.price:.2f}₽ ",
                                style=ft.TextStyle(
                                    decoration=ft.TextDecoration.LINE_THROUGH,
                                    color=ft.Colors.RED_800,
                                )
                            ),
                            ft.TextSpan(
                                text=f"{product.final_price:.2f}₽",
                                style=ft.TextStyle(
                                    size=12,
                                    color=ft.Colors.BLACK,
                                )
                            )
                        ],
                        size=12,
                        text_align=ft.TextAlign.CENTER,
                    )
                ]
            )
        else:
            return ft.Text(
                f"Цена: {product.price:.2f}₽",
                size=14,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.BLACK
            )

    def create_image_widget(self, product):
        if product.photo:
            image_src = os.path.join(config.TOVAR_IMAGES_DIR, product.photo)
        else:
            image_src = config.PLACEHOLDER_IMAGE
        return ft.Container(
            content=ft.Image(
                src=image_src,
                fit=ft.ImageFit.CONTAIN,
                height=150
            ),
            alignment=ft.alignment.center,
        )
    
    def logout_click(self, e):
        def on_confirm():
            self.page.floating_action_button=None
            self.page.client_storage.remove("current_user")
            
            self.page.clean()
            from modules.auth import LoginPage
            login_page = LoginPage(self.page)
            self.page.add(login_page.build())
            self.page.update()
        
        DialogManager.show_warning_dialog(
            self.page,
            "Выход из системы",
            "Вы уверены, что хотите выйти?",
            on_confirm=on_confirm
        )       

