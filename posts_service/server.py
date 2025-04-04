import grpc
from concurrent import futures
import time
from datetime import datetime
import json

import posts_service.post_pb2 as postservice_pb2
import posts_service.post_pb2_grpc as postservice_pb2_grpc
from google.protobuf.timestamp_pb2 import Timestamp
from database import get_connection, init_db

import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def iso_to_timestamp(iso_str):
    ts = Timestamp()
    dt = datetime.fromisoformat(iso_str)
    ts.FromDatetime(dt)
    return ts

def row_to_post(row):
    return postservice_pb2.Post(
        id=row['id'],
        title=row['title'],
        description=row['description'],
        creator_id=row['creator_id'],
        created_at=iso_to_timestamp(row['created_at']),
        updated_at=iso_to_timestamp(row['updated_at']),
        is_private=bool(row['is_private']),
        tags=json.loads(row['tags']) if row['tags'] else []
    )

class PostServiceServicer(postservice_pb2_grpc.PostServiceServicer):
    def CreatePost(self, request, context):
        now = datetime.utcnow().isoformat()
        tags_str = json.dumps(list(request.tags))
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO posts (title, description, creator_id, created_at, updated_at, is_private, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (request.title, request.description, request.user_id, now, now, int(request.is_private), tags_str))
        conn.commit()
        post_id = cursor.lastrowid
        conn.close()

        ts = iso_to_timestamp(now)
        post = postservice_pb2.Post(
            id=post_id,
            title=request.title,
            description=request.description,
            creator_id=request.user_id,
            created_at=ts,
            updated_at=ts,
            is_private=request.is_private,
            tags=request.tags
        )
        return postservice_pb2.CreatePostResponse(post=post)

    def DeletePost(self, request, context):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM posts WHERE id = ?', (request.post_id,))
        row = cursor.fetchone()
        if not row:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Post not found')
            conn.close()
            return postservice_pb2.DeletePostResponse(success=False)
        if row['creator_id'] != request.user_id:
            context.set_code(grpc.StatusCode.PERMISSION_DENIED)
            context.set_details('Not authorized to delete this post')
            conn.close()
            return postservice_pb2.DeletePostResponse(success=False)
        cursor.execute('DELETE FROM posts WHERE id = ?', (request.post_id,))
        conn.commit()
        conn.close()
        return postservice_pb2.DeletePostResponse(success=True)

    def UpdatePost(self, request, context):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM posts WHERE id = ?', (request.post_id,))
        row = cursor.fetchone()
        if not row:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Post not found')
            conn.close()
            return postservice_pb2.UpdatePostResponse()
        if row['creator_id'] != request.user_id:
            context.set_code(grpc.StatusCode.PERMISSION_DENIED)
            context.set_details('Not authorized to update this post')
            conn.close()
            return postservice_pb2.UpdatePostResponse()
        
        title = request.title if request.title else row['title']
        description = request.description if request.description else row['description']
        is_private = int(request.is_private)
        tags_str = json.dumps(list(request.tags)) if request.tags else row['tags']
        now = datetime.utcnow().isoformat()
        
        cursor.execute('''
            UPDATE posts
            SET title = ?, description = ?, is_private = ?, tags = ?, updated_at = ?
            WHERE id = ?
        ''', (title, description, is_private, tags_str, now, request.post_id))
        conn.commit()
        cursor.execute('SELECT * FROM posts WHERE id = ?', (request.post_id,))
        updated_row = cursor.fetchone()
        conn.close()
        post = row_to_post(updated_row)
        return postservice_pb2.UpdatePostResponse(post=post)

    def GetPostById(self, request, context):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM posts WHERE id = ?', (request.post_id,))
        row = cursor.fetchone()
        conn.close()
        if not row:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Post not found')
            return postservice_pb2.GetPostByIdResponse()
        if row['is_private'] and row['creator_id'] != request.user_id:
            context.set_code(grpc.StatusCode.PERMISSION_DENIED)
            context.set_details('Not authorized to view this post')
            return postservice_pb2.GetPostByIdResponse()
        post = row_to_post(row)
        return postservice_pb2.GetPostByIdResponse(post=post)

    def ListPosts(self, request, context):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM posts')
        rows = cursor.fetchall()
        conn.close()
        filtered = []
        for row in rows:
            if row['is_private']:
                if row['creator_id'] == request.user_id:
                    filtered.append(row)
            else:
                filtered.append(row)
        page_size = request.page_size if request.page_size > 0 else 10
        page_number = request.page_number if request.page_number > 0 else 1
        start = (page_number - 1) * page_size
        paginated = filtered[start:start + page_size]
        total_pages = (len(filtered) + page_size - 1) // page_size
        posts_list = [row_to_post(row) for row in paginated]
        return postservice_pb2.ListPostsResponse(
            posts=posts_list,
            total_pages=total_pages,
            current_page=page_number
        )

def serve():
    init_db()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    postservice_pb2_grpc.add_PostServiceServicer_to_server(PostServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Server started on port 50051...")
    logger.info("Server started on port 50051.")
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()
