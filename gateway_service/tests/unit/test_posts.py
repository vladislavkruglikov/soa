import json
from fastapi.testclient import TestClient
from google.protobuf.timestamp_pb2 import Timestamp

import gateway_service.post_pb2 as postservice_pb2
import gateway_service.post_pb2_grpc as postservice_pb2_grpc
import gateway_service.main as gateway


class FakePostsStub:
    async def CreatePost(self, request):
        ts = Timestamp()
        ts.GetCurrentTime()
        return postservice_pb2.CreatePostResponse(
            post=postservice_pb2.Post(
                id=1,
                title=request.title,
                description=request.description,
                creator_id=request.user_id,
                created_at=ts,
                updated_at=ts,
                is_private=request.is_private,
                tags=list(request.tags)
            )
        )

    async def ListPosts(self, request):
        ts = Timestamp()
        ts.GetCurrentTime()
        posts = [
            postservice_pb2.Post(
                id=1,
                title="Post 1",
                description="Desc 1",
                creator_id=request.user_id,
                created_at=ts,
                updated_at=ts,
                is_private=False,
                tags=["tag1"]
            ),
            postservice_pb2.Post(
                id=2,
                title="Post 2",
                description="Desc 2",
                creator_id=request.user_id,
                created_at=ts,
                updated_at=ts,
                is_private=False,
                tags=["tag2"]
            ),
        ]
        return postservice_pb2.ListPostsResponse(
            posts=posts, total_pages=1, current_page=request.page_number
        )

    async def GetPostById(self, request):
        ts = Timestamp()
        ts.GetCurrentTime()
        return postservice_pb2.GetPostByIdResponse(
            post=postservice_pb2.Post(
                id=request.post_id,
                title="Post",
                description="Description",
                creator_id=request.user_id,
                created_at=ts,
                updated_at=ts,
                is_private=False,
                tags=["tag"]
            )
        )

    async def UpdatePost(self, request):
        ts = Timestamp()
        ts.GetCurrentTime()
        return postservice_pb2.UpdatePostResponse(
            post=postservice_pb2.Post(
                id=request.post_id,
                title=request.title,
                description=request.description,
                creator_id=request.user_id,
                created_at=ts,
                updated_at=ts,
                is_private=request.is_private,
                tags=list(request.tags)
            )
        )

    async def DeletePost(self, request):
        return postservice_pb2.DeletePostResponse(success=True)

gateway.posts_stub = FakePostsStub()

client = TestClient(gateway.app)

def test_create_post():
    payload = {
        "user_id": 1,
        "title": "Test Post",
        "description": "Testing",
        "is_private": False,
        "tags": ["test"]
    }
    response = client.post("/posts", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "post" in data
    assert data["post"]["title"] == "Test Post"

def test_list_posts():
    params = {"user_id": "1", "page_number": "1", "page_size": "10"}
    response = client.get("/posts", params=params)
    assert response.status_code == 200
    data = response.json()
    assert "posts" in data
    assert "currentPage" in data
    assert data["currentPage"] == 1

def test_get_post_by_id():
    params = {"user_id": "1"}
    response = client.get("/posts/1", params=params)
    assert response.status_code == 200
    data = response.json()
    assert "post" in data
    assert int(data["post"]["id"]) == 1

def test_update_post():
    payload = {
        "user_id": 1,
        "title": "Updated Title",
        "description": "Updated Description",
        "is_private": False,
        "tags": ["updated"]
    }
    response = client.put("/posts/1", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "post" in data
    assert data["post"]["title"] == "Updated Title"

def test_delete_post():
    params = {"user_id": "1"}
    response = client.delete("/posts/1", params=params)
    assert response.status_code == 200
    data = response.json()
    assert "success" in data
    assert data["success"] is True
