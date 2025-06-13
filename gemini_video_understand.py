import google.generativeai as genai
from google.ai import generativelanguage as types
genai.configure(api_key='AIzaSyC5lKSpC33Bm1lJmMFuaSfA_0viHJqiWek')

# 初始化客戶端，指定模型名稱
client = genai.GenerativeModel('gemini-2.5-flash-preview-05-20')

response = client.generate_content(
    contents=[
        {
            "file_data": {
                "file_uri": 'https://www.youtube.com/watch?v=S7ARexSGEGo'
            }
        },
        'Please summarize the video.輸出繁體中文'
    ]
)

print(response.text)