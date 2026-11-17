# 商品資料庫操作指南

本專案的 SQLite 資料庫是根目錄的 `store.db`。新增商品最簡單的方法是執行 `add_products.py`；也可以用 DB Browser for SQLite 直接編輯 `products` 資料表。

## 方法一：用互動程式新增商品

1. 把商品圖片放進 `static/uploads/products/`。
2. 在專案根目錄開啟終端機，執行：

   ```powershell
   python add_products.py
   ```

3. 依序輸入名稱、價格、介紹、分類、庫存、評分、顏色、尺寸和照片檔名。
4. 分類和照片都可以用逗號分隔，例如 `上衣,新品,夏季`、`front,back`。
5. 程式會新增資料、列出新商品 ID，並提醒尚未找到的照片檔名。

照片檔名可省略副檔名。若輸入 `front,back`，程式會依序尋找 `front.jpg`、`front.jpeg`、`front.png`、`front.webp`，再以相同方式尋找 `back`。若資料夾內有同名的多種格式，會優先使用 JPG、JPEG、PNG、WebP 的順序。

## 方法二：用 DB Browser 直接新增／編輯

1. 開啟專案根目錄的 `store.db`。
2. 打開 `products` 資料表，新增一列。`id` 留白，由 SQLite 自動編號。
3. 填商品資料：

   - `name`：商品名稱
   - `price`：整數價格，例如 `1280`
   - `description`：商品介紹，詳細頁也使用這個欄位
   - `categories`：分類清單，以逗號分隔，可直接輸入新分類，例如 `上衣,新品,夏季`
   - `photos`：照片檔名清單，以逗號分隔，可省略副檔名，例如 `front,back`
   - `stock`：非負整數庫存
   - `rating`：0 到 5，例如 `4.5`
   - `colors`：顏色清單，例如 `奶油白,深藍`
   - `sizes`：尺寸清單，例如 `S,M,L,XL`

4. 按 DB Browser 的 **Write Changes** 儲存資料，再重新整理商店頁面。

分類名稱不需先建立，也不必另外新增分類資料表的列；網站會從所有商品的 `categories` 欄位自動整理分類按鈕。逗號是分隔符，因此分類名稱本身不要含逗號。

照片檔案不是存進 SQLite。`photos` 欄位只記錄檔名，實際圖片需放在 `static/uploads/products/`。允許填 `front.jpg,back.png`，也允許填 `front,back`。

## 賣家庫存與照片頁

首頁頁尾的庫存連結會直接打開管理頁，不需要賣家登入。該頁可以調整庫存或上傳圖片；圖片支援 JPG、PNG、WebP，每次最多 12 張、每張最多 5 MB。上傳後檔案會存入 `static/uploads/products/`，並自動把檔名加入商品的 `photos` 欄位。詳細頁會顯示多張照片並提供縮圖切換。

## 資料表補充

- `products.categories` 和 `products.photos` 是日常直接編輯的逗號分隔欄位。
- 舊欄位 `products.category`、`products.image_url` 仍保留以相容既有資料；網站優先讀取 `categories`、`photos`。
- `product_categories`、`product_images` 是舊版遷移留下的相容資料表；使用互動新增程式或直接編輯 `products` 時不必手動操作它們。
- `details` 欄位已移除；商品介紹統一使用 `description`。

## 後端商品管理選單

在專案目錄執行 `python add_products.py`，即可選擇新增、修改、刪除或查看商品。修改商品時按 Enter 保留目前欄位；評分欄位輸入 `-` 可清除評分。新增商品的評分可以直接留白。沒有評分的商品，商品詳細頁不會顯示評分區塊。

刪除商品時需要再次輸入商品 ID 確認。商品的照片檔案請放在 `static/uploads/products/`，照片欄位填檔名，多張照片以逗號分隔。
