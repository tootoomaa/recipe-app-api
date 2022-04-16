from unittest.mock import patch                     # 장고의 데이터베이스 데이터를 가져오는데 Mock수행
from django.core.management import call_command     # Command 기능 추가
from django.db.utils import OperationalError        # 장고가 발생하는 에러 임포
from django.test import TestCase

class CommandTests(TestCase):

    def test_wait_for_db_ready(self):
        """Test waiting for db when do is available"""
        # ConnectionHandler를 오버라이드 하여 Mock과 같이 동작하도록 만든다.
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            gi.return_value = True                  # 리턴 값을 덮어 씌움
            call_command('wait_for_db')             #
            self.assertEqual(gi.call_count, 1)      #

    # 5번 까지는 실패, 6번 부터는 정상 실행 확인
    @patch('time.sleep', return_value=True)         # 테스트 실행 시간을 줄이고자 함
    def test_wait_for_db(self, ts):                 # 전달 인자로 ts 전달
        """Test waiting for db"""
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            gi.side_effect = [OperationalError] * 5 + [True]
            call_command('wait_for_db')
            self.assertEqual(gi.call_count, 6)
