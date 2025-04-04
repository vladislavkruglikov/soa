import os
import pytest
import grpc
from concurrent import futures

import posts_service.post_pb2 as postservice_pb2
import posts_service.post_pb2_grpc as postservice_pb2_grpc
from server import PostServiceServicer
from database import init_db

@pytest.fixture(scope="module", autouse=True)
def cleanup_db():
    db_file = "posts.db"
    if os.path.exists(db_file):
        os.remove(db_file)
    init_db()
    yield
    if os.path.exists(db_file):
        os.remove(db_file)

@pytest.fixture(scope="module")
def grpc_server_address():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    postservice_pb2_grpc.add_PostServiceServicer_to_server(PostServiceServicer(), server)
    port = server.add_insecure_port("localhost:0")
    server.start()
    address = f"localhost:{port}"
    yield address
    server.stop(0)

@pytest.fixture
def stub(grpc_server_address):
    channel = grpc.insecure_channel(grpc_server_address)
    return postservice_pb2_grpc.PostServiceStub(channel)

def test_create_post(stub):
    response = stub.CreatePost(
        postservice_pb2.CreatePostRequest(
            user_id=1,
            title="Test Post",
            description="Test Description",
            is_private=False,
            tags=["tag1", "tag2"],
        )
    )
    assert response.post.id > 0
    assert response.post.title == "Test Post"
    assert response.post.creator_id == 1

def test_get_post_by_id(stub):
    create_resp = stub.CreatePost(
        postservice_pb2.CreatePostRequest(
            user_id=1,
            title="Get Test",
            description="Test",
            is_private=False,
            tags=["tag"],
        )
    )
    post_id = create_resp.post.id
    get_resp = stub.GetPostById(
        postservice_pb2.GetPostByIdRequest(user_id=1, post_id=post_id)
    )
    assert get_resp.post.id == post_id

def test_update_post(stub):
    create_resp = stub.CreatePost(
        postservice_pb2.CreatePostRequest(
            user_id=1,
            title="Original Title",
            description="Original Desc",
            is_private=False,
            tags=["tag1"],
        )
    )
    post_id = create_resp.post.id
    update_resp = stub.UpdatePost(
        postservice_pb2.UpdatePostRequest(
            user_id=1,
            post_id=post_id,
            title="Updated Title",
            description="Updated Desc",
            is_private=False,
            tags=["tag2"],
        )
    )
    assert update_resp.post.title == "Updated Title"
    assert update_resp.post.description == "Updated Desc"
    assert update_resp.post.tags == ["tag2"]

def test_delete_post(stub):
    create_resp = stub.CreatePost(
        postservice_pb2.CreatePostRequest(
            user_id=1,
            title="Delete Test",
            description="Test",
            is_private=False,
            tags=["tag"],
        )
    )
    post_id = create_resp.post.id
    delete_resp = stub.DeletePost(
        postservice_pb2.DeletePostRequest(user_id=1, post_id=post_id)
    )
    assert delete_resp.success is True

    with pytest.raises(grpc.RpcError) as exc_info:
        stub.GetPostById(
            postservice_pb2.GetPostByIdRequest(user_id=1, post_id=post_id)
        )
    assert exc_info.value.code() == grpc.StatusCode.NOT_FOUND

def test_list_posts(stub):
    for i in range(5):
        stub.CreatePost(
            postservice_pb2.CreatePostRequest(
                user_id=1,
                title=f"List Post {i}",
                description="Test",
                is_private=False,
                tags=["tag"],
            )
        )
    list_resp = stub.ListPosts(
        postservice_pb2.ListPostsRequest(user_id=1, page_number=1, page_size=3)
    )
    assert len(list_resp.posts) == 3
    assert list_resp.current_page == 1
    assert list_resp.total_pages >= 2

def test_private_post_access(stub):
    create_resp = stub.CreatePost(
        postservice_pb2.CreatePostRequest(
            user_id=1,
            title="Private Post",
            description="Test",
            is_private=True,
            tags=["tag"],
        )
    )
    post_id = create_resp.post.id
    with pytest.raises(grpc.RpcError) as exc_info:
        stub.GetPostById(
            postservice_pb2.GetPostByIdRequest(user_id=2, post_id=post_id)
        )
    assert exc_info.value.code() == grpc.StatusCode.PERMISSION_DENIED
