
import sqlite3
from pathlib import Path

# 資料庫檔案放在目前專案的根目錄
DB_PATH = Path(__file__).resolve().parent / "store.db"


# 第一次建立資料庫時使用的範例商品
INITIAL_PRODUCTS = [
    ("極簡機械鍵盤", 2500, "手感極佳的青軸機械鍵盤", "⌨️"),
    ("無線電競滑鼠", 1200, "超低延遲、人體工學設計", "🖱️"),
    ("抗噪藍牙耳機", 3800, "沉浸式音質，主動降噪功能", "🎧"),
    ("4K 護眼螢幕", 8900, "27 吋 IPS 面板，色彩精準", "🖥️"),
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
                image TEXT NOT NULL DEFAULT ''
            )
        """)

                # 訂單主表
        conn.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                total INTEGER NOT NULL CHECK (total >= 0),
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

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
                    (name, price, description, image)
                VALUES (?, ?, ?, ?)
            """, INITIAL_PRODUCTS)


def get_all_products():
    """取得所有商品。"""
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT
                id,
                name,
                price,
                description AS desc,
                image AS img
            FROM products
            ORDER BY id
        """).fetchall()

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
                image AS img
            FROM products
            WHERE id = ?
        """, (product_id,)).fetchone()

        return dict(row) if row else None


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


def create_order(cart):
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
            INSERT INTO orders (total, status)
            VALUES (?, 'pending')
        """, (total,))

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
