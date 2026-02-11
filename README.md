# 酷澎連結轉換工具

自動展開酷澎短連結並生成聯盟網追蹤連結的完整解決方案。

## 📦 檔案說明

- `app.py` - Flask 後端 API
- `index.html` - 前端頁面（整合版，需要後端）
- `requirements.txt` - Python 依賴套件
- `vercel.json` - Vercel 部署配置

## 🚀 本地測試

### 1. 安裝 Python 依賴

```bash
pip install -r requirements.txt
```

### 2. 啟動後端 API

```bash
python app.py
```

API 會在 `http://localhost:5000` 運行

### 3. 開啟前端頁面

直接用瀏覽器打開 `index.html` 即可使用

## 🌐 部署到 Vercel（免費）

### 方法一：透過 GitHub

1. 將所有檔案上傳到 GitHub repository
2. 到 [Vercel](https://vercel.com) 註冊/登入
3. 點擊 "New Project"
4. 選擇你的 GitHub repository
5. 直接點擊 "Deploy"（Vercel 會自動識別配置）

### 方法二：透過 Vercel CLI

```bash
# 安裝 Vercel CLI
npm i -g vercel

# 在專案目錄執行
vercel

# 第一次會要求登入，之後按照提示操作即可
```

部署成功後，你會得到一個網址，例如：`https://your-project.vercel.app`

然後在前端頁面的「API 端點」欄位填入這個網址即可！

## 📝 使用說明

1. **貼上連結**：可以是酷澎短連結 (`link.tw.coupang.com/a/xxxx`) 或完整連結
2. **填入 Base Tracking URL**：你的聯盟網追蹤連結
3. **選填追蹤標籤**：subid_1 ~ subid_5, unique_id
4. **點擊生成**：自動展開並生成追蹤連結
5. **複製使用**：點擊「複製連結」按鈕

## 🔧 API 端點說明

### POST /api/generate-tracking

生成追蹤連結（包含自動展開短連結）

**請求範例：**
```json
{
  "product_url": "https://link.tw.coupang.com/a/xxxxx",
  "base_url": "https://vbtrax.com/track/clicks/3559/...",
  "sub_ids": {
    "subid_1": "user123",
    "subid_2": "campaign"
  }
}
```

**回應範例：**
```json
{
  "success": true,
  "original_url": "https://link.tw.coupang.com/a/xxxxx",
  "expanded_url": "https://www.coupang.com.tw/vp/products/xxxxx",
  "tracking_url": "https://vbtrax.com/track/clicks/3559/...?subid_1=user123&subid_2=campaign&t=...",
  "is_short_link": true
}
```

## ⚙️ 其他部署選項

### Render（免費）

1. 到 [Render](https://render.com) 註冊
2. 選擇 "New Web Service"
3. 連接 GitHub repository
4. 設定：
   - Environment: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`

### Railway（免費）

1. 到 [Railway](https://railway.app) 註冊
2. "New Project" → "Deploy from GitHub repo"
3. 選擇你的 repository
4. Railway 會自動偵測並部署

## 🛠️ 技術架構

- **後端**：Python + Flask
- **前端**：原生 HTML/CSS/JavaScript
- **CORS**：支援跨域請求
- **展開機制**：HTTP 重定向追蹤

## 📞 支援

如有問題請聯繫開發團隊。
