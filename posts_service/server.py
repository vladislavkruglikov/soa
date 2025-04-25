import grpc
from concurrent import futures
import time
from datetime import datetime
import json
import sqlite3

import post_pb2 as postservice_pb2
import post_pb2_grpc as postservice_pb2_grpc
from google.protobuf.timestamp_pb2 import Timestamp
from database import get_connection, init_db
from kafka_config import get_kafka_producer, send_post_like_event, send_post_view_event, send_post_comment_event

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
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) as count FROM likes WHERE post_id = ?', (row['id'],))
    likes_count = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) as count FROM views WHERE post_id = ?', (row['id'],))
    views_count = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) as count FROM comments WHERE post_id = ?', (row['id'],))
    comments_count = cursor.fetchone()['count']
    
    conn.close()
    
    logger.info(f"Creating Post with likes_count: {likes_count} (type: {type(likes_count)})")
    post = postservice_pb2.Post(
        id=row['id'],
        title=row['title'],
        description=row['description'],
        creator_id=row['creator_id'],
        created_at=iso_to_timestamp(row['created_at']),
        updated_at=iso_to_timestamp(row['updated_at']),
        is_private=bool(row['is_private']),
        tags=json.loads(row['tags']) if row['tags'] else [],
        likes_count=likes_count,
        views_count=views_count,
        comments_count=comments_count
    )
    logger.info(f"Created Post message: {post}")
    return post

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
            tags=request.tags,
            likes_count=0,
            views_count=0,
            comments_count=0
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
        
        if not row:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Post not found')
            conn.close()
            return postservice_pb2.GetPostByIdResponse()
            
        if row['is_private'] and row['creator_id'] != request.user_id:
            context.set_code(grpc.StatusCode.PERMISSION_DENIED)
            context.set_details('Not authorized to view this post')
            conn.close()
            return postservice_pb2.GetPostByIdResponse()

        try:
            now = datetime.utcnow()
            logger.info(f"Recording view for post {request.post_id} by user {request.user_id} at {now}")
            cursor.execute('''
                INSERT INTO views (post_id, user_id, created_at)
                VALUES (?, ?, ?)
            ''', (request.post_id, request.user_id, now.isoformat()))
            conn.commit()

            producer = get_kafka_producer()
            send_post_view_event(producer, request.user_id, request.post_id, now)
            producer.close()
        except sqlite3.IntegrityError:
            # User already viewed this post
            pass

        post = row_to_post(row)
        conn.close()
        return postservice_pb2.GetPostByIdResponse(post=post)

    def ListPosts(self, request, context):
        conn = get_connection()
        cursor = conn.cursor()        
        cursor.execute('SELECT * FROM posts')
        rows = cursor.fetchall()
        logger.info(f"Found {len(rows)} posts")
        
        post_ids = [row['id'] for row in rows]
        logger.info(f"Post IDs: {post_ids}")
        
        likes_counts = {}
        if post_ids:
            placeholders = ','.join(['?' for _ in post_ids])
            query = f'''
                SELECT p.id as post_id, COUNT(l.id) as count 
                FROM posts p
                LEFT JOIN likes l ON p.id = l.post_id
                WHERE p.id IN ({placeholders})
                GROUP BY p.id
            '''
            logger.info(f"Executing likes query: {query}")
            cursor.execute(query, post_ids)
            likes_rows = cursor.fetchall()
            logger.info(f"Likes query result: {likes_rows}")
            likes_counts = {row['post_id']: row['count'] for row in likes_rows}
        
        logger.info(f"Likes counts: {likes_counts}")
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
        
        posts_list = []
        for row in paginated:
            likes_count = likes_counts.get(row['id'], 0)
            logger.info(f"Post {row['id']} has {likes_count} likes")
            post = postservice_pb2.Post(
                id=row['id'],
                title=row['title'],
                description=row['description'],
                creator_id=row['creator_id'],
                created_at=iso_to_timestamp(row['created_at']),
                updated_at=iso_to_timestamp(row['updated_at']),
                is_private=bool(row['is_private']),
                tags=json.loads(row['tags']) if row['tags'] else [],
                likes_count=likes_count,
                views_count=0,
                comments_count=0
            )
            logger.info(f"Created Post message: {post}")
            posts_list.append(post)
            
        response = postservice_pb2.ListPostsResponse(
            posts=posts_list,
            total_pages=total_pages,
            current_page=page_number
        )
        logger.info(f"Created ListPostsResponse: {response}")
        return response

    def LikePost(self, request, context):
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM posts WHERE id = ?', (request.post_id,))
        post = cursor.fetchone()
        if not post:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Post not found')
            conn.close()
            return postservice_pb2.LikePostResponse(success=False, likes_count=0)
        
        if post['is_private'] and post['creator_id'] != request.user_id:
            context.set_code(grpc.StatusCode.PERMISSION_DENIED)
            context.set_details('Not authorized to like this post')
            conn.close()
            return postservice_pb2.LikePostResponse(success=False, likes_count=0)
        
        try:
            now = datetime.utcnow()
            cursor.execute('''
                INSERT INTO likes (post_id, user_id, created_at)
                VALUES (?, ?, ?)
            ''', (request.post_id, request.user_id, now.isoformat()))
            conn.commit()
            
            cursor.execute('SELECT COUNT(*) as count FROM likes WHERE post_id = ?', (request.post_id,))
            likes_count = cursor.fetchone()['count']
            conn.close()

            producer = get_kafka_producer()
            send_post_like_event(producer, request.user_id, request.post_id, now)
            producer.close()

            return postservice_pb2.LikePostResponse(success=True, likes_count=likes_count)
        except sqlite3.IntegrityError:
            # User already liked this post
            conn.close()
            return postservice_pb2.LikePostResponse(success=False, likes_count=0)

    def UnlikePost(self, request, context):
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM posts WHERE id = ?', (request.post_id,))
        post = cursor.fetchone()
        if not post:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Post not found')
            conn.close()
            return postservice_pb2.UnlikePostResponse(success=False, likes_count=0)
        
        if post['is_private'] and post['creator_id'] != request.user_id:
            context.set_code(grpc.StatusCode.PERMISSION_DENIED)
            context.set_details('Not authorized to unlike this post')
            conn.close()
            return postservice_pb2.UnlikePostResponse(success=False, likes_count=0)
        
        cursor.execute('DELETE FROM likes WHERE post_id = ? AND user_id = ?', (request.post_id, request.user_id))
        conn.commit()
        
        cursor.execute('SELECT COUNT(*) as count FROM likes WHERE post_id = ?', (request.post_id,))
        likes_count = cursor.fetchone()['count']
        conn.close()
        return postservice_pb2.UnlikePostResponse(success=True, likes_count=likes_count)

    def CreateComment(self, request, context):
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM posts WHERE id = ?', (request.post_id,))
        post = cursor.fetchone()
        if not post:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Post not found')
            conn.close()
            return postservice_pb2.CreateCommentResponse()
            
        if post['is_private'] and post['creator_id'] != request.user_id:
            context.set_code(grpc.StatusCode.PERMISSION_DENIED)
            context.set_details('Not authorized to comment on this post')
            conn.close()
            return postservice_pb2.CreateCommentResponse()
        
        try:
            now = datetime.utcnow()
            cursor.execute('''
                INSERT INTO comments (post_id, user_id, content, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (request.post_id, request.user_id, request.content, now.isoformat(), now.isoformat()))
            conn.commit()
            comment_id = cursor.lastrowid
            
            cursor.execute('SELECT * FROM comments WHERE id = ?', (comment_id,))
            comment_row = cursor.fetchone()
            
            comment = postservice_pb2.Comment(
                id=comment_row['id'],
                post_id=comment_row['post_id'],
                user_id=comment_row['user_id'],
                content=comment_row['content'],
                created_at=iso_to_timestamp(comment_row['created_at']),
                updated_at=iso_to_timestamp(comment_row['updated_at'])
            )
            
            producer = get_kafka_producer()
            send_post_comment_event(producer, request.user_id, request.post_id, comment_id, now)
            producer.close()
            
            conn.close()
            return postservice_pb2.CreateCommentResponse(comment=comment)
            
        except Exception as e:
            logger.error(f"Error creating comment: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('Error creating comment')
            conn.close()
            return postservice_pb2.CreateCommentResponse()

    def ListComments(self, request, context):
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM posts WHERE id = ?', (request.post_id,))
        post = cursor.fetchone()
        if not post:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Post not found')
            conn.close()
            return postservice_pb2.ListCommentsResponse()
            
        if post['is_private'] and post['creator_id'] != request.user_id:
            context.set_code(grpc.StatusCode.PERMISSION_DENIED)
            context.set_details('Not authorized to view comments on this post')
            conn.close()
            return postservice_pb2.ListCommentsResponse()
        
        cursor.execute('SELECT COUNT(*) as count FROM comments WHERE post_id = ?', (request.post_id,))
        total_comments = cursor.fetchone()['count']
        
        page_size = request.page_size if request.page_size > 0 else 10
        page_number = request.page_number if request.page_number > 0 else 1
        offset = (page_number - 1) * page_size
        
        cursor.execute('''
            SELECT * FROM comments 
            WHERE post_id = ? 
            ORDER BY created_at DESC 
            LIMIT ? OFFSET ?
        ''', (request.post_id, page_size, offset))
        
        comment_rows = cursor.fetchall()
        conn.close()
        
        comments = []
        for row in comment_rows:
            comment = postservice_pb2.Comment(
                id=row['id'],
                post_id=row['post_id'],
                user_id=row['user_id'],
                content=row['content'],
                created_at=iso_to_timestamp(row['created_at']),
                updated_at=iso_to_timestamp(row['updated_at'])
            )
            comments.append(comment)
        
        total_pages = (total_comments + page_size - 1) // page_size
        
        return postservice_pb2.ListCommentsResponse(
            comments=comments,
            total_pages=total_pages,
            current_page=page_number
        )

def serve():
    try:
        from post_pb2 import Post
        test_post = Post()
        test_post.likes_count = 1
        logger.info(f"Proto files verified. Test post: {test_post}")
    except Exception as e:
        logger.error(f"Error verifying proto files: {e}")
        raise

    init_db()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    postservice_pb2_grpc.add_PostServiceServicer_to_server(PostServiceServicer(), server)
    server.add_insecure_port('[::]:50052')
    server.start()
    print("Server started on port 50052...")
    logger.info("Server started on port 50052.")
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()
