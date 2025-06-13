from fastapi import FastAPI, Query, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
import google.generativeai as genai
from google.ai import generativelanguage as types
import os
from dotenv import load_dotenv
import uvicorn
from typing import Optional

# 載入環境變數
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

# 檢查 API 金鑰是否設定
if not API_KEY:
    raise ValueError("GEMINI_API_KEY 環境變數未設定。請在 .env 檔案中設定此變數。")

# 配置 Gemini API
genai.configure(api_key=API_KEY)

# 初始化模型
model = genai.GenerativeModel('gemini-2.5-flash-preview-05-20')

# 建立 FastAPI 應用
app = FastAPI(
    title="YouTube Gemini 摘要 API",
    description="一個使用 Google Gemini 模型摘要 YouTube 影片的 API",
    version="1.0.0",
)

# 設定 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生產環境中應該設定為特定的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 定義請求模型
class VideoRequest(BaseModel):
    youtube_url: HttpUrl
    prompt: Optional[str] = "Please summarize the video. 輸出繁體中文"

# 定義回應模型
class VideoSummary(BaseModel):
    summary: str

class ErrorResponse(BaseModel):
    error: str

# 檢查 API 金鑰函數
def verify_api_key():
    if not API_KEY:
        raise HTTPException(status_code=500, detail="API 金鑰未設定")
    return True

@app.get("/")
def read_root():
    """API 根路徑，返回歡迎信息"""
    return {"message": "歡迎使用 YouTube Gemini 摘要 API", "status": "運行中"}

@app.get("/health")
def health_check():
    """健康檢查端點"""
    return {"status": "healthy"}

@app.get("/summarize", response_model=VideoSummary, responses={500: {"model": ErrorResponse}})
def summarize_youtube_video(
    url: str = Query(..., description="YouTube 視頻連結"),
    _: bool = Depends(verify_api_key)
):
    """
    使用 Gemini 模型摘要指定的 YouTube 影片（繁體中文）
    
    - **url**: YouTube 影片網址
    
    回傳:
    - **summary**: 影片的中文摘要
    """
    try:
        response = model.generate_content(
            contents=[
                {"file_data": {"file_uri": url}},
                "Please summarize the video. 輸出繁體中文"
            ]
        )
        return {"summary": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/summarize", response_model=VideoSummary, responses={500: {"model": ErrorResponse}})
def summarize_youtube_video_post(
    request: VideoRequest,
    _: bool = Depends(verify_api_key)
):
    """
    使用 Gemini 模型摘要指定的 YouTube 影片（POST 方法）
    
    - **request**: 包含 YouTube 網址和可選提示的請求
    
    回傳:
    - **summary**: 影片的中文摘要
    """
    try:
        response = model.generate_content(
            contents=[
                {"file_data": {"file_uri": str(request.youtube_url)}},
                request.prompt
            ]
        )
        return {"summary": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 啟動應用
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
