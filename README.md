# Gemini AI 多功能服務 API

這是一個使用 Google Gemini 模型打造的多功能後端服務，基於 FastAPI 框架開發。它不僅提供強大的 AI 功能，還具備高擴展性和模組化的架構，支持通過 Cloudflare 反向代理部署。

## ✨ 主要功能

- **📝 YouTube 影片摘要**: 輸入 YouTube 連結，快速生成影片的繁體中文摘要。
- **📄 文件理解**: 上傳文件（如 PDF、PPT），API 會提取並整理其核心內容。
- **🌐 智能問答 (Grounding)**: 結合 Google 搜索，提供更具事實基礎的問答體驗。
- **🎨 文字生成圖片**: 根據文字描述創造出獨特的圖片。
- **🖼️ 圖片編輯**: 上傳一張圖片，並透過文字指令對其進行修改。

## 🏗️ 部署方式

### 方式一：本地開發

1.  **克隆專案**:
    ```bash
    git clone <repository-url>
    cd gemini_api
    ```

2.  **安裝依賴**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **設定環境變數**:
    在專案根目錄下建立一個 `.env` 檔案，並填入您的 Gemini API 金鑰：
    ```
    GEMINI_API_KEY="YOUR_API_KEY_HERE"
    ```

4.  **啟動服務**:
    ```bash
    python main.py
    ```
    服務將在 `http://localhost:8001` 上運行。

### 方式二：Docker 部署

1.  **設定環境變數**:
    ```bash
    cp example.env .env
    # 編輯 .env 文件，設置你的 GEMINI_API_KEY
    nano .env
    ```

2.  **使用 Docker Compose 啟動**:
    ```bash
    docker-compose up -d
    ```
    服務將在 `http://localhost` 上運行，通過 Nginx 反向代理。

### 方式三：Cloudflare 反向代理部署 🌟

1.  **快速部署**:
    ```bash
    ./deploy.sh your-domain.com
    ```

2.  **手動配置** (詳細步驟請查看 [CLOUDFLARE_SETUP.md](CLOUDFLARE_SETUP.md)):
    - 將代碼部署到 VPS 服務器
    - 在 Cloudflare 添加域名
    - 配置 DNS 記錄指向服務器
    - 設置 SSL/TLS 為 "Full" 模式
    - 配置防火墻和安全規則

#### Cloudflare 部署的優勢：
- � **免費 SSL 證書**
- 🛡️ **DDoS 防護**
- 🌍 **全球 CDN 加速**
- 📊 **流量分析**
- 🔥 **隱藏真實服務器 IP**

## �📚 API 端點說明

您可以訪問 `http://localhost:8001/docs` 或 `https://api.yourdomain.com/docs` 來查看完整的 Swagger UI 互動式 API 文件。

---

### 影片與文件處理

-   **`POST /summarize`**: 摘要指定的 YouTube 影片。
    -   **Request Body**: `{"youtube_url": "...", "prompt": "..."}`
    -   **Curl 範例**:
        ```bash
        curl -X POST "https://api.yourdomain.com/summarize" \
          -H "Content-Type: application/json" \
          -d '{"youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "prompt": "請總結這部影片"}'
        ```
-   **`POST /doc`**: 上傳並分析文件內容。
    -   **Request Body**: `multipart/form-data`，包含一個 `file` 欄位。
    -   **Curl 範例**:
        ```bash
        curl -X POST "https://api.yourdomain.com/doc" \
          -H "Content-Type: multipart/form-data" \
          -F "file=@/path/to/your/document.pdf"
        ```

### 智能查詢

-   **`POST /grounding`**: 根據提供的查詢進行 Google 搜索並生成回覆。
    -   **Request Body**: `{"query": "...", "use_google_search": true}`
    -   **Curl 範例**:
        ```bash
        curl -X POST "https://api.yourdomain.com/grounding" \
          -H "Content-Type: application/json" \
          -d '{"query": "台灣最高的山是哪一座？", "use_google_search": true}'
        ```

### 圖片處理 (前綴: `/images`)

-   **`POST /images/text-to-image`**: 根據文字提示生成圖片。
    -   **Request Body**: `{"prompt": "A cat wearing a hat", "return_base64": false}`
    -   **Curl 範例**:
        ```bash
        curl -X POST "https://api.yourdomain.com/images/text-to-image" \
          -H "Content-Type: application/json" \
          -d '{"prompt": "一個戴著帽子的貓", "return_base64": false}'
        ```
-   **`POST /images/edit-image`**: 上傳圖片並根據文字指令進行修改。
    -   **Request Body**: `multipart/form-data`，包含 `prompt` (文字指令) 和 `file` (圖片檔案) 兩個欄位。
    -   **Curl 範例**:
        ```bash
        curl -X POST "https://api.yourdomain.com/images/edit-image" \
          -H "Content-Type: multipart/form-data" \
          -F "prompt=把天空變成黃昏" \
          -F "file=@/path/to/your/image.jpg"
        ```
-   **`GET /images/download/{filename}`**: 下載先前生成或編輯過的圖片。
    -   **Curl 範例**:
        ```bash
        curl -X GET "https://api.yourdomain.com/images/download/generated_image.png" \
          -o "downloaded_image.png"
        ```

### 系統

-   **`GET /`**: API 根目錄，顯示歡迎訊息和功能列表。
-   **`GET /health`**: 健康檢查端點，確認服務是否正常運行。

## 🔧 配置文件說明

- **`docker-compose.yaml`**: Docker 容器編排配置
- **`nginx.conf`**: Nginx 反向代理配置
- **`Dockerfile`**: Docker 鏡像構建配置
- **`.env`**: 環境變數配置（從 `example.env` 複製）
- **`CLOUDFLARE_SETUP.md`**: Cloudflare 部署詳細指南
- **`deploy.sh`**: 一鍵部署腳本

## 🛡️ 安全考慮

- 使用環境變數存儲敏感信息
- 通過 Nginx 配置請求大小限制
- Cloudflare 提供 DDoS 防護和 WAF
- 建議配置速率限制和 IP 白名單

## 📈 監控和維護

```bash
# 查看服務狀態
docker-compose ps

# 查看日志
docker-compose logs -f

# 重啟服務
docker-compose restart

# 停止服務
docker-compose down
```

## 🔗 相關資源

- [Cloudflare 部署指南](CLOUDFLARE_SETUP.md)
- [Google Gemini API 文檔](https://ai.google.dev/gemini-api/docs)
- [FastAPI 文檔](https://fastapi.tiangolo.com/)
- [Docker Compose 文檔](https://docs.docker.com/compose/)

## ⚠️ 注意事項

-   請確保您的 `GEMINI_API_KEY` 是有效且保密的。
-   `.gitignore` 檔案已設定忽略 `.env` 檔案，請勿將其提交到版本控制系統中。
-   在生產環境中，建議設置適當的 CORS 策略。
-   定期更新依賴包以確保安全性。