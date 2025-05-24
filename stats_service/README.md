# Stats Service

### Get statistics for a post

```
curl -X GET "http://localhost:8080/posts/1/stats" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VybmFtZTciLCJ1c2VyX2lkIjoyLCJleHAiOjE3NDgxMDY2MTB9.xz6oQkSVy7XtK1pIJpE4F7CjyJFmktQBpYz28RY26Zo"
```

### Get view dynamics for a post (views per day)

```
curl -X GET "http://localhost:8080/posts/1/view_dynamics" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VybmFtZTciLCJ1c2VyX2lkIjoyLCJleHAiOjE3NDgxMDY2MTB9.xz6oQkSVy7XtK1pIJpE4F7CjyJFmktQBpYz28RY26Zo"
```

### Get like dynamics for a post (likes per day)

```
curl -X GET "http://localhost:8080/posts/1/like_dynamics" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VybmFtZTciLCJ1c2VyX2lkIjoyLCJleHAiOjE3NDgxMDY2MTB9.xz6oQkSVy7XtK1pIJpE4F7CjyJFmktQBpYz28RY26Zo"
```

### Get comment dynamics for a post (comments per day)

```
curl -X GET "http://localhost:8080/posts/1/comment_dynamics" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VybmFtZTciLCJ1c2VyX2lkIjoyLCJleHAiOjE3NDgxMDY2MTB9.xz6oQkSVy7XtK1pIJpE4F7CjyJFmktQBpYz28RY26Zo"
```

### Get top 10 posts by likes, comments, or views

```
curl -X GET "http://localhost:8080/posts/top?metric=like" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VybmFtZTciLCJ1c2VyX2lkIjoyLCJleHAiOjE3NDgxMDY2MTB9.xz6oQkSVy7XtK1pIJpE4F7CjyJFmktQBpYz28RY26Zo"
```

### Get top 10 users by likes, comments, or views

```
curl -X GET "http://localhost:8080/users/top?metric=like" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VybmFtZTciLCJ1c2VyX2lkIjoyLCJleHAiOjE3NDgxMDY2MTB9.xz6oQkSVy7XtK1pIJpE4F7CjyJFmktQBpYz28RY26Zo"
```
