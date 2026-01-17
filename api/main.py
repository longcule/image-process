from fastapi import FastAPI, HTTPException, Query, Response
import httpx
import logging

# Khai báo app
app = FastAPI(
    title="Image Proxy API",
    docs_url="/docs",
    openapi_url="/openapi.json"
)

class ImageProxy:
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"

    async def get_image_response(self, url: str):
        """
        Hàm xử lý logic lấy ảnh, sử dụng httpx để không gây blocking
        """
        headers = {
            "User-Agent": self.USER_AGENT,
            "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
            "Referer": url, # Một số site check Referer để chống hotlinking
            "Connection": "keep-alive",
        }
        
        async with httpx.AsyncClient(follow_redirects=True, verify=False) as client:
            try:
                response = await client.get(url, headers=headers, timeout=10.0)
                return response
            except httpx.TimeoutException:
                logging.error(f"Image: {url} connection timeout")
                return None
            except Exception as e:
                logging.error(f"Error fetching image: {str(e)}")
                return None

# Khởi tạo instance
proxy_service = ImageProxy()

@app.get("/")
async def root():
    return {"message": "API is running. Go to /docs for Swagger UI"}

@app.get("/proxy-image")
async def proxy_image(url: str = Query(..., description="URL của ảnh cần lấy")):
    # 1. Gọi hàm lấy response từ server gốc
    res = await proxy_service.get_image_response(url)

    # 2. Kiểm tra nếu có lỗi hoặc không có phản hồi
    if res is None:
        raise HTTPException(status_code=504, detail="Timeout hoặc lỗi kết nối khi lấy ảnh")
    
    if res.status_code != 200:
        # Nếu Cloudflare trả về 403, 404... ta trả về đúng mã đó cho client biết
        raise HTTPException(
            status_code=res.status_code, 
            detail=f"Server gốc từ chối truy cập (Mã lỗi: {res.status_code})"
        )

    # 3. Lấy định dạng ảnh (Content-Type)
    content_type = res.headers.get("Content-Type", "image/jpeg")
    
    # 4. Trả về Response chuẩn của FastAPI để trình duyệt hiển thị được ảnh
    return Response(content=res.content, media_type=content_type)

# Chạy local: uvicorn main:app --reload