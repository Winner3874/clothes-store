
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
    # Older databases declared rating NOT NULL. Rebuild only that table so a
    # blank rating can be stored as SQL NULL while preserving product IDs and
    # the foreign-key references from related tables.
    migration_conn = sqlite3.connect(DB_PATH)
    try:
        migration_conn.execute("PRAGMA foreign_keys = OFF")
        existing = migration_conn.execute(
            "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'products'"
        ).fetchone()
        if existing and "RATING REAL NOT NULL" in (existing[0] or "").upper():
            migration_conn.execute("BEGIN")
            migration_conn.execute("""
                CREATE TABLE products_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    price INTEGER NOT NULL CHECK (price >= 0),
                    description TEXT NOT NULL DEFAULT '',
                    image TEXT NOT NULL DEFAULT '',
                    image_url TEXT NOT NULL DEFAULT '',
                    categories TEXT NOT NULL DEFAULT '',
                    photos TEXT NOT NULL DEFAULT '',
                    category TEXT NOT NULL DEFAULT '其他',
                    stock INTEGER NOT NULL DEFAULT 20 CHECK (stock >= 0),
                    rating REAL DEFAULT 5 CHECK (rating IS NULL OR (rating >= 0 AND rating <= 5)),
                    colors TEXT NOT NULL DEFAULT 'Black,White',
                    sizes TEXT NOT NULL DEFAULT 'S,M,L'
                )
            """)
            migration_conn.execute("""
                INSERT INTO products_new
                    (id, name, price, description, image, image_url, categories, photos,
                     category, stock, rating, colors, sizes)
                SELECT id, name, price, description, image, image_url, categories, photos,
                       category, stock, rating, colors, sizes
                FROM products
            """)
            migration_conn.execute("DROP TABLE products")
            migration_conn.execute("ALTER TABLE products_new RENAME TO products")
            migration_conn.commit()
    except Exception:
        migration_conn.rollback()
        raise
    finally:
        migration_conn.close()

    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price INTEGER NOT NULL CHECK (price >= 0),
                description TEXT NOT NULL DEFAULT '',
                image TEXT NOT NULL DEFAULT '',
                image_url TEXT NOT NULL DEFAULT '',
                categories TEXT NOT NULL DEFAULT '',
                photos TEXT NOT NULL DEFAULT '',
                category TEXT NOT NULL DEFAULT '其他',
                stock INTEGER NOT NULL DEFAULT 20 CHECK (stock >= 0),
                rating REAL DEFAULT 5 CHECK (rating IS NULL OR (rating >= 0 AND rating <= 5)),
                colors TEXT NOT NULL DEFAULT 'Black,White',
                sizes TEXT NOT NULL DEFAULT 'S,M,L'
            )
        """)

        product_columns = {
            row["name"] for row in conn.execute("PRAGMA table_info(products)")
        }
        if "category" not in product_columns:
            conn.execute(
                "ALTER TABLE products ADD COLUMN category TEXT NOT NULL DEFAULT '其他'"
            )
        if "stock" not in product_columns:
            conn.execute(
                "ALTER TABLE products ADD COLUMN stock INTEGER NOT NULL DEFAULT 20 CHECK (stock >= 0)"
            )

        product_columns = {row["name"] for row in conn.execute("PRAGMA table_info(products)")}
        for column, definition in {
            "image_url": "TEXT NOT NULL DEFAULT ''",
            "categories": "TEXT NOT NULL DEFAULT ''",
            "photos": "TEXT NOT NULL DEFAULT ''",
            "rating": "REAL DEFAULT 5 CHECK (rating IS NULL OR (rating >= 0 AND rating <= 5))",
            "colors": "TEXT NOT NULL DEFAULT 'Black,White'",
            "sizes": "TEXT NOT NULL DEFAULT 'S,M,L'",
        }.items():
            if column not in product_columns:
                conn.execute(f"ALTER TABLE products ADD COLUMN {column} {definition}")

        conn.execute("""
            CREATE TABLE IF NOT EXISTS product_categories (
                product_id INTEGER NOT NULL,
                category TEXT NOT NULL,
                PRIMARY KEY (product_id, category),
                FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
            )
        """)
        conn.execute("CREATE TABLE IF NOT EXISTS schema_migrations (version TEXT PRIMARY KEY)")
        product_columns = {row["name"] for row in conn.execute("PRAGMA table_info(products)")}
        if "details" in product_columns:
            conn.execute("""
                UPDATE products
                SET description = CASE
                    WHEN description = '' THEN details
                    ELSE description || char(10) || details
                END
                WHERE details <> '' AND instr(description, details) = 0
            """)
            conn.execute("ALTER TABLE products DROP COLUMN details")

        conn.execute("""
            CREATE TABLE IF NOT EXISTS product_images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                image_url TEXT NOT NULL,
                sort_order INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                username TEXT NOT NULL UNIQUE COLLATE NOCASE,
                email TEXT UNIQUE COLLATE NOCASE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Migrate the original email-login schema while preserving user IDs
        # referenced by favorites and orders.
        user_columns = {row["name"] for row in conn.execute("PRAGMA table_info(users)")}
        if "username" not in user_columns:
            conn.execute("PRAGMA foreign_keys = OFF")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    username TEXT NOT NULL UNIQUE COLLATE NOCASE,
                    email TEXT UNIQUE COLLATE NOCASE,
                    password_hash TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)
            for old in conn.execute("SELECT * FROM users").fetchall():
                email = old["email"]
                base = (email.split("@", 1)[0] if email else "member").strip() or "member"
                username, suffix = base, 1
                while conn.execute("SELECT 1 FROM users_new WHERE username = ? COLLATE NOCASE", (username,)).fetchone():
                    suffix += 1
                    username = f"{base}{suffix}"
                conn.execute(
                    "INSERT INTO users_new (id, name, username, email, password_hash, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (old["id"], old["name"], username, email, old["password_hash"], old["created_at"]),
                )
            conn.execute("DROP TABLE users")
            conn.execute("ALTER TABLE users_new RENAME TO users")
            conn.execute("PRAGMA foreign_keys = ON")

        user_columns = {row["name"] for row in conn.execute("PRAGMA table_info(users)")}
        if "google_sub" not in user_columns:
            conn.execute("ALTER TABLE users ADD COLUMN google_sub TEXT")
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS users_google_sub_unique ON users(google_sub) WHERE google_sub IS NOT NULL")

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
                selected_options TEXT NOT NULL DEFAULT '',

                FOREIGN KEY (order_id)
                    REFERENCES orders(id)
                    ON DELETE CASCADE,

                FOREIGN KEY (product_id)
                    REFERENCES products(id)
                    ON DELETE SET NULL
            )
        """)

        order_item_columns = {row["name"] for row in conn.execute("PRAGMA table_info(order_items)")}
        if "selected_options" not in order_item_columns:
            conn.execute("ALTER TABLE order_items ADD COLUMN selected_options TEXT NOT NULL DEFAULT ''")

        count = conn.execute(
            "SELECT COUNT(*) FROM products"
        ).fetchone()[0]

        if count == 0:
            conn.executemany("""
                INSERT INTO products
                    (name, price, description, image, category, stock)
                VALUES (?, ?, ?, ?, ?, ?)
            """, [(*product, 20) for product in INITIAL_PRODUCTS])

        migrated = conn.execute(
            "SELECT 1 FROM schema_migrations WHERE version = 'product-categories-v1'"
        ).fetchone()
        if not migrated:
            for product in conn.execute("SELECT id, category FROM products").fetchall():
                values = [value.strip() for value in (product["category"] or "").split(",") if value.strip()]
                conn.executemany(
                    "INSERT OR IGNORE INTO product_categories (product_id, category) VALUES (?, ?)",
                    [(product["id"], value) for value in values],
                )
            conn.execute(
                "INSERT INTO schema_migrations (version) VALUES ('product-categories-v1')"
            )

        migrated_images = conn.execute(
            "SELECT 1 FROM schema_migrations WHERE version = 'product-images-v1'"
        ).fetchone()
        if not migrated_images:
            for product in conn.execute("SELECT id, image_url FROM products WHERE image_url <> ''").fetchall():
                conn.execute(
                    "INSERT INTO product_images (product_id, image_url, sort_order) VALUES (?, ?, 0)",
                    (product["id"], product["image_url"]),
                )
            conn.execute(
                "INSERT INTO schema_migrations (version) VALUES ('product-images-v1')"
            )

        migrated_csv = conn.execute(
            "SELECT 1 FROM schema_migrations WHERE version = 'product-csv-fields-v1'"
        ).fetchone()
        if not migrated_csv:
            for product in conn.execute("SELECT id, category, image_url FROM products").fetchall():
                category_rows = conn.execute(
                    "SELECT category FROM product_categories WHERE product_id = ? ORDER BY category",
                    (product["id"],),
                ).fetchall()
                categories = [row["category"] for row in category_rows]
                if not categories:
                    categories = [part.strip() for part in (product["category"] or "").split(",") if part.strip()]
                image_rows = conn.execute(
                    "SELECT image_url FROM product_images WHERE product_id = ? ORDER BY sort_order, id",
                    (product["id"],),
                ).fetchall()
                photos = []
                for row in image_rows:
                    value = row["image_url"]
                    photos.append(Path(value).name if value.startswith("/static/uploads/products/") else value)
                if not photos and product["image_url"]:
                    value = product["image_url"]
                    photos = [Path(value).name if value.startswith("/static/uploads/products/") else value]
                conn.execute(
                    "UPDATE products SET categories = ?, photos = ? WHERE id = ?",
                    (",".join(categories), ",".join(photos), product["id"]),
                )
            conn.execute(
                "INSERT INTO schema_migrations (version) VALUES ('product-csv-fields-v1')"
            )


def _split_csv(value):
    return list(dict.fromkeys(part.strip() for part in (value or "").split(",") if part.strip()))


def _resolve_product_image(value):
    value = (value or "").strip()
    if not value:
        return ""
    if value.startswith(("http://", "https://", "/")):
        if value.startswith("/static/uploads/products/"):
            filename = Path(value).name
        else:
            return value
    else:
        filename = Path(value).name
    image_dir = Path(__file__).resolve().parent / "static" / "uploads" / "products"
    suffix = Path(filename).suffix.lower()
    candidates = [filename] if suffix else [filename + ext for ext in (".jpg", ".jpeg", ".png", ".webp")]
    existing_files = {path.name.casefold(): path.name for path in image_dir.iterdir()} if image_dir.is_dir() else {}
    for candidate in candidates:
        actual_name = existing_files.get(candidate.casefold())
        if actual_name:
            return "/static/uploads/products/" + actual_name
    return ""


def _attach_product_images(conn, product):
    stored_names = _split_csv(product.get("photos", ""))
    table_rows = conn.execute(
        "SELECT id, image_url FROM product_images WHERE product_id = ? ORDER BY sort_order, id",
        (product["id"],),
    ).fetchall()
    if not stored_names:
        stored_names = [row["image_url"] for row in table_rows]
    if not stored_names and product.get("image_url"):
        stored_names = [product["image_url"]]

    images = []
    for name in stored_names:
        image_url = _resolve_product_image(name)
        if image_url and image_url not in images:
            images.append(image_url)
    record_by_url = {}
    for row in table_rows:
        resolved = _resolve_product_image(row["image_url"])
        if resolved:
            record_by_url[resolved] = row["id"]
    product["images"] = images
    product["image_url"] = images[0] if images else ""
    product["image_records"] = [
        {"id": record_by_url.get(url), "image_url": url} for url in images
    ]
    categories = _split_csv(product.get("categories", ""))
    product["category_list"] = categories
    product["category"] = ", ".join(categories)
    return product


def get_all_products(search="", category=""):
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT id, name, price, description AS desc, image AS img, image_url,
                   categories, photos, category AS legacy_category, stock, rating, colors, sizes
            FROM products
            WHERE (? = '' OR name LIKE ? OR description LIKE ?)
            ORDER BY id
        """, (search, f"%{search}%", f"%{search}%")).fetchall()
        products = [_attach_product_images(conn, dict(row)) for row in rows]
        if category:
            products = [product for product in products if category in product["category_list"]]
        return products


def get_product_by_id(product_id):
    with get_connection() as conn:
        row = conn.execute("""
            SELECT id, name, price, description AS desc, image AS img, image_url,
                   categories, photos, category AS legacy_category, stock, rating, colors, sizes
            FROM products WHERE id = ?
        """, (product_id,)).fetchone()
        return _attach_product_images(conn, dict(row)) if row else None


def get_product_categories():
    with get_connection() as conn:
        rows = conn.execute("SELECT categories FROM products").fetchall()
        categories = {category for row in rows for category in _split_csv(row["categories"])}
        return sorted(categories)


def create_user(name, username, email, password_hash):
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO users (name, username, email, password_hash) VALUES (?, ?, ?, ?)",
            (name.strip(), username.strip(), email.strip().lower() or None, password_hash),
        )
        return cursor.lastrowid


def get_user_by_username(username):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id, name, username, email, password_hash FROM users WHERE username = ? COLLATE NOCASE",
            (username.strip(),),
        ).fetchone()
        return dict(row) if row else None


def get_user_by_google_sub(google_sub):
    with get_connection() as conn:
        row = conn.execute("SELECT id, name, username, email FROM users WHERE google_sub = ?", (google_sub,)).fetchone()
        return dict(row) if row else None


def create_or_link_google_user(name, email, google_sub, password_hash):
    """Find an existing Google member, link a verified email, or create a member."""
    email = email.strip().lower()
    with get_connection() as conn:
        row = conn.execute("SELECT id, name, username, email FROM users WHERE google_sub = ?", (google_sub,)).fetchone()
        if row:
            return dict(row)
        row = conn.execute("SELECT id, name, username, email FROM users WHERE email = ? COLLATE NOCASE", (email,)).fetchone()
        if row:
            conn.execute("UPDATE users SET google_sub = ? WHERE id = ?", (google_sub, row["id"]))
            return dict(row)
        base = "".join(ch for ch in email.split("@", 1)[0] if ch.isalnum() or ch in "_-")[:32] or "member"
        username, suffix = base, 1
        while conn.execute("SELECT 1 FROM users WHERE username = ? COLLATE NOCASE", (username,)).fetchone():
            suffix += 1
            username = f"{base[:35]}{suffix}"
        cursor = conn.execute(
            "INSERT INTO users (name, username, email, password_hash, google_sub) VALUES (?, ?, ?, ?, ?)",
            (name.strip()[:80] or username, username, email, password_hash, google_sub),
        )
        row = conn.execute("SELECT id, name, username, email FROM users WHERE id = ?", (cursor.lastrowid,)).fetchone()
        return dict(row)


def get_user_by_id(user_id):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id, name, username, email FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        return dict(row) if row else None


def username_exists(username):
    with get_connection() as conn:
        return conn.execute("SELECT 1 FROM users WHERE username = ? COLLATE NOCASE", (username.strip(),)).fetchone() is not None


def update_user_password(user_id, password_hash):
    with get_connection() as conn:
        conn.execute("UPDATE users SET password_hash = ? WHERE id = ?", (password_hash, user_id))


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
        rows = conn.execute(
            "SELECT product_id FROM favorites WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,),
        ).fetchall()
    return [product for row in rows if (product := get_product_by_id(row["product_id"]))]


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
                SELECT product_name, quantity, unit_price, selected_options
                FROM order_items WHERE order_id = ? ORDER BY id
            """, (order["id"],)).fetchall()
            order["items"] = [dict(item) for item in items]
            orders.append(order)
        return orders


def add_product(name, price, description="", image="", *, image_url="", photos="", category="", categories=None, stock=20, rating=5, colors="Black,White", sizes="S,M,L"):
    """新增商品，回傳新商品的 ID。"""
    if not isinstance(name, str) or not name.strip():
        raise ValueError("name is required")
    if not isinstance(price, int) or price < 0:
        raise ValueError("price must be a non-negative integer")
    if not isinstance(stock, int) or stock < 0:
        raise ValueError("stock must be a non-negative integer")
    if rating is not None and (not isinstance(rating, (int, float)) or not 0 <= rating <= 5):
        raise ValueError("rating must be between 0 and 5")
    category_source = categories if categories is not None else category
    if isinstance(category_source, str):
        category_values = [value.strip() for value in category_source.split(",") if value.strip()]
    elif isinstance(category_source, (list, tuple, set)):
        category_values = list(dict.fromkeys(value.strip() for value in category_source if isinstance(value, str) and value.strip()))
    else:
        raise ValueError("categories must be a string or a list of strings")
    if not all(isinstance(value, str) for value in (description, image, image_url, photos, colors, sizes)):
        raise ValueError("product text fields must be strings")

    category_text = ",".join(category_values)
    photo_values = _split_csv(photos)
    if image_url and not photo_values:
        photo_values = [image_url]
    photos_text = ",".join(photo_values)
    with get_connection() as conn:
        cursor = conn.execute("""
            INSERT INTO products
                (name, price, description, image, image_url, categories, photos, category, stock, rating, colors, sizes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name.strip(), price, description, image, image_url, category_text, photos_text, category_text, stock, rating, colors, sizes))
        product_id = cursor.lastrowid
        conn.executemany(
            "INSERT INTO product_categories (product_id, category) VALUES (?, ?)",
            [(product_id, value) for value in category_values],
        )
        for order, photo in enumerate(photo_values):
            normalized = photo if photo.startswith(("http://", "https://", "/")) else "/static/uploads/products/" + Path(photo).name
            conn.execute(
                "INSERT INTO product_images (product_id, image_url, sort_order) VALUES (?, ?, ?)",
                (product_id, normalized, order),
            )
        return product_id


def update_product(product_id, **fields):
    allowed = {"name", "price", "description", "categories", "photos", "stock", "rating", "colors", "sizes"}
    unknown = set(fields) - allowed
    if unknown:
        raise ValueError(f"unsupported product fields: {', '.join(sorted(unknown))}")
    if "name" in fields and (not isinstance(fields["name"], str) or not fields["name"].strip()):
        raise ValueError("name is required")
    for key in ("price", "stock"):
        if key in fields and (not isinstance(fields[key], int) or fields[key] < 0):
            raise ValueError(f"{key} must be a non-negative integer")
    if "rating" in fields and fields["rating"] is not None and not 0 <= fields["rating"] <= 5:
        raise ValueError("rating must be blank or between 0 and 5")
    with get_connection() as conn:
        current = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
        if current is None:
            return False
        values = dict(current)
        values.update(fields)
        categories = values.get("categories", "")
        category_values = _split_csv(categories) if isinstance(categories, str) else list(categories)
        category_text = ",".join(category_values)
        photos = values.get("photos", "")
        photo_values = _split_csv(photos) if isinstance(photos, str) else list(photos)
        values.update(categories=category_text, category=category_text, photos=",".join(photo_values))
        columns = ("name", "price", "description", "categories", "photos", "category", "stock", "rating", "colors", "sizes")
        conn.execute(
            "UPDATE products SET " + ", ".join(f"{column} = ?" for column in columns) + " WHERE id = ?",
            tuple(values[column] for column in columns) + (product_id,),
        )
        conn.execute("DELETE FROM product_categories WHERE product_id = ?", (product_id,))
        conn.executemany("INSERT INTO product_categories (product_id, category) VALUES (?, ?)", [(product_id, item) for item in category_values])
        conn.execute("DELETE FROM product_images WHERE product_id = ?", (product_id,))
        for order, photo in enumerate(photo_values):
            normalized = photo if photo.startswith(("http://", "https://", "/")) else "/static/uploads/products/" + Path(photo).name
            conn.execute("INSERT INTO product_images (product_id, image_url, sort_order) VALUES (?, ?, ?)", (product_id, normalized, order))
        first_photo = photo_values[0] if photo_values else ""
        image_url = first_photo if first_photo.startswith(("http://", "https://", "/")) else "/static/uploads/products/" + Path(first_photo).name if first_photo else ""
        conn.execute("UPDATE products SET image_url = ? WHERE id = ?", (image_url, product_id))
        return True


def delete_product(product_id):
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
        return cursor.rowcount == 1


def add_product_image(product_id, image_url):
    with get_connection() as conn:
        if conn.execute("SELECT 1 FROM products WHERE id = ?", (product_id,)).fetchone() is None:
            return None
        product = conn.execute(
            "SELECT image_url FROM products WHERE id = ?", (product_id,)
        ).fetchone()
        order = conn.execute(
            "SELECT COALESCE(MAX(sort_order), -1) + 1 FROM product_images WHERE product_id = ?",
            (product_id,),
        ).fetchone()[0]
        if order == 0 and product["image_url"] and product["image_url"] != image_url:
            conn.execute(
                "INSERT INTO product_images (product_id, image_url, sort_order) VALUES (?, ?, 0)",
                (product_id, product["image_url"]),
            )
            order = 1
        cursor = conn.execute(
            "INSERT INTO product_images (product_id, image_url, sort_order) VALUES (?, ?, ?)",
            (product_id, image_url, order),
        )
        filename = Path(image_url).name if image_url.startswith("/static/uploads/products/") else image_url
        existing = conn.execute("SELECT photos FROM products WHERE id = ?", (product_id,)).fetchone()["photos"]
        photo_values = _split_csv(existing)
        if filename not in photo_values:
            photo_values.append(filename)
        first_photo = photo_values[0] if photo_values else ""
        first_url = first_photo if first_photo.startswith(("http://", "https://", "/")) else _resolve_product_image(first_photo)
        conn.execute(
            "UPDATE products SET photos = ?, image_url = ? WHERE id = ?",
            (",".join(photo_values), first_url, product_id),
        )
        return cursor.lastrowid


def delete_product_image(image_id, product_id):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT image_url FROM product_images WHERE id = ? AND product_id = ?",
            (image_id, product_id),
        ).fetchone()
        if row is None:
            return None
        conn.execute("DELETE FROM product_images WHERE id = ?", (image_id,))
        first = conn.execute(
            "SELECT image_url FROM product_images WHERE product_id = ? ORDER BY sort_order, id LIMIT 1",
            (product_id,),
        ).fetchone()
        product = conn.execute("SELECT photos FROM products WHERE id = ?", (product_id,)).fetchone()
        removed_name = Path(row["image_url"]).name if row["image_url"].startswith("/static/uploads/products/") else row["image_url"]
        remaining = [value for value in _split_csv(product["photos"]) if value != removed_name]
        first_url = first["image_url"] if first else (
            remaining[0] if remaining and remaining[0].startswith(("http://", "https://", "/"))
            else _resolve_product_image(remaining[0]) if remaining else ""
        )
        conn.execute(
            "UPDATE products SET photos = ?, image_url = ? WHERE id = ?",
            (",".join(remaining), first_url, product_id),
        )
        return row["image_url"]


def create_order(cart, user_id=None):
    """
    根據購物車建立訂單。
    cart 格式：{"1": 2, "3": 1}
    回傳：(order_id, total)
    """

    if not cart:
        raise ValueError("購物車是空的")

    with get_connection() as conn:
        conn.execute("BEGIN IMMEDIATE")
        items = []
        total = 0

        # 重新從資料庫讀取商品價格
        for cart_key, quantity in cart.items():
            parts = str(cart_key).split("|", 2)
            product_id = int(parts[0])
            selected_options = " / ".join(part for part in parts[1:] if part)

            if not isinstance(quantity, int) or quantity <= 0:
                raise ValueError("商品數量不正確")

            product = conn.execute("""
                SELECT id, name, price, stock
                FROM products
                WHERE id = ?
            """, (product_id,)).fetchone()

            if product is None:
                raise ValueError("商品不存在")

            if quantity > product["stock"]:
                raise ValueError(f"{product['name']} 庫存不足，目前剩餘 {product['stock']} 件")

            subtotal = product["price"] * quantity
            total += subtotal

            items.append({
                "product_id": product["id"],
                "product_name": product["name"],
                "quantity": quantity,
                "unit_price": product["price"],
                "selected_options": selected_options,
            })

        # 建立訂單主表
        cursor = conn.execute("""
            INSERT INTO orders (user_id, total, status)
            VALUES (?, ?, 'pending')
        """, (user_id, total))

        order_id = cursor.lastrowid

        for item in items:
            updated = conn.execute(
                "UPDATE products SET stock = stock - ? WHERE id = ? AND stock >= ?",
                (item["quantity"], item["product_id"], item["quantity"]),
            )
            if updated.rowcount != 1:
                raise ValueError("商品庫存已變動，請重新確認購物車數量")

        # 建立訂單明細
        conn.executemany("""
            INSERT INTO order_items (
                order_id,
                product_id,
                product_name,
                quantity,
                unit_price,
                selected_options
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, [
            (
                order_id,
                item["product_id"],
                item["product_name"],
                item["quantity"],
                item["unit_price"],
                item["selected_options"],
            )
            for item in items
        ])

        return order_id, total


def set_product_stock(product_id, stock):
    if not isinstance(stock, int) or stock < 0:
        raise ValueError("庫存數量必須是 0 或以上的整數")
    with get_connection() as conn:
        cursor = conn.execute(
            "UPDATE products SET stock = ? WHERE id = ?", (stock, product_id)
        )
        return cursor.rowcount == 1


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
                unit_price,
                selected_options
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
