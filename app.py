
import os

from flask import Flask, abort, redirect, render_template, request, session, url_for

from database import (
    init_db,
    get_all_products,
    get_product_by_id,
    get_product_categories,
    create_order,
    get_order_details,
)

app = Flask(__name__)

app.secret_key = os.environ.get(
    "FLASK_SECRET_KEY",
    "dev-only-change-this-secret-key"
)

# 啟動時確認資料表存在
init_db()


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

    return render_template(
        "index.html",
        products=products,
        cart_items=cart_items,
        total=total,
        categories=categories,
        search=search,
        selected_category=category,
    )


@app.get("/product/<int:product_id>")
def product_detail(product_id):
    product = get_product_by_id(product_id)
    if product is None:
        abort(404)
    return render_template("product_detail.html", product=product)


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
        order_id, total = create_order(cart)

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
