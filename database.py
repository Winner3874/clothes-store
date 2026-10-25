
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
    """建立資料庫連線。"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
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
