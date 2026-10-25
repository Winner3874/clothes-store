
import os

from flask import Flask, redirect, render_template, session, url_for

from database import (
    init_db,
    get_all_products,
    get_product_by_id,
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
    products = get_all_products()
    cart_items, total = get_cart_items()

    return render_template(
        "index.html",
        products=products,
        cart_items=cart_items,
        total=total,
    )


@app.post("/add/<int:product_id>")
def add_to_cart(product_id):
    # 商品必須存在於資料庫中
    if get_product_by_id(product_id) is None:
        return redirect(url_for("index"))

    cart = session.get("cart", {})
    key = str(product_id)

    cart[key] = cart.get(key, 0) + 1
    session["cart"] = cart

    return redirect(url_for("index"))


@app.post("/clear")
def clear_cart():
    session.pop("cart", None)
    return redirect(url_for("index"))


@app.post("/checkout")
def checkout():
    cart_items, total = get_cart_items()

    if not cart_items:
        return redirect(url_for("index"))

    session.pop("cart", None)

    # 目前僅為展示用結帳，不會真的收款或建立正式訂單
    return render_template(
        "checkout_success.html",
        total=total,
    )


if __name__ == "__main__":
    app.run(debug=True)
