from urllib.parse import parse_qs
from channels.middleware import BaseMiddleware
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.models import AnonymousUser
from accounts.models import CustomUser

class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        query_string = scope.get("query_string", b"").decode()
        query_params = parse_qs(query_string)
        token = query_params.get("token", [None])[0]

        if token:
            try:
                access_token = AccessToken(token)
                user_id = access_token["user_id"]
                user = await CustomUser.objects.aget(id=user_id)
                scope["user"] = user
                print(f"[JWTAuth] Authenticated user: {getattr(user, 'username', None)}")
            except Exception as e:
                print(f"[JWTAuth] Token invalid or user not found: {e}")
                scope["user"] = AnonymousUser()
        else:
            print("[JWTAuth] No token provided.")
            scope["user"] = AnonymousUser()

        return await super().__call__(scope, receive, send)
