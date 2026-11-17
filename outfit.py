import sqlite3
from pathlib import Path
from flask import Flask, render_template_string, request, jsonify, session

app = Flask(__name__)
app.secret_key = "form_and_field_secret_key"

# 資料庫檔案放在目前專案的根目錄
DB_PATH = Path(__file__).resolve().parent / "store.db"

# 圖片中的「form & field」風格商品 (名稱, 價格, 描述, 圖片URL, 分類)
INITIAL_PRODUCTS = [
    (
        "Everyday Mug",
        28,
        "Speckled stoneware · Oat",
        "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?auto=format&fit=crop&w=600&q=80",
        "Ceramics",
    ),
    (
        "Sunday Throw",
        89,
        "Washed linen · Olive",
        "https://images.unsplash.com/photo-1580301762395-21ce84d00bc6?auto=format&fit=crop&w=600&q=80",
        "Textiles",
    ),
    (
        "Gather Tray",
        48,
        "Solid oak · Natural",
        "https://images.unsplash.com/photo-1615486511484-92e172cc4fe0?auto=format&fit=crop&w=600&q=80",
        "Living",
    ),
    (
        "Forma Vase",
        42,
        "Hand-finished · Terracotta",
        "https://images.unsplash.com/photo-1578749556568-bc2c40e68b61?auto=format&fit=crop&w=600&q=80",
        "Ceramics",
    ),
]


# ==================== 資料庫邏輯 ====================

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """建立商品資料表，並確保載入設計圖的範例商品。"""
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

        conn.execute("""
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                product_id INTEGER,
                product_name TEXT NOT NULL,
                quantity INTEGER NOT NULL CHECK (quantity > 0),
                unit_price INTEGER NOT NULL CHECK (unit_price >= 0),
                FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE SET NULL
            )
        """)

        # 建立預設測試使用者 (ID=1)
        user_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        if user_count == 0:
            conn.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                ("Demo User", "demo@formandfield.com", "hashed_pw"),
            )

        # 檢查是否為空，或是還留著舊版的「經典白襯衫」資料，若是則更新為圖片中的商品
        first_row = conn.execute("SELECT name FROM products ORDER BY id LIMIT 1").fetchone()
        if first_row is None or first_row["name"] == "經典白襯衫":
            conn.execute("DELETE FROM products")
            conn.execute("DELETE FROM sqlite_sequence WHERE name='products'")
            conn.executemany("""
                INSERT INTO products (name, price, description, image, category)
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
    with get_connection() as conn:
        row = conn.execute("""
            SELECT id, name, price, description AS desc, image AS img, category
            FROM products WHERE id = ?
        """, (product_id,)).fetchone()
        return dict(row) if row else None


def get_product_categories():
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT DISTINCT category FROM products WHERE category <> '' ORDER BY category"
        ).fetchall()
        return [row["category"] for row in rows]


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


def create_order(cart, user_id=None):
    if not cart:
        raise ValueError("購物車是空的")

    with get_connection() as conn:
        items = []
        total = 0

        for product_id, quantity in cart.items():
            product_id = int(product_id)
            if not isinstance(quantity, int) or quantity <= 0:
                raise ValueError("商品數量不正確")

            product = conn.execute(
                "SELECT id, name, price FROM products WHERE id = ?", (product_id,)
            ).fetchone()

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

        cursor = conn.execute(
            "INSERT INTO orders (user_id, total, status) VALUES (?, ?, 'pending')",
            (user_id, total),
        )
        order_id = cursor.lastrowid

        conn.executemany("""
            INSERT INTO order_items (order_id, product_id, product_name, quantity, unit_price)
            VALUES (?, ?, ?, ?, ?)
        """, [
            (order_id, item["product_id"], item["product_name"], item["quantity"], item["unit_price"])
            for item in items
        ])

        return order_id, total


# ==================== 前端 UI 模板 (修正破版問題) ====================

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>form & field</title>
    <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-main: #FAF9F5;
            --text-dark: #233B2D;
            --text-muted: #8E938C;
            --accent-green: #244734;
            --border-color: #E6E4DD;
            --card-radius: 16px;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            -webkit-tap-highlight-color: transparent;
        }

        body {
            background-color: #EAE8E1;
            display: flex;
            justify-content: center;
            min-height: 100vh;
            overflow-x: hidden;
        }

        /* 手機外框容器 */
        .app-shell {
            width: 100%;
            max-width: 414px;
            background-color: var(--bg-main);
            min-height: 100vh;
            position: relative;
            padding: 24px 20px 96px 20px;
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.08);
            overflow-x: hidden;
        }

        /* 頂部品牌與購物袋 */
        .top-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 24px;
        }

        .brand-logo {
            font-size: 19px;
            font-weight: 700;
            color: var(--text-dark);
            letter-spacing: -0.4px;
            text-decoration: none;
        }

        .bag-btn {
            position: relative;
            background: none;
            border: none;
            cursor: pointer;
            color: var(--text-dark);
            padding: 4px;
        }

        .bag-badge {
            position: absolute;
            top: -3px;
            right: -5px;
            background-color: var(--accent-green);
            color: #FFFFFF;
            font-size: 11px;
            font-weight: 700;
            width: 18px;
            height: 18px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        /* 主標題區 */
        .hero-title {
            font-size: 32px;
            font-weight: 600;
            color: var(--text-dark);
            letter-spacing: -0.8px;
            line-height: 1.15;
            margin-bottom: 6px;
        }

        .hero-subtitle {
            font-size: 14px;
            color: var(--text-muted);
            margin-bottom: 20px;
        }

        /* 搜尋欄 */
        .search-bar {
            position: relative;
            margin-bottom: 16px;
        }

        .search-bar input {
            width: 100%;
            padding: 14px 44px;
            border-radius: 14px;
            border: 1px solid var(--border-color);
            background-color: #FFFFFF;
            font-size: 14px;
            color: var(--text-dark);
            outline: none;
            transition: border 0.2s;
        }

        .search-bar input::placeholder {
            color: #A9ADA6;
        }

        .search-bar input:focus {
            border-color: var(--accent-green);
        }

        .search-icon {
            position: absolute;
            left: 15px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--text-dark);
            pointer-events: none;
        }

        .filter-icon {
            position: absolute;
            right: 15px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--text-dark);
            cursor: pointer;
        }

        /* 分類膠囊按鈕 */
        .category-pills {
            display: flex;
            gap: 8px;
            overflow-x: auto;
            padding-bottom: 4px;
            margin-bottom: 18px;
            scrollbar-width: none;
        }

        .category-pills::-webkit-scrollbar {
            display: none;
        }

        .pill {
            padding: 8px 16px;
            border-radius: 999px;
            border: 1px solid var(--border-color);
            background-color: #FFFFFF;
            color: var(--text-dark);
            font-size: 13px;
            font-weight: 500;
            text-decoration: none;
            white-space: nowrap;
            transition: all 0.2s;
        }

        .pill.active {
            background-color: var(--accent-green);
            color: #FFFFFF;
            border-color: var(--accent-green);
        }

        /* 數量統計與排序 */
        .meta-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
            font-size: 13px;
            color: var(--text-muted);
        }

        .sort-dropdown {
            font-weight: 600;
            color: var(--text-dark);
            display: flex;
            align-items: center;
            gap: 4px;
            cursor: pointer;
        }

        /* 商品雙欄網格 - 使用 minmax(0, 1fr) 防止長文字撐破欄位 */
        .product-grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 20px 14px;
            width: 100%;
        }

        .product-card {
            display: flex;
            flex-direction: column;
            min-width: 0; /* 關鍵：允許 Flex/Grid 子項目縮小並觸發文字省略 */
        }

        .img-wrapper {
            position: relative;
            width: 100%;
            aspect-ratio: 4 / 4.4;
            border-radius: var(--card-radius);
            overflow: hidden;
            background-color: #EAE7DF;
            margin-bottom: 10px;
            cursor: pointer;
        }

        .img-wrapper img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            display: block;
            transition: transform 0.3s ease;
        }

        .img-wrapper:hover img {
            transform: scale(1.04);
        }

        .emoji-fallback {
            width: 100%;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 54px;
        }

        /* 左上角標籤 (BESTSELLER / NEW) */
        .tag-badge {
            position: absolute;
            top: 10px;
            left: 10px;
            background-color: rgba(255, 255, 255, 0.92);
            color: var(--text-dark);
            font-size: 9px;
            font-weight: 700;
            letter-spacing: 0.6px;
            padding: 4px 8px;
            border-radius: 6px;
            text-transform: uppercase;
        }

        /* 右下角收藏愛心 */
        .heart-btn {
            position: absolute;
            bottom: 10px;
            right: 10px;
            width: 32px;
            height: 32px;
            border-radius: 50%;
            background-color: rgba(255, 255, 255, 0.92);
            border: none;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            box-shadow: 0 2px 6px rgba(0,0,0,0.08);
            transition: transform 0.15s;
        }

        .heart-btn:active {
            transform: scale(0.9);
        }

        .heart-btn svg {
            width: 16px;
            height: 16px;
            stroke: var(--text-dark);
            stroke-width: 2;
            fill: none;
        }

        .heart-btn.favorited svg {
            fill: var(--accent-green);
            stroke: var(--accent-green);
        }

        /* 商品文字與價格 */
        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            gap: 6px;
            margin-bottom: 3px;
            min-width: 0;
        }

        .prod-title {
            font-size: 15px;
            font-weight: 600;
            color: var(--text-dark);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            flex: 1;
            min-width: 0;
        }

        .prod-price {
            font-size: 14px;
            font-weight: 600;
            color: var(--text-dark);
            flex-shrink: 0;
        }

        .prod-desc {
            font-size: 12px;
            color: var(--text-muted);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            width: 100%;
        }

        /* 底部標語 */
        .footer-note {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
            margin-top: 32px;
            font-size: 12px;
            color: var(--text-muted);
        }

        /* 底部導覽列 */
        .bottom-nav {
            position: fixed;
            bottom: 0;
            left: 50%;
            transform: translateX(-50%);
            width: 100%;
            max-width: 414px;
            background-color: var(--bg-main);
            border-top: 1px solid var(--border-color);
            display: flex;
            justify-content: space-around;
            padding: 14px 0 20px 0;
            z-index: 20;
        }

        .nav-link {
            color: #9CA19B;
            text-decoration: none;
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        .nav-link.active {
            color: var(--accent-green);
        }

        /* Toast 提示訊息 */
        .toast {
            position: fixed;
            bottom: 80px;
            left: 50%;
            transform: translateX(-50%);
            background-color: var(--accent-green);
            color: white;
            padding: 10px 18px;
            border-radius: 999px;
            font-size: 13px;
            font-weight: 500;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.25s;
            z-index: 50;
            white-space: nowrap;
        }

        .toast.show {
            opacity: 1;
        }
    </style>
</head>
<body>
    <div class="app-shell">
        <!-- 頂部列 -->
        <header class="top-bar">
            <a href="/" class="brand-logo">form & field</a>
            <button class="bag-btn" onclick="checkoutCart()" title="點擊結帳建立訂單">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"></path>
                    <line x1="3" y1="6" x2="21" y2="6"></line>
                    <path d="M16 10a4 4 0 0 1-8 0"></path>
                </svg>
                <span class="bag-badge" id="cart-badge">{{ cart_count }}</span>
            </button>
        </header>

        <!-- 標題區 -->
        <h1 class="hero-title">Good things, daily.</h1>
        <p class="hero-subtitle">Thoughtful objects for a slower kind of living.</p>

        <!-- 搜尋框 -->
        <form class="search-bar" method="GET" action="/">
            {% if current_category %}
            <input type="hidden" name="category" value="{{ current_category }}">
            {% endif %}
            <svg class="search-icon" width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="11" cy="11" r="8"></circle>
                <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
            </svg>
            <input type="text" name="search" placeholder="Search your everyday essentials" value="{{ search }}">
            <svg class="filter-icon" width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="4" y1="21" x2="4" y2="14"></line>
                <line x1="4" y1="10" x2="4" y2="3"></line>
                <line x1="12" y1="21" x2="12" y2="12"></line>
                <line x1="12" y1="8" x2="12" y2="3"></line>
                <line x1="20" y1="21" x2="20" y2="16"></line>
                <line x1="20" y1="12" x2="20" y2="3"></line>
                <line x1="1" y1="14" x2="7" y2="14"></line>
                <line x1="9" y1="8" x2="15" y2="8"></line>
                <line x1="17" y1="16" x2="23" y2="16"></line>
            </svg>
        </form>

        <!-- 分類標籤 -->
        <div class="category-pills">
            <a href="/?search={{ search }}" class="pill {% if not current_category and not fav_only %}active{% endif %}">All goods</a>
            {% for cat in categories %}
            <a href="/?category={{ cat }}&search={{ search }}" class="pill {% if current_category == cat %}active{% endif %}">{{ cat }}</a>
            {% endfor %}
        </div>

        <!-- 商品數量與排序 -->
        <div class="meta-row">
            <span>{{ total_display }} considered essentials</span>
            <div class="sort-dropdown">
                Featured
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="6 9 12 15 18 9"></polyline>
                </svg>
            </div>
        </div>

        <!-- 商品列表 -->
        <div class="product-grid">
            {% for p in products %}
            <div class="product-card">
                <div class="img-wrapper" onclick="addToBag({{ p.id }}, '{{ p.name }}')">
                    {% if p.img.startswith('http') %}
                    <img src="{{ p.img }}" alt="{{ p.name }}">
                    {% else %}
                    <div class="emoji-fallback">{{ p.img }}</div>
                    {% endif %}

                    {% if loop.index == 1 %}
                    <span class="tag-badge">BESTSELLER</span>
                    {% elif loop.index == 4 %}
                    <span class="tag-badge">NEW</span>
                    {% endif %}

                    <button type="button" class="heart-btn {% if p.id in fav_ids %}favorited{% endif %}" onclick="event.stopPropagation(); toggleFav({{ p.id }}, this)">
                        <svg viewBox="0 0 24 24">
                            <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
                        </svg>
                    </button>
                </div>
                <div class="card-header">
                    <h2 class="prod-title">{{ p.name }}</h2>
                    <span class="prod-price">${{ p.price }}</span>
                </div>
                <p class="prod-desc">{{ p.desc }}</p>
            </div>
            {% endfor %}
        </div>

        <!-- 底部標語 -->
        <div class="footer-note">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#244734" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z"></path>
                <path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"></path>
            </svg>
            <span>Made with care. Chosen to last.</span>
        </div>

        <!-- 底部導覽列 -->
        <nav class="bottom-nav">
            <a href="/" class="nav-link {% if not fav_only %}active{% endif %}">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect x="3" y="3" width="7" height="7" rx="1"></rect>
                    <rect x="14" y="3" width="7" height="7" rx="1"></rect>
                    <rect x="14" y="14" width="7" height="7" rx="1"></rect>
                    <rect x="3" y="14" width="7" height="7" rx="1"></rect>
                </svg>
            </a>
            <a href="/?search=" class="nav-link">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10"></circle>
                    <polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"></polygon>
                </svg>
            </a>
            <a href="/?favorites=1" class="nav-link {% if fav_only %}active{% endif %}">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
                </svg>
            </a>
            <a href="javascript:void(0)" onclick="showToast('Demo User logged in')" class="nav-link">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                    <circle cx="12" cy="7" r="4"></circle>
                </svg>
            </a>
        </nav>
    </div>

    <div id="toast" class="toast"></div>

    <script>
        function showToast(msg) {
            const toast = document.getElementById('toast');
            toast.textContent = msg;
            toast.classList.add('show');
            setTimeout(() => toast.classList.remove('show'), 2000);
        }

        async function toggleFav(productId, btn) {
            const res = await fetch('/api/favorite', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ product_id: productId })
            });
            const data = await res.json();
            if (data.favorited) {
                btn.classList.add('favorited');
                showToast('Added to favorites');
            } else {
                btn.classList.remove('favorited');
                showToast('Removed from favorites');
            }
        }

        async function addToBag(productId, productName) {
            const res = await fetch('/api/cart/add', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ product_id: productId })
            });
            const data = await res.json();
            document.getElementById('cart-badge').textContent = data.cart_count;
            showToast(`Added ${productName} to bag`);
        }

        async function checkoutCart() {
            const res = await fetch('/api/checkout', { method: 'POST' });
            const data = await res.json();
            if (data.error) {
                showToast(data.error);
            } else {
                document.getElementById('cart-badge').textContent = 0;
                showToast(`Order #${data.order_id} placed! Total: $${data.total}`);
            }
        }
    </script>
</body>
</html>
"""


# ==================== Flask 路由與 API ====================

@app.route("/")
def index():
    search = request.args.get("search", "").strip()
    category = request.args.get("category", "").strip()
    fav_only = request.args.get("favorites") == "1"
    user_id = 1

    if "cart" not in session:
        session["cart"] = {"1": 1, "4": 1}

    if fav_only:
        products = get_favorite_products(user_id)
    else:
        products = get_all_products(search=search, category=category)

    db_categories = get_product_categories()
    preferred_order = ["Ceramics", "Textiles", "Living"]
    categories = [c for c in preferred_order if c in db_categories] + [
        c for c in db_categories if c not in preferred_order
    ]

    fav_ids = get_favorite_product_ids(user_id)
    cart_count = sum(session["cart"].values())

    total_display = 24 if (not search and not category and not fav_only and len(products) == 4) else len(products)

    return render_template_string(
        HTML_TEMPLATE,
        products=products,
        categories=categories,
        current_category=category,
        search=search,
        fav_ids=fav_ids,
        cart_count=cart_count,
        fav_only=fav_only,
        total_display=total_display,
    )


@app.route("/api/favorite", methods=["POST"])
def api_toggle_favorite():
    data = request.get_json()
    product_id = int(data["product_id"])
    favorited = toggle_favorite(user_id=1, product_id=product_id)
    return jsonify({"favorited": favorited})


@app.route("/api/cart/add", methods=["POST"])
def api_add_to_cart():
    data = request.get_json()
    product_id = str(data["product_id"])
    cart = session.get("cart", {})
    cart[product_id] = cart.get(product_id, 0) + 1
    session["cart"] = cart
    return jsonify({"cart_count": sum(cart.values())})


@app.route("/api/checkout", methods=["POST"])
def api_checkout():
    cart = session.get("cart", {})
    try:
        order_id, total = create_order(cart, user_id=1)
        session["cart"] = {}
        return jsonify({"order_id": order_id, "total": total})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    init_db()
    print("啟動成功！請在瀏覽器開啟： http://127.0.0.1:5000")
    app.run(debug=True, port=5000)