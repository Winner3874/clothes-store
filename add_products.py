"""後端商品管理工具：新增、修改或刪除商品。"""

from pathlib import Path

from database import (
    add_product,
    delete_product,
    get_all_products,
    get_product_by_id,
    init_db,
    update_product,
)

PROJECT_DIR = Path(__file__).resolve().parent
IMAGE_DIR = PROJECT_DIR / "static" / "uploads" / "products"
IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp")


def ask(prompt, default=""):
    suffix = f" [{default}]" if default != "" else ""
    value = input(f"{prompt}{suffix}: ").strip()
    return value if value else default


def ask_int(prompt, default=None, minimum=0):
    while True:
        raw = ask(prompt, "" if default is None else str(default))
        try:
            number = int(raw)
            if number >= minimum:
                return number
        except ValueError:
            pass
        print(f"請輸入大於或等於 {minimum} 的整數。")


def ask_rating(default=None, *, allow_clear=False):
    while True:
        hint = "留白代表不評分" if default is None else f"目前 {default}；輸入 - 清除評分"
        raw = input(f"評分 0–5 ({hint}): ").strip()
        if not raw:
            return default
        if allow_clear and raw == "-":
            return None
        try:
            rating = float(raw)
            if 0 <= rating <= 5:
                return rating
        except ValueError:
            pass
        print("評分請輸入 0 到 5 的數字；新增商品可留白不評分。")


def check_photo_names(photo_csv):
    missing = []
    for item in (value.strip() for value in photo_csv.split(",")):
        if not item or item.startswith(("http://", "https://", "/")):
            continue
        name = Path(item).name
        candidates = [IMAGE_DIR / name] if Path(name).suffix else [IMAGE_DIR / f"{name}{ext}" for ext in IMAGE_EXTENSIONS]
        if not any(path.is_file() for path in candidates):
            missing.append(name)
    return missing


def show_products():
    products = get_all_products()
    if not products:
        print("目前沒有商品。")
        return
    print("\n商品清單：")
    for product in products:
        rating = "未評分" if product["rating"] is None else f"{product['rating']}/5"
        print(f"  ID {product['id']} | {product['name']} | NT$ {product['price']} | 評分 {rating}")


def ask_product_fields(product=None):
    editing = product is not None
    def existing(key, fallback=""):
        return str(product[key] if product[key] is not None else fallback) if editing else ""

    name = ask("商品名稱", existing("name"))
    if not name:
        print("商品名稱不能空白。")
        return None
    price = ask_int("價格", product["price"] if editing else None)
    description = ask("商品介紹", existing("desc"))
    categories = ask("分類（逗號分隔，可新增分類）", existing("categories"))
    stock = ask_int("庫存", product["stock"] if editing else 20)
    rating = ask_rating(product["rating"] if editing else None, allow_clear=editing)
    colors = ask("顏色（逗號分隔）", existing("colors", "Black,White") if editing else "Black,White")
    sizes = ask("尺寸（逗號分隔）", existing("sizes", "S,M,L") if editing else "S,M,L")
    photos = ask("照片檔名（逗號分隔，放在 static/uploads/products）", existing("photos"))
    return {
        "name": name,
        "price": price,
        "description": description,
        "categories": categories,
        "stock": stock,
        "rating": rating,
        "colors": colors,
        "sizes": sizes,
        "photos": photos,
    }


def report_photos(photos):
    missing = check_photo_names(photos)
    if missing:
        print(f"找不到這些照片，請放入 {IMAGE_DIR}：{', '.join(missing)}")
    else:
        print(f"照片資料夾：{IMAGE_DIR}")


def create_product():
    values = ask_product_fields()
    if values is None:
        return
    product_id = add_product(**values)
    print(f"商品已新增，ID={product_id}")
    report_photos(values["photos"])


def edit_product():
    show_products()
    product_id = ask_int("要修改的商品 ID")
    product = get_product_by_id(product_id)
    if product is None:
        print("找不到這個商品 ID。")
        return
    print("直接按 Enter 保留原值；評分輸入 - 可清除。")
    values = ask_product_fields(product)
    if values is None:
        return
    if update_product(product_id, **values):
        print(f"商品 ID={product_id} 已更新。")
        report_photos(values["photos"])
    else:
        print("商品不存在，沒有更新。")


def remove_product():
    show_products()
    product_id = ask_int("要刪除的商品 ID")
    product = get_product_by_id(product_id)
    if product is None:
        print("找不到這個商品 ID。")
        return
    confirm = input(f"確定刪除「{product['name']}」？請輸入商品 ID {product_id} 確認：").strip()
    if confirm != str(product_id):
        print("已取消刪除。")
        return
    if delete_product(product_id):
        print("商品已刪除。")
    else:
        print("商品不存在，沒有刪除。")


def main():
    init_db()
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    while True:
        print("\nStyleLab 後端商品管理")
        print("1. 新增商品")
        print("2. 修改商品")
        print("3. 刪除商品")
        print("4. 查看商品")
        print("0. 離開")
        choice = input("請選擇：").strip()
        if choice == "1":
            create_product()
        elif choice == "2":
            edit_product()
        elif choice == "3":
            remove_product()
        elif choice == "4":
            show_products()
        elif choice == "0":
            break
        else:
            print("請輸入 0 到 4。")


if __name__ == "__main__":
    main()
