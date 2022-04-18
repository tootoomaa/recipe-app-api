from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient    # API를 테스트 할수 있는 client
from rest_framework import status            # 읽기 쉽게 지원해줌

CREATE_USER_URL = reverse('user:create')    # URL 생성
TOKEN_URL = reverse('user:token')

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
