
import sqlite3
from pathlib import Path

# 資料庫檔案放在目前專案的根目錄
DB_PATH = Path(__file__).resolve().parent / "store.db"


# 第一次建立資料庫時使用的範例商品
INITIAL_PRODUCTS = [
    ("經典白襯衫", 1280, "採用舒適透氣的棉質布料，適合日常穿搭。", "👔", "上衣"),
    ("休閒直筒長褲", 1680, "俐落直筒剪裁，搭配襯衫或 T 恤都合適。", "👖", "褲裝"),
    ("輕量連帽外套", 2280, "輕量防風設計，適合換季與戶外活動。", "🧥", "外套"),
    ("帆布日常托特包", 880, "耐用帆布材質，日常收納輕鬆有型。", "👜", "配件"),
]


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """建立商品資料表，並在資料表為空時加入範例商品。"""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price INTEGER NOT NULL CHECK (price >= 0),
                description TEXT NOT NULL DEFAULT '',
                image TEXT NOT NULL DEFAULT '',
                category TEXT NOT NULL DEFAULT '其他'
            )
        """)

        product_columns = {
            row["name"] for row in conn.execute("PRAGMA table_info(products)")
        }
        if "category" not in product_columns:
            conn.execute(
                "ALTER TABLE products ADD COLUMN category TEXT NOT NULL DEFAULT '其他'"
            )

        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE COLLATE NOCASE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS favorites (
                user_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, product_id),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
            )
        """)

                # 訂單主表
        conn.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                total INTEGER NOT NULL CHECK (total >= 0),
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
            )
        """)

        order_columns = {
            row["name"] for row in conn.execute("PRAGMA table_info(orders)")
        }
        if "user_id" not in order_columns:
            conn.execute(
                "ALTER TABLE orders ADD COLUMN user_id INTEGER REFERENCES users(id) ON DELETE SET NULL"
            )

        # 訂單商品明細
        conn.execute("""
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                product_id INTEGER,
                product_name TEXT NOT NULL,
                quantity INTEGER NOT NULL CHECK (quantity > 0),
                unit_price INTEGER NOT NULL CHECK (unit_price >= 0),

                FOREIGN KEY (order_id)
                    REFERENCES orders(id)
                    ON DELETE CASCADE,

                FOREIGN KEY (product_id)
                    REFERENCES products(id)
                    ON DELETE SET NULL
            )
        """)

        count = conn.execute(
            "SELECT COUNT(*) FROM products"
        ).fetchone()[0]

        if count == 0:
            conn.executemany("""
                INSERT INTO products
                    (name, price, description, image, category)
                VALUES (?, ?, ?, ?, ?)
            """, INITIAL_PRODUCTS)


def get_all_products(search="", category=""):
    """取得所有商品。"""
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT
                id,
                name,
                price,
                description AS desc,
                image AS img,
                category
            FROM products
            WHERE (? = '' OR name LIKE ? OR description LIKE ?)
                AND (? = '' OR category = ?)
            ORDER BY id
        """, (search, f"%{search}%", f"%{search}%", category, category)).fetchall()

        return [dict(row) for row in rows]


def get_product_by_id(product_id):
    """根據商品 ID 取得單一商品。"""
    with get_connection() as conn:
        row = conn.execute("""
            SELECT
                id,
                name,
                price,
                description AS desc,
                image AS img,
                category
            FROM products
            WHERE id = ?
        """, (product_id,)).fetchone()

        return dict(row) if row else None


def get_product_categories():
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT DISTINCT category FROM products WHERE category <> '' ORDER BY category"
        ).fetchall()
        return [row["category"] for row in rows]


def create_user(name, email, password_hash):
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (name.strip(), email.strip().lower(), password_hash),
        )
        return cursor.lastrowid


def get_user_by_email(email):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id, name, email, password_hash FROM users WHERE email = ? COLLATE NOCASE",
            (email.strip(),),
        ).fetchone()
        return dict(row) if row else None


def get_user_by_id(user_id):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id, name, email FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        return dict(row) if row else None


def get_favorite_product_ids(user_id):
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT product_id FROM favorites WHERE user_id = ?", (user_id,)
        ).fetchall()
        return {row["product_id"] for row in rows}


def toggle_favorite(user_id, product_id):
    with get_connection() as conn:
        existing = conn.execute(
            "SELECT 1 FROM favorites WHERE user_id = ? AND product_id = ?",
            (user_id, product_id),
        ).fetchone()
        if existing:
            conn.execute(
                "DELETE FROM favorites WHERE user_id = ? AND product_id = ?",
                (user_id, product_id),
            )
            return False

        conn.execute(
            "INSERT INTO favorites (user_id, product_id) VALUES (?, ?)",
            (user_id, product_id),
        )
        return True


def get_favorite_products(user_id):
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT p.id, p.name, p.price, p.description AS desc,
                   p.image AS img, p.category
            FROM favorites f
            JOIN products p ON p.id = f.product_id
            WHERE f.user_id = ?
            ORDER BY f.created_at DESC
        """, (user_id,)).fetchall()
        return [dict(row) for row in rows]


def get_orders_by_user(user_id):
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, total, status, created_at FROM orders WHERE user_id = ? ORDER BY id DESC",
            (user_id,),
        ).fetchall()
        orders = []
        for row in rows:
            order = dict(row)
            items = conn.execute("""
                SELECT product_name, quantity, unit_price
                FROM order_items WHERE order_id = ? ORDER BY id
            """, (order["id"],)).fetchall()
            order["items"] = [dict(item) for item in items]
            orders.append(order)
        return orders


def add_product(name, price, description="", image=""):
    """新增商品，回傳新商品的 ID。"""
    if not name.strip():
        raise ValueError("商品名稱不可為空")

    if price < 0:
        raise ValueError("商品價格不可小於 0")

    with get_connection() as conn:
        cursor = conn.execute("""
            INSERT INTO products
                (name, price, description, image)
            VALUES (?, ?, ?, ?)
        """, (name.strip(), price, description, image))

        return cursor.lastrowid


def create_order(cart, user_id=None):
    """
    根據購物車建立訂單。
    cart 格式：{"1": 2, "3": 1}
    回傳：(order_id, total)
    """

    if not cart:
        raise ValueError("購物車是空的")

    with get_connection() as conn:
        items = []
        total = 0

        # 重新從資料庫讀取商品價格
        for product_id, quantity in cart.items():

            product_id = int(product_id)

            if not isinstance(quantity, int) or quantity <= 0:
                raise ValueError("商品數量不正確")

            product = conn.execute("""
                SELECT id, name, price
                FROM products
                WHERE id = ?
            """, (product_id,)).fetchone()

            if product is None:
                raise ValueError("商品不存在")

            subtotal = product["price"] * quantity
            total += subtotal

            items.append({
                "product_id": product["id"],
                "product_name": product["name"],
                "quantity": quantity,
                "unit_price": product["price"],
            })

        # 建立訂單主表
        cursor = conn.execute("""
            INSERT INTO orders (user_id, total, status)
            VALUES (?, ?, 'pending')
        """, (user_id, total))

        order_id = cursor.lastrowid

        # 建立訂單明細
        conn.executemany("""
            INSERT INTO order_items (
                order_id,
                product_id,
                product_name,
                quantity,
                unit_price
            )
            VALUES (?, ?, ?, ?, ?)
        """, [
            (
                order_id,
                item["product_id"],
                item["product_name"],
                item["quantity"],
                item["unit_price"],
            )
            for item in items
        ])

        return order_id, total


def get_order_details(order_id):
    """取得一筆訂單及其所有商品明細。"""

    with get_connection() as conn:

        # 查詢訂單基本資料
        order = conn.execute("""
            SELECT id, total, status, created_at
            FROM orders
            WHERE id = ?
        """, (order_id,)).fetchone()

        if order is None:
            return None

        # 查詢這筆訂單包含的商品
        rows = conn.execute("""
            SELECT
                product_name,
                quantity,
                unit_price
            FROM order_items
            WHERE order_id = ?
            ORDER BY id
        """, (order_id,)).fetchall()

        items = []

        for row in rows:
            item = dict(row)
            item["subtotal"] = (
                item["quantity"] * item["unit_price"]
            )
            items.append(item)

        return {
            **dict(order),
            "items": items,
        }
