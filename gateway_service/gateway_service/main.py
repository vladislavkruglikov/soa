import os
from fastapi import FastAPI, Request, Response
import httpx

app = FastAPI(title="Gateway Service")

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user_service:8000")

@app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy(full_path: str, request: Request):
    url = f"{USER_SERVICE_URL}/{full_path}"
    method = request.method
    headers = dict(request.headers)
    headers.pop("host", None)
    query = request.url.query
    body = await request.body()
    
    async with httpx.AsyncClient() as client:
        proxy_response = await client.request(
            method=method,
            url=url,
            headers=headers,
            params=query,
            content=body
        )
    
    return Response(
        content=proxy_response.content,
        status_code=proxy_response.status_code,
        headers=dict(proxy_response.headers)
    )
