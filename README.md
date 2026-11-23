# StyleLab Store

以 Flask、SQLite、HTML、CSS 與 JavaScript 製作的服飾商店示範網站。包含商品瀏覽與搜尋、會員登入、購物車、訂單、賣家管理介面，以及 LINE Pay Sandbox 結帳流程。

## 功能

- 商品首頁、分類瀏覽、商品詳細資訊、尺寸與顏色選擇及庫存顯示。
- 商品名稱、描述與分類的模糊搜尋；支援中文拼音比對（需安裝 `pypinyin`）。
- 會員註冊、登入、個人資料、收藏、訂單紀錄，以及 Google OAuth 登入與帳號連結。
- Session 購物車、庫存檢查、數量調整與金額計算。
- 賣家後台可管理商品、庫存及訂單，並查看管理操作紀錄。
- LINE Pay Online API v3 Sandbox 付款請求、付款確認及取消處理。

## 專案結構

```text
clothes-store/
├── app.py                 # Flask 路由、登入流程、購物車、結帳與 LINE Pay
├── database.py            # SQLite 初始化、資料查詢與更新
├── add_products.py        # 命令列商品管理工具
├── create_admin.py        # 建立賣家管理員帳號
├── requirements.txt       # Python 套件
├── templates/             # Jinja HTML 頁面模板
├── static/
│   ├── css/style.css      # 網站樣式
│   ├── js/main.js         # 前端互動
│   └── uploads/           # 商品圖片與會員頭像
├── SELLER_SETUP.md        # 賣家帳號建立說明
└── README.md
```

資料庫使用專案根目錄的 `store.db`。應用程式啟動時會自動初始化資料表；資料庫檔案已列入 `.gitignore`。

## 環境需求

- Python 3.10 或更新版本
- pip
- Google 登入或 LINE Pay 付款為選用功能；使用時需各自設定憑證

## 安裝與啟動

請在專案根目錄執行以下命令。第一次啟動會安裝相依套件並建立本機 SQLite 資料庫。

### Windows PowerShell

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python app.py
```

如果 PowerShell 阻止虛擬環境啟動腳本，可在目前 PowerShell 視窗執行以下命令後，再啟動虛擬環境：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

若使用命令提示字元（CMD），啟動命令改為：

```bat
.venv\Scripts\activate.bat
```

### Linux（含 WSL / Ubuntu）

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python app.py
```

若系統尚未安裝 venv 模組（例如 Ubuntu），先安裝 Python 與 venv 套件：

```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip
```

啟動後在瀏覽器開啟 <http://127.0.0.1:5000>。停止伺服器可在終端機按 `Ctrl+C`；離開虛擬環境可執行 `deactivate`。

## 環境設定

應用程式會讀取專案根目錄 `.env` 中的 `KEY=VALUE` 設定。`.env` 已加入 `.gitignore`，請勿提交密碼或金鑰。只有使用 Google 登入或 LINE Pay 時才需要設定對應的值。

### Google OAuth（選用）

1. 在 Google Cloud Console 建立 OAuth 2.0 Web 用戶端。
2. 將 `http://127.0.0.1:5000/auth/google/callback` 加入授權重新導向 URI。
3. 在專案根目錄新增 `.env`，填入：

```dotenv
GOOGLE_CLIENT_ID=你的用戶端ID
GOOGLE_CLIENT_SECRET=你的用戶端密鑰
FLASK_SECRET_KEY=請換成隨機且長度足夠的秘密字串
```

`FLASK_SECRET_KEY` 用於 Flask Session 與 LINE Pay 回呼驗證。部署或多人共用環境務必設定為隨機秘密值；不要使用程式內建的開發用預設值。

### LINE Pay Sandbox（選用）

請建立 LINE Pay Sandbox Channel，並在 `.env` 加入：

```dotenv
LINE_PAY_CHANNEL_ID=你的SandboxChannelID
LINE_PAY_CHANNEL_SECRET=你的SandboxChannelSecret
LINE_PAY_API_BASE=https://sandbox-api-pay.line.me
LINE_PAY_CALLBACK_BASE_URL=https://可由外部連線的HTTPS網址
```

LINE Pay 必須能從網際網路連到回呼網址；`localhost` 與 `127.0.0.1` 無法供 LINE Pay 服務回連。本機測試可使用公開 HTTPS 開發通道，並將該網址設為 `LINE_PAY_CALLBACK_BASE_URL`。若網站本身已使用可公開連線的 HTTPS 網址，則可省略此設定。

此專案預設呼叫 Sandbox API。正式環境須改用正式 Channel 憑證與 `https://api-pay.line.me`，並部署在安全、可公開連線的 HTTPS 網站。

## 建立賣家帳號

在已啟動虛擬環境的專案根目錄執行：

```bash
python create_admin.py
```

Windows PowerShell 同樣使用 `python create_admin.py`。依提示輸入賣家帳號、名稱及至少 8 個字元的密碼；電子郵件可留白。此工具會建立新的賣家帳號，不會更改既有會員。更多說明請見 [SELLER_SETUP.md](SELLER_SETUP.md)。

## 管理商品

```bash
python add_products.py
```

Windows PowerShell 使用相同命令。依命令列提示新增或維護商品；商品圖片可放在 `static/uploads/products/`，會員頭像放在 `static/uploads/avatars/`。

## 常見問題

- **`python` 找不到：** Windows 可試 `py -3`；Linux 可試 `python3`，並確認已安裝 Python。
- **無法啟動虛擬環境：** PowerShell 請參考上方執行原則指令；CMD 使用 `activate.bat`；Linux 使用 `source .venv/bin/activate`。
- **Google 登入失敗：** 確認 `.env` 的 Client ID、Secret 與 Google Console 登入重新導向 URI 完全一致。
- **LINE Pay 無法付款或回呼：** 確認 Sandbox 憑證正確，且 `LINE_PAY_CALLBACK_BASE_URL` 是 LINE Pay 可連線的公開 HTTPS 網址。
- **要重設本機資料：** 停止伺服器後刪除專案根目錄的 `store.db`，重新執行 `python app.py` 會建立新的資料庫。刪除資料庫會一併移除本機會員、商品與訂單資料。

## 注意事項

`python app.py` 適合本機開發與課程展示。Flask 開發伺服器、開發用密鑰及 Sandbox 金流不適合直接用於正式營運；正式部署前需設定安全密鑰、正式金流憑證與 HTTPS，並使用正式 WSGI 伺服器及適當的資料備份方式。
