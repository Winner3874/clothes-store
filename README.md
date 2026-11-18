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

## 店主庫存管理

先設定店主管理帳密，再啟動 Flask。PowerShell 範例：

```powershell
$env:ADMIN_USERNAME = "store-owner"
$env:ADMIN_PASSWORD = "請改成自己的長密碼"
python app.py
```

開啟商店頁面最下方的「賣家管理」，登入後可更新各商品庫存。舊資料庫會在程式啟動時自動新增庫存欄位，既有商品初始庫存為 20 件。商品售出後會在結帳時扣除庫存。

## 目前功能

- 顯示示範商品
- 將商品加入 session 購物車
- 顯示購物車小計與總價
- 清空購物車
- 示範結帳流程
- 商品庫存顯示、店主庫存管理與結帳扣庫存

## 尚未完成

商品仍是示範資料，結帳為示範流程，不會收款。`app.secret_key` 目前是開發用範例值，正式部署前必須改為環境變數中的隨機密鑰，並關閉 debug 模式。

## Google 帳號登入設定

1. 在 Google Cloud Console 建立 OAuth 2.0 網頁用戶端，授權重新導向 URI 設為 `http://127.0.0.1:5000/auth/google/callback`（正式站請換成正式網域）。
2. 在專案根目錄建立 `.env`（已列入 `.gitignore`），填入 OAuth 憑證與固定的隨機 Flask 密鑰：

```text
GOOGLE_CLIENT_ID=你的用戶端 ID
GOOGLE_CLIENT_SECRET=你的用戶端密鑰
FLASK_SECRET_KEY=請設定隨機且固定的長字串
```

應用程式啟動時會讀取 `.env`；作業系統已設定的環境變數優先。

Google 登入會以 Google 回傳的已驗證電子郵件識別會員；若該電子郵件已存在，會將 Google 身分連結到該會員。首次 Google 登入會自動建立會員。
