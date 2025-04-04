import os
import json
from fastapi import FastAPI, Request, Response, HTTPException, Header, Depends
import httpx
import grpc
import grpc.aio
import jwt

import gateway_service.post_pb2 as postservice_pb2
import gateway_service.post_pb2_grpc as postservice_pb2_grpc
from google.protobuf.json_format import MessageToDict

app = FastAPI(title="Gateway Service")

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user_service:8000")
POST_SERVICE_ADDRESS = os.getenv("POST_SERVICE_ADDRESS", "posts_service:50051")

JWT_SECRET = os.getenv("JWT_SECRET", "SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

grpc_channel = grpc.aio.insecure_channel(POST_SERVICE_ADDRESS)
posts_stub = postservice_pb2_grpc.PostServiceStub(grpc_channel)

@app.on_event("shutdown")
async def shutdown_event():
    await grpc_channel.close()

async def get_current_user(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    token = authorization[len("Bearer "):]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.exceptions.PyJWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    user_id = payload.get("user_id")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Token missing user id")
    return user_id

@app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy(full_path: str, request: Request, authorization: str = Header(None)):
    if full_path.startswith("posts"):
        if not authorization:
            raise HTTPException(status_code=401, detail="Missing auth token")
        user_id = await get_current_user(authorization)
        return await handle_posts_request(full_path, request, user_id)
    else:
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

async def handle_posts_request(full_path: str, request: Request, current_user: str) -> Response:
    try:
        uid = int(current_user)
    except ValueError:
        raise HTTPException(status_code=401, detail="User id in token must be numeric")
    
    path_parts = full_path.split("/")    
    if len(path_parts) == 1 or (len(path_parts) == 2 and path_parts[1] == ""):
        if request.method == "GET":
            try:
                page_number = int(request.query_params.get("page_number", "1"))
                page_size = int(request.query_params.get("page_size", "10"))
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid query parameter format")
            grpc_req = postservice_pb2.ListPostsRequest(
                user_id=uid,
                page_number=page_number,
                page_size=page_size
            )
            grpc_resp = await posts_stub.ListPosts(grpc_req)
            return Response(
                content=json.dumps(MessageToDict(grpc_resp, preserving_proto_field_name=True)),
                media_type="application/json"
            )
        elif request.method == "POST":
            body = await request.json()
            grpc_req = postservice_pb2.CreatePostRequest(
                user_id=uid,
                title=body.get("title"),
                description=body.get("description"),
                is_private=body.get("is_private", False),
                tags=body.get("tags", [])
            )
            grpc_resp = await posts_stub.CreatePost(grpc_req)
            return Response(
                content=json.dumps(MessageToDict(grpc_resp, preserving_proto_field_name=True)),
                media_type="application/json"
            )
        else:
            raise HTTPException(status_code=405, detail="Method not allowed on /posts")
    
    elif len(path_parts) >= 2:
        try:
            post_id = int(path_parts[1])
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid post ID")
        
        if request.method == "GET":
            grpc_req = postservice_pb2.GetPostByIdRequest(
                user_id=uid,
                post_id=post_id
            )
            grpc_resp = await posts_stub.GetPostById(grpc_req)
            return Response(
                content=json.dumps(MessageToDict(grpc_resp, preserving_proto_field_name=True)),
                media_type="application/json"
            )
        elif request.method == "PUT":
            body = await request.json()
            grpc_req = postservice_pb2.UpdatePostRequest(
                user_id=uid,
                post_id=post_id,
                title=body.get("title", ""),
                description=body.get("description", ""),
                is_private=body.get("is_private", False),
                tags=body.get("tags", [])
            )
            grpc_resp = await posts_stub.UpdatePost(grpc_req)
            return Response(
                content=json.dumps(MessageToDict(grpc_resp, preserving_proto_field_name=True)),
                media_type="application/json"
            )
        elif request.method == "DELETE":
            grpc_req = postservice_pb2.DeletePostRequest(
                user_id=uid,
                post_id=post_id
            )
            grpc_resp = await posts_stub.DeletePost(grpc_req)
            return Response(
                content=json.dumps(MessageToDict(grpc_resp, preserving_proto_field_name=True)),
                media_type="application/json"
            )
        else:
            raise HTTPException(status_code=405, detail="Method not allowed on /posts/{id}")
    else:
        raise HTTPException(status_code=404, detail="Invalid posts path")