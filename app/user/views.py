from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from user.serializers import UserSerializer, AuthTokenSerializer

class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system"""
    serializer_class = UserSerializer

class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user"""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user"""
    serializer_class = UserSerializer
    # 인증을 위한 추가적인 클레스 2개
    authentication_classes = (authentication.TokenAuthentication,) # 쿠키, 토큰
    permission_classes = (permissions.IsAuthenticated,)

    # 로그인한 사용자의 모델 검색
    def get_object(self):
        """Retrieve and return authentication user"""
        return self.request.user
