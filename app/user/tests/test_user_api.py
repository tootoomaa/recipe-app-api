from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient    # API를 테스트 할수 있는 client
from rest_framework import status            # 읽기 쉽게 지원해줌

CREATE_USER_URL = reverse('user:create')    # URL 생성
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')

# helper functions
def create_user(**params):                   # 다수의 파라미터 전달 가능
    return get_user_model().objects.create_user(**params)

# Public의 뜻은 인증 절차 없다는 의미
class PublicUserApiTests(TestCase):
    """Test the user api (pulbic)"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valide_user_success(self):
        """Test createing user with payload is successful"""
        payload = {
            'email': 'tootoomaa@naver.com',
            'password': 'testpass',
            'name': 'Test name'
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))   # 암호 검증
        self.assertNotIn('password', res.data)                      # 암호화 체크

    def test_user_exists(self):
        """Test creating a user that already exists fails"""
        payload = {'email': 'tootoomaa@naver.com', 'password': 'testpass'}
        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that the password must be more than 5 chracters"""
        payload = {
            'email': 'tootoomaa@naver.com',
            'password': 'pw',
            'name': 'Test',
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test that a token is created for the user"""
        payload = {'email': 'tootoomaa@naver.com', 'password': 'testpass'}
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data) # token 포함 여부
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """Test that token is not created if invalid credentials are given"""
        create_user(email='tootoomaa@naver.com', password="testpass")
        payload = {'email': 'tootoomaa@naver.com', 'password': 'wrong'}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('toekn', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """Test that token is not create if user doesn't exist"""
        # create_user를 하지 않았음으로 사용자가 존제하지 않게됨
        payload = {'email': 'tootoomaa@naver.com', 'password': 'testpass'}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """Test that email and password are required"""
        res = self.client.post(TOKEN_URL, {'email': 'one', 'password': ''})

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """Test that authentication is required for users"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test API request that require authentication"""

    def setUp(self):
        self.user = create_user(
            email = 'tootoomaa@naver.com',
            password = 'testpass',
            name='name'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user) # 강제 사용자 인증

    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in used"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email
        })

    def test_post_not_allowed(self):
        """Test that POST is not allowed on the me url"""
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating the user profile for authentication user"""
        # 테스트 중이라서 setup에서 설정한 기존 사용자의 정보와 다르다
        payload = {'name': 'new name', 'password': 'newpassword123'}

        res = self.client.patch(ME_URL, payload)
        # DB를 최신 사용자 정보로 업데이트 한다.
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
