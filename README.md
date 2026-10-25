# StyleLab Store — Flask 商店原型

這是把原本單一 Python 檔案中的 HTML、CSS 和 JavaScript 拆開後的版本。

## 專案結構

```text
stylelab-store/
├── app.py
├── requirements.txt
├── templates/
│   ├── index.html
│   └── checkout_success.html
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
├── .gitignore
└── README.md
```

## 在 WSL Ubuntu 執行

在專案根目錄執行：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

然後在瀏覽器開啟 http://127.0.0.1:5000 。

## 目前功能

- 顯示示範商品
- 將商品加入 session 購物車
- 顯示購物車小計與總價
- 清空購物車
- 示範結帳流程

## 尚未完成

商品仍是寫死的假資料，沒有會員系統、資料庫、正式訂單、庫存管理或第三方金流。結帳按鈕不會收款。`app.secret_key` 目前是開發用範例值，正式部署前必須改為環境變數中的隨機密鑰，並關閉 debug 模式。
