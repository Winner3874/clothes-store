
import os
import sqlite3
from functools import wraps

from flask import Flask, abort, flash, redirect, render_template, request, session, url_for
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
    return {"current_user": get_current_user()}


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if get_current_user() is None:
            flash("請先登入會員。", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped_view


def get_cart_items():
    """根據購物車中的商品 ID，從資料庫取得商品資訊。"""
    cart = session.get("cart", {})
    cart_items = []
    total = 0

    for product_id, quantity in cart.items():
        product = get_product_by_id(int(product_id))

        if product and isinstance(quantity, int) and quantity > 0:
            subtotal = product["price"] * quantity

            cart_items.append({
                **product,
                "qty": quantity,
                "subtotal": subtotal,
            })

            total += subtotal

    return cart_items, total


@app.get("/")
def index():
    search = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()
    products = get_all_products(search=search, category=category)
    categories = get_product_categories()
    cart_items, total = get_cart_items()
    current_user = get_current_user()
    favorite_product_ids = (
        get_favorite_product_ids(current_user["id"]) if current_user else set()
    )

    return render_template(
        "index.html",
        products=products,
        cart_items=cart_items,
        total=total,
        categories=categories,
        search=search,
        selected_category=category,
        favorite_product_ids=favorite_product_ids,
    )


@app.get("/product/<int:product_id>")
def product_detail(product_id):
    product = get_product_by_id(product_id)
    if product is None:
        abort(404)
    current_user = get_current_user()
    is_favorite = (
        product_id in get_favorite_product_ids(current_user["id"])
        if current_user else False
    )
    return render_template(
        "product_detail.html", product=product, is_favorite=is_favorite
    )


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


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
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
            return redirect(url_for("profile"))
    return render_template("profile.html", user=user)


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
    # 商品必須存在於資料庫中
    if get_product_by_id(product_id) is None:
        return redirect(url_for("index"))

    cart = session.get("cart", {})
    key = str(product_id)

    current_quantity = cart.get(key, 0)
    if not isinstance(current_quantity, int) or current_quantity < 0:
        current_quantity = 0
    cart[key] = min(current_quantity + 1, 99)
    session["cart"] = cart

    return redirect(url_for("index"))


@app.post("/cart/update/<int:product_id>")
def update_cart_quantity(product_id):
    cart = session.get("cart", {})
    key = str(product_id)

    try:
        quantity = int(request.form.get("quantity", ""))
    except (TypeError, ValueError):
        return redirect(url_for("index"))

    if key in cart and get_product_by_id(product_id) and 1 <= quantity <= 99:
        cart[key] = quantity
        session["cart"] = cart

    return redirect(url_for("index"))


@app.post("/cart/remove/<int:product_id>")
def remove_from_cart(product_id):
    cart = session.get("cart", {})
    cart.pop(str(product_id), None)

    if cart:
        session["cart"] = cart
    else:
        session.pop("cart", None)

    return redirect(url_for("index"))


@app.post("/clear")
def clear_cart():
    session.pop("cart", None)
    return redirect(url_for("index"))


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

    except (ValueError, TypeError):
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
