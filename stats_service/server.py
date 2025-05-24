import grpc
from concurrent import futures
import stats_pb2
import stats_pb2_grpc
from datetime import datetime, timedelta

class StatsService(stats_pb2_grpc.StatsServiceServicer):
    def GetPostStats(self, request, context):
        return stats_pb2.GetPostStatsResponse(
            post_id=request.post_id,
            like_count=42,
            view_count=100,
            comment_count=7
        )

    def GetPostViewDynamics(self, request, context):
        today = datetime.utcnow().date()
        days = []
        for i in range(7):
            day = today - timedelta(days=6-i)
            days.append(stats_pb2.PostViewDay(date=day.isoformat(), view_count=10 + i * 3))
        return stats_pb2.GetPostViewDynamicsResponse(days=days)

    def GetPostLikeDynamics(self, request, context):
        today = datetime.utcnow().date()
        days = []
        for i in range(7):
            day = today - timedelta(days=6-i)
            days.append(stats_pb2.PostLikeDay(date=day.isoformat(), like_count=5 + i * 2))
        return stats_pb2.GetPostLikeDynamicsResponse(days=days)

    def GetPostCommentDynamics(self, request, context):
        today = datetime.utcnow().date()
        days = []
        for i in range(7):
            day = today - timedelta(days=6-i)
            days.append(stats_pb2.PostCommentDay(date=day.isoformat(), comment_count=2 + i))
        return stats_pb2.GetPostCommentDynamicsResponse(days=days)

    def GetTopPosts(self, request, context):
        posts = []
        for i in range(10):
            posts.append(stats_pb2.TopPost(post_id=100 + i, count=1000 - i * 50))
        return stats_pb2.GetTopPostsResponse(posts=posts)

    def GetTopUsers(self, request, context):
        users = []
        for i in range(10):
            users.append(stats_pb2.TopUser(user_id=200 + i, count=500 - i * 20))
        return stats_pb2.GetTopUsersResponse(users=users)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    stats_pb2_grpc.add_StatsServiceServicer_to_server(StatsService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print('StatsService gRPC server started on port 50051')
    server.wait_for_termination()

if __name__ == '__main__':
    serve() 