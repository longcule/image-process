import requests
from fastapi import FastAPI, Query, Response

app = FastAPI()

class ImageDownloader:
    def get_image_response(self, url, auth=None):
        try:
            # Dùng đúng code của bạn
            response = requests.get(
                url, 
                headers={"User-Agent": "your bot 0.1"}, 
                auth=auth, 
                timeout=10, 
                verify=False
            )
            return response
        except Exception:
            return None

downloader = ImageDownloader()

@app.get("/proxy-image")
def proxy_image(url: str = Query(...)):
    # 1. Gọi hàm và nhận về đối tượng <requests.Response>
    res_from_origin = downloader.get_image_response(url)

    if res_from_origin is None:
        return Response(content="Lỗi kết nối", status_code=502)

    # 2. Trích xuất các thành phần giống hệt như requests đang có
    # để FastAPI trả về cho trình duyệt/client khác
    return Response(
        content=res_from_origin.content,           # Nội dung ảnh (bytes)
        status_code=res_from_origin.status_code,   # Giữ nguyên mã 200, 403, 404...
        headers={
            "Content-Type": res_from_origin.headers.get("Content-Type", ""),
            "Cache-Control": "public, max-age=86400"
        },
        media_type=res_from_origin.headers.get("Content-Type")
    )
