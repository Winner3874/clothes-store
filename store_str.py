from flask import Flask, redirect, render_template_string, session, url_for

app = Flask(__name__)
# 設定密鑰以啟用 session（用來儲存購物車資料）
app.secret_key = "my_super_secret_key"

# 模擬資料庫中的商品列表
PRODUCTS = [
    {
        "id": 1,
        "name": "極簡機械鍵盤",
        "price": 2500,
        "desc": "手感極佳的青軸機械鍵盤",
        "img": "⌨️",
    },
    {
        "id": 2,
        "name": "無線電競滑鼠",
        "price": 1200,
        "desc": "超低延遲、人體工學設計",
        "img": "🖱️",
    },
    {
        "id": 3,
        "name": "抗噪藍牙耳機",
        "price": 3800,
        "desc": "沉浸式音質，主動降噪功能",
        "img": "🎧",
    },
    {
        "id": 4,
        "name": "4K 護眼螢幕",
        "price": 8900,
        "desc": "27吋 IPS 面板，色彩精準",
        "img": "🖥️",
    },
]

# 網頁的 HTML 模板 (結合 Bootstrap 5 美化介面)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <title>Python 迷你商店</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .product-icon { font-size: 4rem; text-align: center; margin: 15px 0; }
        .card { transition: transform 0.2s; }
        .card:hover { transform: translateY(-5px); box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
    </style>
</head>
<body class="bg-light">

<nav class="navbar navbar-dark bg-dark mb-4">
    <div class="container">
        <a class="navbar-brand" href="/">🐍 Python 3C 販賣鋪</a>
    </div>
</nav>

<div class="container">
    <div class="row">
        <!-- 左側：商品列表 -->
        <div class="col-md-8">
            <h4 class="mb-3">熱門商品</h4>
            <div class="row">
                {% for p in products %}
                <div class="col-md-6 mb-4">
                    <div class="card h-100">
                        <div class="product-icon">{{ p.img }}</div>
                        <div class="card-body d-flex flex-column">
                            <h5 class="card-title">{{ p.name }}</h5>
                            <p class="card-text text-muted">{{ p.desc }}</p>
                            <div class="mt-auto d-flex justify-content-between align-items-center">
                                <span class="fs-5 fw-bold text-danger">NT$ {{ p.price }}</span>
                                <a href="/add/{{ p.id }}" class="btn btn-primary">加入購物車</a>
                            </div>
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>

        <!-- 右側：購物車 -->
        <div class="col-md-4">
            <div class="card shadow-sm">
                <div class="card-header bg-success text-white">
                    <h5 class="mb-0">🛒 您的購物車</h5>
                </div>
                <div class="card-body">
                    {% if cart_items %}
                        <ul class="list-group list-group-flush mb-3">
                            {% for item in cart_items %}
                            <li class="list-group-item d-flex justify-content-between align-items-center px-0">
                                <div>
                                    <h6 class="my-0">{{ item.name }}</h6>
                                    <small class="text-muted">單價: ${{ item.price }} x {{ item.qty }}</small>
                                </div>
                                <span class="text-muted">NT$ {{ item.subtotal }}</span>
                            </li>
                            {% endfor %}
                        </ul>
                        <div class="d-flex justify-content-between mb-3">
                            <span>總計 (新台幣)</span>
                            <strong class="fs-5 text-success">NT$ {{ total }}</strong>
                        </div>
                        <div class="d-grid gap-2">
                            <a href="/checkout" class="btn btn-success" onclick="alert('感謝您的購買！訂單已送出！')">立即結帳</a>
                            <a href="/clear" class="btn btn-outline-danger btn-sm">清空購物車</a>
                        </div>
                    {% else %}
                        <p class="text-muted text-center my-4">購物車目前是空的喔！</p>
                    {% endif %}
                </div>
            </div>
        </div>
    </div>
</div>

</body>
</html>
"""


@app.route("/")
def index():
    # 從 session 取得購物車內容，格式為 {'商品ID': 數量}
    cart = session.get("cart", {})
    cart_items = []
    total = 0

    for prod_id, qty in cart.items():
        # 尋找對應的商品資料
        product = next((p for p in PRODUCTS if p["id"] == int(prod_id)), None)
        if product:
            subtotal = product["price"] * qty
            total += subtotal
            cart_items.append({
                "name": product["name"],
                "price": product["price"],
                "qty": qty,
                "subtotal": subtotal,
            })

    return render_template_string(
        HTML_TEMPLATE, products=PRODUCTS, cart_items=cart_items, total=total
    )


@app.route("/add/<int:product_id>")
def add_to_cart(product_id):
    cart = session.get("cart", {})
    str_id = str(product_id)

    # 如果商品已在購物車則數量+1，否則設為1
    if str_id in cart:
        cart[str_id] += 1
    else:
        cart[str_id] = 1

    session["cart"] = cart
    return redirect(url_for("index"))


@app.route("/clear")
def clear_cart():
    session.pop("cart", None)
    return redirect(url_for("index"))


@app.route("/checkout")
def checkout():
    # 這裡未來可以串接資料庫儲存訂單，或是串接金流
    session.pop("cart", None)
    return redirect(url_for("index"))



if __name__ == "__main__":
    app.run(debug=True)

#先輸入pip install flask，再輸入python store_str.py
