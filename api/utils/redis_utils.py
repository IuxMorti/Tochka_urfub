import uuid


class RedisKeys:

    @staticmethod
    def video_views(video_id: uuid.UUID) -> str:
        return f"video_{video_id}_views"

    @staticmethod
    def video_likes(video_id: uuid.UUID) -> str:
        return f"video_{video_id}_likes"

    @staticmethod
    def video_dislike(video_id: uuid.UUID) -> str:
        return f"video_{video_id}_dislike"

    @staticmethod
    def user_views(user_id: uuid.UUID) -> str:
        return f"user_{user_id}_views"

    @staticmethod
    def user_likes(user_id: uuid.UUID) -> str:
        return f"user_{user_id}_likes"

    @staticmethod
    def comment_likes(comment_id: uuid.UUID) -> str:
        return f"comment_{comment_id}_like"

    @staticmethod
    def comment_dislikes(comment_id: uuid.UUID) -> str:
        return f"comment_{comment_id}_dislike"