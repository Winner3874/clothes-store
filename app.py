
import os
import json
import secrets
import sqlite3
import base64
import hashlib
import hmac
import uuid
from pathlib import Path
import urllib.parse
import urllib.request
import urllib.error
from functools import wraps

from flask import Flask, abort, flash, redirect, render_template, request, send_from_directory, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from database import (
    init_db,
    get_all_products,
    get_product_by_id,
    get_product_categories,
    create_order,
    get_order_details,
    create_user,
    get_user_by_username,
    create_or_link_google_user,
    get_user_by_google_sub,
    get_user_by_email,
    create_google_user,
    username_exists,
    update_user_password,
    update_user_avatar,
    get_user_by_id,
    get_favorite_product_ids,
    get_favorite_products,
    toggle_favorite,
    get_orders_by_user,
    set_line_transaction,
    get_order_for_payment,
    complete_line_payment,
    cancel_order_and_restore_stock,
    add_product,
    update_product,
    delete_product,
    get_admin_orders,
    update_admin_order_status,
    log_admin_action,
    get_admin_audit_logs,
)


def load_local_env():
    """Load simple KEY=VALUE entries from the git-ignored local .env file."""
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    try:
        with open(env_path, encoding="utf-8") as env_file:
            for line in env_file:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                value = value.strip().strip("\"'")
                os.environ.setdefault(key.strip(), value)
    except FileNotFoundError:
        pass


load_local_env()
app = Flask(__name__)

app.secret_key = os.environ.get(
    "FLASK_SECRET_KEY",
    "dev-only-change-this-secret-key"
)


def line_pay_request(path, body):
    """Send a signed LINE Pay Online API v3 request."""
    channel_id = os.environ.get("LINE_PAY_CHANNEL_ID", "").strip()
    channel_secret = os.environ.get("LINE_PAY_CHANNEL_SECRET", "").strip()
    if not channel_id or not channel_secret:
        raise RuntimeError("尚未設定 LINE_PAY_CHANNEL_ID / LINE_PAY_CHANNEL_SECRET")
    base_url = os.environ.get("LINE_PAY_API_BASE", "https://sandbox-api-pay.line.me").rstrip("/")
    nonce = str(uuid.uuid4())
    body_text = json.dumps(body, ensure_ascii=False, separators=(",", ":"))
    message = channel_secret + path + body_text + nonce
    signature = base64.b64encode(
        hmac.new(channel_secret.encode(), message.encode(), hashlib.sha256).digest()
    ).decode()
    request = urllib.request.Request(
        base_url + path,
        data=body_text.encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "X-LINE-ChannelId": channel_id,
            "X-LINE-Authorization-Nonce": nonce,
            "X-LINE-Authorization": signature,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            result = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, ValueError) as error:
        raise RuntimeError("無法連線 LINE Pay，請稍後重試") from error
    if result.get("returnCode") != "0000":
        raise RuntimeError("LINE Pay 請款失敗：" + str(result.get("returnMessage", result.get("returnCode", "未知錯誤"))))
    return result.get("info", {})


def linepay_callback_token(order_id):
    secret = app.secret_key.encode("utf-8")
    return hmac.new(secret, f"linepay:{order_id}".encode(), hashlib.sha256).hexdigest()

# 啟動時確認資料表存在
init_db()


def get_current_user():
    user_id = session.get("user_id")
    if user_id is None:
        return None
    user = get_user_by_id(user_id)
    if user is None:
        session.pop("user_id", None)
    elif not user.get("avatar_url"):
        user["avatar_url"] = "/static/uploads/avatars/default.png"
    return user


@app.context_processor
def inject_current_user():
    return {"current_user": get_current_user(), "cart_count": sum(q for q in session.get("cart", {}).values() if isinstance(q, int) and q > 0)}


def get_cart_items():
    """Resolve the session cart into the rows expected by the cart template."""
    cart = session.get("cart", {})
    if not isinstance(cart, dict):
        return [], 0

    items = []
    total = 0
    for cart_key, quantity in cart.items():
        try:
            parts = str(cart_key).split("|", 2)
            product_id = int(parts[0])
            quantity = int(quantity)
        except (TypeError, ValueError):
            continue
        if quantity < 1:
            continue

        product = get_product_by_id(product_id)
        if product is None:
            continue

        color = parts[1] if len(parts) > 1 else ""
        size = parts[2] if len(parts) > 2 else ""
        subtotal = product["price"] * quantity
        total += subtotal
        items.append({
            "id": product_id,
            "name": product["name"],
            "price": product["price"],
            "stock": product["stock"],
            "qty": quantity,
            "subtotal": subtotal,
            "cart_key": str(cart_key),
            "color": color,
            "size": size,
        })
    return items, total


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if get_current_user() is None:
            flash("請先登入會員。", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped_view


def seller_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        user = get_current_user()
        if user is None:
            return redirect(url_for("login", next=request.path))
        if user.get("role") != "admin":
            abort(403)
        return view(*args, **kwargs)
    return wrapped_view


@app.get("/")
def index():
    search = request.args.get("q", "").strip()
    selected_category = request.args.get("category", "").strip()
    products = get_all_products(search=search, category=selected_category)
    user = get_current_user()
    favorite_product_ids = set(get_favorite_product_ids(user["id"])) if user else set()
    return render_template(
        "index.html",
        products=products,
        categories=get_product_categories(),
        search=search,
        selected_category=selected_category,
        favorite_product_ids=favorite_product_ids,
    )


@app.get("/product/<int:product_id>")
def product_detail(product_id):
    product = get_product_by_id(product_id)
    if product is None:
        abort(404)
    user = get_current_user()
    is_favorite = bool(user and product_id in get_favorite_product_ids(user["id"]))
    return render_template("product_detail.html", product=product, is_favorite=is_favorite)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not name or len(name) > 80:
            flash("請輸入 1 到 80 個字的姓名。", "danger")
        elif not username or len(username) > 40 or not username.replace("_", "").replace("-", "").isalnum():
            flash("使用者名稱須為 1 到 40 個英數字、底線或連字號。", "danger")
        elif email and ("@" not in email or "." not in email or len(email) > 254):
            flash("請輸入有效的電子郵件地址。", "danger")
        elif len(password) < 8 or len(password) > 256:
            flash("密碼長度需為 8 到 256 個字元。", "danger")
        elif password != confirm_password:
            flash("兩次輸入的密碼不一致。", "danger")
        elif username_exists(username):
            flash("\u9019\u500b\u4f7f\u7528\u8005\u540d\u7a31\u5df2\u6709\u4eba\u4f7f\u7528\uff0c\u8acb\u63db\u4e00\u500b\u3002", "warning")
        else:
            try:
                user_id = create_user(name, username, email, generate_password_hash(password))
            except sqlite3.IntegrityError:
                flash("\u4f7f\u7528\u8005\u540d\u7a31\u6216\u96fb\u5b50\u90f5\u4ef6\u5df2\u88ab\u4f7f\u7528\u3002", "warning")
            else:
                session["user_id"] = user_id
                flash("註冊成功，歡迎加入！", "success")
                return redirect(url_for("index"))
    return render_template("auth.html", mode="register")


@app.route("/login", methods=["GET", "POST"])
def login():
    next_url = request.form.get("next", "") if request.method == "POST" else request.args.get("next", "")
    parsed_next = urllib.parse.urlsplit(next_url)
    if not next_url.startswith("/") or next_url.startswith("//") or parsed_next.netloc or parsed_next.scheme:
        next_url = ""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = get_user_by_username(username)
        if user is None or not check_password_hash(user["password_hash"], password):
            flash("\u4f7f\u7528\u8005\u540d\u7a31\u6216\u5bc6\u78bc\u4e0d\u6b63\u78ba\u3002", "danger")
        else:
            session["user_id"] = user["id"]
            flash(f"歡迎回來，{user['username']}！", "success")
            return redirect(next_url or (url_for("seller_dashboard") if user.get("role") == "admin" else url_for("index")))
    return render_template(
        "auth.html",
        mode="login",
        login_required=request.args.get("required") == "1",
        next_url=next_url,
    )


@app.get("/auth/google")
def google_login():
    client_id = os.environ.get("GOOGLE_CLIENT_ID")
    if not client_id or not os.environ.get("GOOGLE_CLIENT_SECRET"):
        flash("Google 登入尚未設定，請管理者設定 GOOGLE_CLIENT_ID 與 GOOGLE_CLIENT_SECRET。", "warning")
        return redirect(url_for("login"))
    state = secrets.token_urlsafe(32)
    session["google_oauth_state"] = state
    query = urllib.parse.urlencode({
        "client_id": client_id,
        "redirect_uri": url_for("google_callback", _external=True),
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "prompt": "select_account",
    })
    return redirect("https://accounts.google.com/o/oauth2/v2/auth?" + query)


@app.get("/auth/google/callback")
def google_callback():
    expected_state = session.pop("google_oauth_state", None)
    if not expected_state or not secrets.compare_digest(expected_state, request.args.get("state", "")):
        flash("Google 登入驗證失敗，請重試。", "danger")
        return redirect(url_for("login"))
    code = request.args.get("code")
    if not code:
        flash("Google 登入未完成，請重試。", "warning")
        return redirect(url_for("login"))
    try:
        token_request = urllib.request.Request(
            "https://oauth2.googleapis.com/token",
            data=urllib.parse.urlencode({
                "code": code,
                "client_id": os.environ["GOOGLE_CLIENT_ID"],
                "client_secret": os.environ["GOOGLE_CLIENT_SECRET"],
                "redirect_uri": url_for("google_callback", _external=True),
                "grant_type": "authorization_code",
            }).encode(),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        with urllib.request.urlopen(token_request, timeout=10) as response:
            token_data = json.loads(response.read())
        id_token = token_data.get("id_token")
        if not id_token:
            raise ValueError("Missing Google ID token")
        with urllib.request.urlopen("https://oauth2.googleapis.com/tokeninfo?id_token=" + urllib.parse.quote(id_token), timeout=10) as response:
            identity = json.loads(response.read())
        if (identity.get("aud") != os.environ["GOOGLE_CLIENT_ID"]
                or identity.get("iss") not in ("accounts.google.com", "https://accounts.google.com")
                or identity.get("email_verified") != "true"
                or not identity.get("sub") or not identity.get("email")):
            raise ValueError("Invalid Google identity")
        user = get_user_by_google_sub(identity["sub"])
        if not user:
            user = get_user_by_email(identity["email"])
            if user:
                user = create_or_link_google_user(
                    identity.get("name", ""), identity["email"], identity["sub"],
                    generate_password_hash(secrets.token_urlsafe(48)),
                )
            else:
                session["pending_google_user"] = {
                    "sub": identity["sub"], "email": identity["email"],
                    "name": identity.get("name", "")
                }
                return redirect(url_for("google_register"))
    except (KeyError, ValueError, urllib.error.URLError, TimeoutError, json.JSONDecodeError) as error:
        app.logger.warning("Google OAuth failed: %s", error)
        flash("Google 登入目前無法完成，請稍後再試。", "danger")
        return redirect(url_for("login"))
    session["user_id"] = user["id"]
    flash(f"登入成功，歡迎 {user['name']}！", "success")
    return redirect(url_for("seller_dashboard") if user.get("role") == "admin" else url_for("index"))


@app.route("/auth/google/register", methods=["GET", "POST"])
def google_register():
    pending = session.get("pending_google_user")
    if not pending:
        flash("請先使用 Google 帳號驗證。", "warning")
        return redirect(url_for("login"))
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        username = request.form.get("username", "").strip()
        if not name or len(name) > 80:
            flash("姓名請輸入 1 到 80 個字元。", "danger")
        elif not username or len(username) > 40 or not username.replace("_", "").replace("-", "").isalnum():
            flash("使用者名稱須為 1 到 40 個英數字、底線或連字號。", "danger")
        elif username_exists(username):
            flash("這個使用者名稱已有人使用，請換一個。", "warning")
        else:
            try:
                user_id = create_google_user(name, username, pending["email"], pending["sub"],
                                            generate_password_hash(secrets.token_urlsafe(48)))
            except sqlite3.IntegrityError:
                flash("這個使用者名稱已有人使用，請換一個。", "warning")
            else:
                session.pop("pending_google_user", None)
                session["user_id"] = user_id
                flash(f"??????? {name}?", "success")
                return redirect(url_for("index"))
    base = "".join(ch for ch in pending["email"].split("@", 1)[0] if ch.isalnum() or ch in "_-")[:40]
    suggested_username = base or ""
    suffix = 1
    while suggested_username and username_exists(suggested_username):
        suffix += 1
        suggested_username = f"{base[:max(1, 40 - len(str(suffix)))]}{suffix}"
    return render_template("google_register.html", email=pending["email"],
                           google_name=pending.get("name", ""),
                           suggested_username=suggested_username)


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user = get_current_user()
    if request.method == "POST":
        photo = request.files.get("avatar")
        extension = Path(photo.filename or "").suffix.lower()
        if not photo or not photo.filename:
            flash("請選擇要上傳的頭貼。", "warning")
        elif extension not in {".jpg", ".jpeg", ".png", ".webp", ".gif"}:
            flash("頭貼格式請使用 JPG、PNG、WebP 或 GIF。", "danger")
        else:
            data = photo.stream.read(5 * 1024 * 1024 + 1)
            if len(data) > 5 * 1024 * 1024:
                flash("頭貼檔案不可超過 5 MB。", "danger")
            else:
                filename = f"{user['id']}-{uuid.uuid4().hex}{extension}"
                avatar_dir = Path(app.root_path) / "static" / "uploads" / "avatars"
                avatar_dir.mkdir(parents=True, exist_ok=True)
                (avatar_dir / filename).write_bytes(data)
                update_user_avatar(user["id"], f"/static/uploads/avatars/{filename}")
                flash("頭貼已更新。", "success")
                return redirect(url_for("profile"))
    return render_template("profile.html", user=user)


@app.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    user = get_current_user()
    if request.method == "POST":
        current_password = request.form.get("current_password", "")
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        if not check_password_hash(user["password_hash"], current_password):
            flash("原密碼不正確。", "danger")
        elif len(password) < 8 or len(password) > 256:
            flash("新密碼長度需為 8 到 256 個字元。", "danger")
        elif password != confirm_password:
            flash("兩次輸入的新密碼不一致。", "danger")
        else:
            update_user_password(user["id"], generate_password_hash(password))
            flash("密碼已更新。", "success")
            return redirect(url_for("change_password"))
    return render_template("change_password.html")


@app.get("/cart")
def cart():
    cart_items, total = get_cart_items()
    return render_template("cart.html", cart_items=cart_items, total=total)


@app.post("/logout")
def logout():
    session.pop("user_id", None)
    flash("你已登出。", "success")
    return redirect(url_for("index"))


@app.get("/favorites")
@login_required
def favorites():
    user = get_current_user()
    products = get_favorite_products(user["id"])
    return render_template("favorites.html", products=products)


@app.post("/favorites/toggle/<int:product_id>")
def favorite_toggle(product_id):
    if get_product_by_id(product_id) is None:
        abort(404)
    user = get_current_user()
    if user is None:
        flash("請先登入會員，再收藏商品。", "warning")
        return redirect(url_for("login"))

    added = toggle_favorite(user["id"], product_id)
    flash("已加入收藏。" if added else "已取消收藏。", "success")
    source = request.form.get("source")
    if source == "favorites":
        return redirect(url_for("favorites"))
    if source == "listing":
        try:
            scroll_y = max(0, min(int(request.form.get("scroll_y", "0")), 100000))
        except (TypeError, ValueError):
            scroll_y = 0
        return redirect(url_for("index") + f"#scroll-y-{scroll_y}")
    return redirect(url_for("product_detail", product_id=product_id))


@app.get("/orders")
@login_required
def order_history():
    user = get_current_user()
    statuses = {"pending", "paid", "shipped", "delivered", "cancelled"}
    selected_status = request.args.get("status", "").strip()
    if selected_status not in statuses:
        selected_status = ""
    orders = get_orders_by_user(user["id"])
    if selected_status:
        orders = [order for order in orders if order["status"] == selected_status]
    return render_template("order_history.html", orders=orders, selected_status=selected_status)


@app.get("/seller")
@seller_required
def seller_dashboard():
    orders = get_admin_orders()
    products = get_all_products()
    counts = {status: sum(order["status"] == status for order in orders)
              for status in ("pending", "paid", "shipped", "delivered", "cancelled")}
    return render_template("seller_dashboard.html", counts=counts, product_count=len(products), order_count=len(orders))


@app.get("/seller/orders")
@seller_required
def seller_orders():
    statuses = {"pending", "paid", "shipped", "delivered", "cancelled"}
    selected_status = request.args.get("status", "").strip()
    if selected_status not in statuses:
        selected_status = ""
    return render_template("seller_orders.html", orders=get_admin_orders(selected_status), selected_status=selected_status)


@app.post("/seller/orders/<int:order_id>/status")
@seller_required
def seller_update_order_status(order_id):
    status = request.form.get("status", "")
    labels = {"pending": "處理中", "paid": "已付款", "shipped": "已出貨", "delivered": "已送達", "cancelled": "已取消"}
    if status not in labels:
        abort(400)
    user = get_current_user()
    try:
        previous = update_admin_order_status(order_id, status)
    except ValueError as error:
        flash(str(error), "warning")
        return redirect(url_for("seller_orders", status=request.form.get("return_status", "")))
    if previous is None:
        abort(404)
    if previous != status:
        log_admin_action(user["id"], "order_status", "order", order_id,
                         f"{labels[previous]} -> {labels[status]}")
        flash(f"訂單 #{order_id} 狀態已更新為「{labels[status]}」。", "success")
    current_filter = request.form.get("return_status", "")
    next_filter = status if current_filter and status != "cancelled" else current_filter
    return redirect(url_for("seller_orders", status=next_filter))


def seller_product_form_values():
    name = request.form.get("name", "").strip()
    if not name or len(name) > 160:
        raise ValueError("商品名稱請填寫 1 至 160 個字。")
    try:
        price = int(request.form.get("price", ""))
        stock = int(request.form.get("stock", ""))
        raw_rating = request.form.get("rating", "").strip()
        rating = float(raw_rating) if raw_rating else None
    except ValueError as error:
        raise ValueError("價格、庫存和評分請輸入有效數字。") from error
    if price < 0 or stock < 0 or (rating is not None and not 0 <= rating <= 5):
        raise ValueError("價格與庫存不可小於 0，評分需介於 0 至 5。")
    return {
        "name": name, "price": price,
        "description": request.form.get("description", "").strip(),
        "categories": request.form.get("categories", "").strip(),
        "stock": stock, "rating": rating,
        "colors": request.form.get("colors", "").strip(),
        "sizes": request.form.get("sizes", "").strip(),
        "photos": request.form.get("photos", "").strip(),
    }


@app.route("/seller/products", methods=["GET", "POST"])
@seller_required
def seller_products():
    if request.method == "POST":
        try:
            values = seller_product_form_values()
            product_id = add_product(**values)
        except (ValueError, TypeError) as error:
            flash(str(error), "warning")
        else:
            user = get_current_user()
            log_admin_action(user["id"], "product_created", "product", product_id, values["name"])
            flash("商品已新增。", "success")
            return redirect(url_for("seller_products"))
    return render_template("seller_products.html", products=get_all_products())


@app.route("/seller/products/<int:product_id>/edit", methods=["GET", "POST"])
@seller_required
def seller_edit_product(product_id):
    product = get_product_by_id(product_id)
    if product is None:
        abort(404)
    if request.method == "POST":
        try:
            values = seller_product_form_values()
            update_product(product_id, **values)
        except (ValueError, TypeError) as error:
            flash(str(error), "warning")
        else:
            user = get_current_user()
            log_admin_action(user["id"], "product_updated", "product", product_id, values["name"])
            flash("商品資料已更新。", "success")
            return redirect(url_for("seller_products"))
    return render_template("seller_product_form.html", product=product)


@app.post("/seller/products/<int:product_id>/delete")
@seller_required
def seller_delete_product(product_id):
    product = get_product_by_id(product_id)
    if product is None:
        abort(404)
    if delete_product(product_id):
        user = get_current_user()
        log_admin_action(user["id"], "product_deleted", "product", product_id, product["name"])
        flash("商品已刪除。", "success")
    return redirect(url_for("seller_products"))


@app.get("/seller/audit")
@seller_required
def seller_audit():
    return render_template("seller_audit.html", logs=get_admin_audit_logs())


@app.post("/add/<int:product_id>")
def add_to_cart(product_id):
    product = get_product_by_id(product_id)
    if product is None:
        abort(404)
    if get_current_user() is None:
        return redirect(url_for(
            "login",
            required="1",
            next=url_for("product_detail", product_id=product_id),
        ))
    try:
        quantity = int(request.form.get("quantity", "1"))
    except (TypeError, ValueError):
        quantity = 0
    colors = [value.strip() for value in (product.get("colors") or "Default").split(",") if value.strip()]
    sizes = [value.strip() for value in (product.get("sizes") or "One size").split(",") if value.strip()]
    # Keep the server-side accepted options aligned with the modal's fallback
    # values when a product has no color or size options configured.
    colors = colors or ["Default"]
    sizes = sizes or ["One size"]
    color = request.form.get("color", colors[0] if colors else "")
    size = request.form.get("size", sizes[0] if sizes else "")
    if color not in colors or size not in sizes or quantity < 1 or quantity > 99:
        flash("\u8acb\u9078\u64c7\u6709\u6548\u7684\u5546\u54c1\u898f\u683c\u8207\u6578\u91cf\u3002", "warning")
        return redirect(url_for("product_detail", product_id=product_id))
    cart = session.get("cart", {})
    key = f"{product_id}|{color}|{size}"
    existing = cart.get(key, 0)
    if not isinstance(existing, int) or existing < 0:
        existing = 0
    already_in_cart = sum(value for old_key, value in cart.items()
                          if str(old_key).split("|", 1)[0] == str(product_id)
                          and isinstance(value, int) and value > 0)
    if product["stock"] <= 0 or already_in_cart + quantity > product["stock"]:
        flash(f"此商品剩餘 {max(0, product['stock'] - already_in_cart)} 個。", "warning")
        return redirect(url_for("cart"))
    cart[key] = min(existing + quantity, 99)
    session["cart"] = cart
    return_to = request.args.get("return_to", "")
    parsed_return = urllib.parse.urlsplit(return_to)
    if (not return_to.startswith("/") or return_to.startswith("//")
            or parsed_return.netloc or parsed_return.scheme):
        return_to = url_for("product_detail", product_id=product_id)
    try:
        scroll_y = max(0, min(int(request.form.get("scroll_y", "0")), 100000))
    except (TypeError, ValueError):
        scroll_y = 0
    return_to += f"#scroll-y-{scroll_y}"
    return redirect(return_to)


@app.post("/cart/update/<int:product_id>")
def update_cart_quantity(product_id):
    cart = session.get("cart", {})
    key = request.form.get("cart_key", str(product_id))
    if not key.startswith(f"{product_id}|") and key != str(product_id):
        abort(400)
    try:
        quantity = int(request.form.get("quantity", ""))
    except (TypeError, ValueError):
        return redirect(url_for("cart"))
    product = get_product_by_id(product_id)
    if key in cart and product:
        other_quantity = sum(value for old_key, value in cart.items()
                             if old_key != key and str(old_key).split("|", 1)[0] == str(product_id)
                             and isinstance(value, int) and value > 0)
        max_quantity = min(99, product["stock"] - other_quantity)
        if max_quantity < 1:
            cart.pop(key, None)
        else:
            if quantity > max_quantity:
                flash(f"此商品剩餘 {max_quantity} 個。", "warning")
            cart[key] = min(max(1, quantity), max_quantity)
        session["cart"] = cart
    return redirect(url_for("cart"))


@app.post("/cart/remove/<int:product_id>")
def remove_from_cart(product_id):
    cart = session.get("cart", {})
    key = request.form.get("cart_key", str(product_id))
    if not key.startswith(f"{product_id}|") and key != str(product_id):
        abort(400)
    cart.pop(key, None)

    if cart:
        session["cart"] = cart
    else:
        session.pop("cart", None)

    return redirect(url_for("cart"))


@app.post("/clear")
def clear_cart():
    session.pop("cart", None)
    return redirect(url_for("cart"))


@app.post("/checkout")
@login_required
def checkout():
    cart = session.get("cart", {})
    if not cart:
        return redirect(url_for("index"))

    order_id = None
    try:
        user = get_current_user()
        order_id, total = create_order(cart, user_id=user["id"] if user else None, payment_method="linepay")
        base_url = os.environ.get("LINE_PAY_CALLBACK_BASE_URL", request.url_root.rstrip("/"))
        products = []
        for key, quantity in cart.items():
            product_id = int(str(key).split("|", 1)[0])
            product = get_product_by_id(product_id)
            if product:
                products.append({"id": str(product_id), "name": product["name"][:100], "quantity": int(quantity), "price": product["price"]})
        callback_token = linepay_callback_token(order_id)
        info = line_pay_request("/v3/payments/request", {
            "amount": total, "currency": "TWD", "orderId": str(order_id),
            "packages": [{"id": str(order_id), "amount": total, "products": products}],
            "redirectUrls": {
                "confirmUrl": base_url + url_for("linepay_confirm", orderId=order_id, token=callback_token),
                "cancelUrl": base_url + url_for("linepay_cancel", orderId=order_id, token=callback_token),
            },
        })
        transaction_id = info.get("transactionId")
        payment_url = (info.get("paymentUrl") or {}).get("web")
        if not transaction_id or not payment_url:
            raise RuntimeError("LINE Pay 回傳資料不完整，請稍後重試")
        if not set_line_transaction(order_id, transaction_id):
            raise RuntimeError("無法保存 LINE Pay 交易資料，請稍後重試")
        session.pop("cart", None)
        return redirect(payment_url)
    except (ValueError, TypeError, RuntimeError) as error:
        if order_id is not None:
            cancel_order_and_restore_stock(order_id)
        flash(str(error), "warning")
        return redirect(url_for("cart"))


@app.get("/payment/linepay/confirm")
def linepay_confirm():
    order_id = request.args.get("orderId", type=int)
    transaction_id = request.args.get("transactionId", type=str)
    order = get_order_for_payment(order_id) if order_id else None
    if (not order or not transaction_id or order["line_transaction_id"] != transaction_id
            or not hmac.compare_digest(request.args.get("token", ""), linepay_callback_token(order_id))):
        flash("找不到這筆 LINE Pay 付款資料。", "warning")
        return redirect(url_for("index"))
    if order["status"] == "paid":
        return render_template("checkout_success.html", order=get_order_details(order_id))
    try:
        line_pay_request(f"/v3/payments/{urllib.parse.quote(transaction_id, safe='')}/confirm", {"amount": order["total"], "currency": "TWD"})
    except RuntimeError as error:
        flash(str(error), "danger")
        return redirect(url_for("order_history") if order["user_id"] else url_for("index"))
    if complete_line_payment(order_id, transaction_id):
        return render_template("checkout_success.html", order=get_order_details(order_id))
    flash("LINE Pay 已回應付款，但訂單狀態尚未更新，請聯絡商店並提供訂單編號。", "warning")
    return redirect(url_for("order_history") if order["user_id"] else url_for("index"))


@app.get("/payment/linepay/cancel")
def linepay_cancel():
    order_id = request.args.get("orderId", type=int)
    if order_id and hmac.compare_digest(request.args.get("token", ""), linepay_callback_token(order_id)):
        order = get_order_for_payment(order_id)
        if order and order["payment_method"] == "linepay":
            cancel_order_and_restore_stock(order_id)
    flash("已取消 LINE Pay 付款，商品庫存已釋回。", "info")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
