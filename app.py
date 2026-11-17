
import os
import sqlite3
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
    username_exists,
    update_user_password,
    get_user_by_id,
    get_favorite_product_ids,
    get_favorite_products,
    toggle_favorite,
    get_orders_by_user,
)

app = Flask(__name__)

app.secret_key = os.environ.get(
    "FLASK_SECRET_KEY",
    "dev-only-change-this-secret-key"
)

# 啟動時確認資料表存在
init_db()


def get_current_user():
    user_id = session.get("user_id")
    if user_id is None:
        return None
    user = get_user_by_id(user_id)
    if user is None:
        session.pop("user_id", None)
    return user


@app.context_processor
def inject_current_user():
    return {"current_user": get_current_user(), "cart_count": sum(q for q in session.get("cart", {}).values() if isinstance(q, int) and q > 0)}


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if get_current_user() is None:
            flash("請先登入會員。", "warning")
            return redirect(url_for("login"))
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
            flash("Username 須為 1 到 40 個英數字、底線或連字號。", "danger")
        elif email and ("@" not in email or "." not in email or len(email) > 254):
            flash("請輸入有效的電子郵件地址。", "danger")
        elif len(password) < 8 or len(password) > 256:
            flash("密碼長度需為 8 到 256 個字元。", "danger")
        elif password != confirm_password:
            flash("兩次輸入的密碼不一致。", "danger")
        elif username_exists(username):
            flash("這個 username 已經有人使用，請換一個。", "warning")
        else:
            try:
                user_id = create_user(name, username, email, generate_password_hash(password))
            except sqlite3.IntegrityError:
                flash("username 或電子郵件已被使用。", "warning")
            else:
                session["user_id"] = user_id
                flash("註冊成功，歡迎加入！", "success")
                return redirect(url_for("index"))
    return render_template("auth.html", mode="register")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = get_user_by_username(username)
        if user is None or not check_password_hash(user["password_hash"], password):
            flash("Username 或密碼不正確。", "danger")
        else:
            session["user_id"] = user["id"]
            flash(f"歡迎回來，{user['username']}！", "success")
            return redirect(url_for("index"))
    return render_template("auth.html", mode="login")


@app.get("/profile")
@login_required
def profile():
    return render_template("profile.html", user=get_current_user())


@app.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    user = get_current_user()
    if request.method == "POST":
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        if len(password) < 8 or len(password) > 256:
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
        return redirect(url_for("index"))
    return redirect(url_for("product_detail", product_id=product_id))


@app.get("/orders")
@login_required
def order_history():
    user = get_current_user()
    orders = get_orders_by_user(user["id"])
    return render_template("order_history.html", orders=orders)


@app.post("/add/<int:product_id>")
def add_to_cart(product_id):
    product = get_product_by_id(product_id)
    if product is None:
        abort(404)
    try:
        quantity = int(request.form.get("quantity", "1"))
    except (TypeError, ValueError):
        quantity = 0
    colors = [value.strip() for value in product["colors"].split(",") if value.strip()]
    sizes = [value.strip() for value in product["sizes"].split(",") if value.strip()]
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
        flash(f"\u76ee\u524d\u5eab\u5b58\u50c5\u5269 {product['stock']} \u4ef6\u3002", "warning")
        return redirect(url_for("cart"))
    cart[key] = min(existing + quantity, 99)
    session["cart"] = cart
    return redirect(url_for("cart"))


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
def checkout():
    cart = session.get("cart", {})

    if not cart:
        return redirect(url_for("index"))

    try:
        user = get_current_user()
        order_id, total = create_order(
            cart, user_id=user["id"] if user else None
        )

    except (ValueError, TypeError) as error:
        flash(str(error), "warning")
        return redirect(url_for("index"))

    # 從資料庫重新讀取剛建立的訂單
    order = get_order_details(order_id)

    # 訂單建立成功後才清空購物車
    session.pop("cart", None)

    return render_template(
        "checkout_success.html",
        order=order,
    )


if __name__ == "__main__":
    app.run(debug=True)
