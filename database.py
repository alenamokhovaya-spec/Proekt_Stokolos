import psycopg2
from psycopg2.extras import RealDictCursor
import config
import random, string
class User:
    def __init__(self, data):
        self.role = data.get('Роль сотрудника')
        self.name = data.get('ФИО')
        self.login = data.get('Логин')
        self.password = data.get('Пароль')
    
    def to_dict(self):
        return {
            'Роль сотрудника': self.role,
            'ФИО': self.name,
            'Логин': self.login,
            'Пароль': self.password,
        }
    
class Product:
    def __init__(self, data):
        self.tovar_id = data.get("tovar_id")
        self.article = data.get('Артикул')
        self.name = data.get('Наименование товара')
        self.unit = data.get('Единица измерения')
        self.price = float(data.get('Цена', 0))
        self.supplier = data.get('Поставщик')
        self.manufacturer = data.get('Производитель')
        self.category = data.get('Категория товара')
        self.discount = data.get('Действующая скидка')
        self.stock = data.get('Кол-во на складе')
        self.description = data.get('Описание товара')
        self.photo = data.get('Фото')
        self.final_price = float(data.get('Финальная цена', 0))
    
    def to_dict(self):
        return {
            'tovat_id': self.tovar_id,
            'Артикул': self.article,
            'Наименование товара': self.name,
            'Единица измерения': self.unit,
            'Цена': self.price,
            'Поставщик': self.supplier,
            'Производитель': self.manufacturer,
            'Категория товара': self.category,
            'Действующая скидка': self.discount,
            'Кол-во на складе': self.stock,
            'Описание товара': self.description,
            'Фото': self.photo,
        }

class Order:
    def __init__(self, data):
        db = Database()
        db.connect()
        self.id = data.get('Номер заказа')
        self.article = db.get_order_article(self.id)
        self.date_order = data.get('Дата заказа')
        self.date_delivery = data.get('Дата доставки')
        self.pick_up_point = db.get_pick_up_point_with_id(data.get('Адрес пункта выдачи'))
        self.customer = data.get('ФИО авторизованного клиента')
        self.code = data.get('Код получения')
        self.status = data.get('Статус заказа')
        
    
    def to_dict(self):
        return {
            'Номер заказа': self.id,
            'Артикул заказа': self.article,
            'Дата заказа': self.date_order,
            'Дата доставки': self.date_delivery,
            'Адрес пункта выдачи': self.pick_up_point,
            'ФИО авторизованного клиента': self.customer,
            'Код получения': self.code,
            'Статус заказа': self.status
        }
    
   
    
    
class Database:
    def __init__(self):
        self.connection = None
    
    def connect(self):
        try:
            self.connection = psycopg2.connect(**config.DB_CONFIG)
            return True
        except Exception as e:
            print(f"Ошибка подключения к БД: {e}")
            return False
        
    def execute_query(self, query, params=None):
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                if query.strip().upper().startswith('SELECT') or ('RETURNING' in query.upper()):
                    return cursor.fetchall()
                else:
                    self.connection.commit()
                    return cursor.rowcount
        except Exception as e:
            print(f"Ошибка выполнения запроса: {e}")
            return None
    
    def get_user_with_credentials(self, username, password):
        """Проверка логина и пароля пользователя"""
        query = f'''
        SELECT * FROM users u
	        WHERE u."Логин" = '{username}'
	        AND u."Пароль" = '{password}';
        '''
        result = self.execute_query(query, (username, password))
        return result[0] if result else None
    
    def get_all_products(self):
        """Получение всех товаров с финальными ценами"""
        query = """
        SELECT t.*,
            CASE 
                WHEN t."Действующая скидка" > 0 
                    THEN ROUND(t."Цена" * (1 - CAST(t."Действующая скидка" AS NUMERIC) / 100))
                ELSE t."Цена"
            END as "Финальная цена"
        FROM tovar t;
        """
        result = self.execute_query(query)
        return [Product(row) for row in result] if result else []
    
    def get_all_orders(self):
        """Получение всех заказов"""
        query = """
        SELECT o.* FROM orders o;
        """
        result = self.execute_query(query)
        return [Order(row) for row in result] if result else []
    
    def get_all_pick_up_points(self):
        """Получение всех пунктов выдачи"""
        query = """
        SELECT p.* FROM order_pick_up_points p;
        """
        result = self.execute_query(query)
        return result if result else []
    
    def add_order(self, article, status, pick_up_point_adress, date_order, date_delivery):
        """Добавление нового заказа"""
        try:
            pick_up_point_adress_id = self.get_pick_up_point(pick_up_point_adress)
            print(pick_up_point_adress_id)

            if not pick_up_point_adress_id:
                pick_up_point_adress_id = self.create_pick_up_point_and_get_id(pick_up_point_adress)    
            
            if not pick_up_point_adress_id:
                raise ValueError("Не удалось создать пункт выдачи.")
            
            query = """
            INSERT INTO orders ("Дата заказа", "Дата доставки", "Адрес пункта выдачи", "Статус заказа")
            VALUES (%s, %s, %s, %s)
            RETURNING "Номер заказа";
            """
        
            params = (date_order, date_delivery, pick_up_point_adress_id, status)
            result = self.execute_query(query, params)
            
            if not result:
                raise Exception("Не удалось создать заказ в БД.")
            
            order_id = result[0].get('Номер заказа')
            print(f"Order created with ID: {order_id}")
            
            self.generate_values_orders_articles(article, order_id)
            
            return order_id
            
        except Exception as e:
            print(f"Ошибка при создании заказа: {str(e)}")
            raise 

    def generate_values_orders_articles(self, article: str, order_id: int): 
        """Генерирует записи товаров в заказе"""
        parts = [s.strip() for s in article.split(',')]

        tovar_ids = []
        amounts = []
        
        try:
            if len(parts) % 2 != 0:
                raise ValueError("Неверный формат артикула. Должны чередоваться артикулы и количества.")
            
            for i, part in enumerate(parts):
                if i % 2 == 0:  # Артикул
                    part_tovar = part
                    print(f"{part_tovar} checking...")
                    
                    tovar = self.get_product_by_article(part_tovar)
                    if not tovar or not tovar.tovar_id:
                        raise ValueError(f"Товара с артикулом '{part_tovar}' не существует.")
                    
                    tovar_ids.append(tovar.tovar_id)
                else:  
                    try:
                        amount = int(part)
                        if amount <= 0:
                            raise ValueError(f"Количество должно быть положительным числом, получено: {amount}")
                        amounts.append(amount)
                    except ValueError as ve:
                        raise ValueError(f"Неверный формат количества '{part}': {str(ve)}")
            
            for tovar_id, amount in zip(tovar_ids, amounts):
                self.update_orders_articles(tovar_id, order_id, amount)
                print(f"Added tovar_id={tovar_id}, amount={amount} to order {order_id}")
        
        except Exception as e:
            print(f"Ошибка при генерировании товаров заказа: {str(e)}")
            raise 

    def update_orders_articles(self, article, order_id, amount):
        query = """
                INSERT INTO orders_articles ("Номер заказа", "tovar_id", "Количество") VALUES (%s,%s,%s);
        """
        self.execute_query(query, (order_id, article, amount))

    def get_pick_up_point_with_id(self, pick_up_point):
        """Получение адреса пункта выдачи по ID"""
        query = """
        SELECT p.* FROM order_pick_up_points p
        WHERE p."point_id" = %s;
        """
        rows = self.execute_query(query, (pick_up_point,))
        if not rows:
            return None
        result = rows[0]
        return result.get("Адрес")
    
    def get_pick_up_point(self, adress): 
        """Получение пункта выдачи по адресу"""
        print(adress)
        query = """
        SELECT p.* FROM order_pick_up_points
        WHERE "Адрес" = %s;
        """
        rows = self.execute_query(query, str(adress))
        if not rows:
            return None
        result = rows[0]
        return result.get("point_id")
    
    def create_pick_up_point_and_get_id(self, adress):
        """Создание нового пункта выдачи и получение его ID"""
        query = """
        INSERT INTO order_pick_up_points ("Адрес") VALUES (%s) RETURNING "point_id";
        """
        result = self.execute_query(query, (adress,))

        if not result:
            return None
        return result[0].get('point_id')
   

    def add_product(self, name, unit, price, supplier, manufacturer, category, discount, stock, description, photo_path):
        def generate_article():
            first_char = random.choice(string.ascii_uppercase)
            
            three_digits = f"{random.randint(0, 999):03d}"
            
            second_char = random.choice(string.ascii_uppercase)
            
            last_digit = random.randint(1, 9)
            
            return f"{first_char}{three_digits}{second_char}{last_digit}"

        article = generate_article()
        query = """
            INSERT INTO tovar (
                "Артикул",
                "Наименование товара",
                "Единица измерения",
                "Цена",
                "Поставщик",
                "Производитель",
                "Категория товара",
                "Действующая скидка",
                "Кол-во на складе",
                "Описание товара",
                "Фото"
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        params = (
            article, name, unit, price, supplier, manufacturer, 
            category, discount, stock, description, photo_path
        )
        self.execute_query(query, params)

    def get_product_by_article(self, article):
        query = 'SELECT * FROM tovar t WHERE t."Артикул" = %s;'
        rows = self.execute_query(query, (article,))
        if not rows:
            return None
        return Product(rows[0])
    
    def get_product(self, tovar_id):
        query = 'SELECT * FROM tovar t WHERE t."tovar_id" = %s;'
        rows = self.execute_query(query, (tovar_id,))
        if not rows:
            return None
        return Product(rows[0])
    
    def delete_product(self, tovar_id):
        """Удаление товара с проверкой наличия в заказах"""
        try:
            check_query = """
            SELECT COUNT(*) as count FROM orders_articles oa
            WHERE oa."tovar_id" = %s;
            """
            result = self.execute_query(check_query, (tovar_id,))
            
            if result and result[0].get('count', 0) > 0:
                raise ValueError(
                    f"Не удалось удалить товар. Товар находится в {result[0]['count']} заказе(ах). "
                    "Сначала удалите товар из всех заказов."
                )
            
            delete_query = 'DELETE FROM tovar WHERE "tovar_id" = %s;'
            self.execute_query(delete_query, (tovar_id,))
            
            return True
            
        except ValueError as ve:
            print(f"Ошибка валидации: {str(ve)}")
            raise
        except Exception as e:
            print(f"Ошибка при удалении товара: {str(e)}")
            raise
    
    def get_order(self, order_id):
        query = 'SELECT * FROM orders o WHERE o."Номер заказа" = %s;'
        rows = self.execute_query(query, (order_id,))
        if not rows:
            return None
        return Order(rows[0])
    
    def get_order_article(self, order_id):
        query = '''
        SELECT oa.*, t."Наименование товара", t."Артикул" FROM orders_articles oa
        JOIN tovar t ON oa."tovar_id" = t."tovar_id"
        WHERE oa."Номер заказа" = %s;
        '''
        rows = self.execute_query(query, (order_id,))
        if not rows:
            return []
        article = ""
        for row in rows:
            article += f"{row['Артикул']}, {row['Количество']}, "
        article = article.rstrip(", ")
        return article
    
    def delete_order(self, order_id):
        query = """
        DELETE FROM orders o WHERE o."Номер заказа" = %s;
        """
        result = self.execute_query(query, (order_id,))
        print(result)
        return result

    def update_product(self, tovar_id, name, unit, price, supplier, manufacturer, category, discount, stock, description, photo_path):
        query = """
            UPDATE tovar
            SET 
                "Наименование товара" = %s,
                "Единица измерения" = %s,
                "Цена" = %s,
                "Поставщик" = %s,
                "Производитель" = %s,
                "Категория товара" = %s,
                "Действующая скидка" = %s,
                "Кол-во на складе" = %s,
                "Описание товара" = %s,
                "Фото" = %s
            WHERE "tovar_id" = %s;
        """
        params = (
            name, unit, price, supplier, manufacturer, 
            category, discount, stock, description, photo_path,
            tovar_id
        )
        self.execute_query(query, params)
    
    def update_order(self, order_id, article, date_order, date_delivery, pick_up_point_adress, status):
        """Обновление заказа с обработкой ошибок"""
        try:
            pick_up_point_adress_id = self.get_pick_up_point(pick_up_point_adress)
            if not pick_up_point_adress_id:
                pick_up_point_adress_id = self.create_pick_up_point_and_get_id(pick_up_point_adress)    
            
            if not pick_up_point_adress_id:
                raise ValueError("Не удалось создать пункт выдачи.")
            
            update_query = """
            UPDATE orders
            SET 
                "Дата заказа" = %s,
                "Дата доставки" = %s,
                "Адрес пункта выдачи" = %s,
                "Статус заказа" = %s
            WHERE "Номер заказа" = %s;
            """
            params = (date_order, date_delivery, pick_up_point_adress_id, status, order_id)
            self.execute_query(update_query, params)
            
            self.generate_values_orders_articles(article, order_id)
            
            return True
            
        except Exception as e:
            print(f"Ошибка при обновлении заказа: {str(e)}")
            raise

# db = Database()
# if not db.connect():
#     print("Не удалось подключиться к базе данных.")
# else:
#     e = db.get_orders_articles(1)
#     print(e)