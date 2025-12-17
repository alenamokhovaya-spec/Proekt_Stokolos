import flet as ft
import config
from database import Database, Order

class OrdersPage:
    def __init__(self, page: ft.Page, user):
        self.page = page
        self.user = user
        self.db = Database()
        self.db.connect()
        self._orders = []
        self.orders = []
        self.load_orders()

    def build(self):
        self.page.title = "ООО «Обувь» - Заказы"
        self.orders_grid_ref = ft.Ref[ft.Column]()
        self.allow_admin_features = self.user.role == 'Администратор'

        header = ft.Container(
            content = 
            ft.Row(
                controls=[
                    ft.IconButton(
                        icon=ft.Icons.ARROW_BACK,
                        tooltip="Назад",
                        on_click=lambda e: self.page.go("/catalog"),
                        icon_color=ft.Colors.BLACK
                    ),
                    ft.Text("Заказы", size=24, weight=ft.FontWeight.BOLD),

                    ft.Container(expand=True),
                    ft.Text(self.user.name),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            padding=10
        )
        self.page.floating_action_button = ft.FloatingActionButton(
            text="Добавить заказ",
            tooltip="Добавить заказ",
            on_click=lambda e: self.new_order_click(e),
            focus_color="#00FA9A",
            foreground_color="#FFFFFF",
            bgcolor="#00FA9A",
            width=180
        ) if self.allow_admin_features else None
        
        orders_grid = self.create_orders_grid()

        return ft.Container(
            content=ft.Column(
                controls=[
                    header,
                    ft.Divider(), 
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.TextButton(      
                                    on_click=lambda e: self.page.go("/catalog"),
                                    content=ft.Text("Перейти к каталогу", color="#2E8B57", size=24),
                                    expand=1
                                ),  
                            ]
                        )
                    ),
                    orders_grid
                    ]
            ),
            bgcolor="#FFFFFF",
        )
    
    def load_orders(self):
        """Загрузка заказов из базы данных"""
        self._orders = self.db.get_all_orders()
        self.orders = self._orders.copy()

    def create_orders_grid(self):
        """Создание сетки заказов"""
        if not self.orders:
            return ft.Text("Нет заказов для отображения.")  
        order_items = [self.create_order_item(order) for order in self.orders]
        return ft.Column(
            ref=self.orders_grid_ref,
            controls=order_items,
            spacing=10,
            run_spacing=10,
        )
    def new_order_click(self, e):
         """Переход на страницу создания нового заказа"""
         self.page.go("/orders/new")

    def edit_order(self, order):
        if self.allow_admin_features:
            self.page.go(f"/orders/{order.id}")
        else:
            pass
                    
    def create_order_item(self, order):
        """Создание элемента заказа для отображения в списке заказов"""
        return ft.Container(
            content=ft.Card(
                content=ft.Container(
                    content=
                    ft.Row(
                        controls=[
                            ft.Column(
                                controls=[
                                    ft.Text(
                                        order.article,
                                        size=16,
                                        weight=ft.FontWeight.BOLD, 
                                        color=ft.Colors.BLACK),
                                    ft.Text(
                                        order.status,
                                        size=14,
                                        weight=ft.FontWeight.NORMAL,
                                        color=ft.Colors.BLACK),
                                    ft.Text(
                                        order.pick_up_point,
                                        size=14,
                                        weight=ft.FontWeight.NORMAL,
                                        color=ft.Colors.BLACK),
                                    ft.Text(
                                        order.date_order,
                                        size=14,
                                        weight=ft.FontWeight.NORMAL,
                                        color=ft.Colors.BLACK),
                                
                                ],
                                spacing=5,
                                ),
                            ft.Text(
                                order.date_delivery,
                                size=22,
                                weight=ft.FontWeight.BOLD,
                            )
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ), 
                    on_hover=lambda e: (
                        setattr(e.control, "bgcolor", "#7FFF00") if e.data == "true" else setattr(e.control, "bgcolor", None),
                        e.control.update()
                    ),
                    padding=10
                ),
                shape=ft.RoundedRectangleBorder(0),
                color="#FFFFFF",
                elevation=4,
                margin=10
            ),
            padding=5,
            on_click=lambda e, order=order: self.edit_order(order)
        
    )
    