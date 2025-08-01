from typing import Any
from unittest.mock import MagicMock

import bcrypt
import database as db  # get_current_user, get_db_connection이 정의된 곳
import schemas
import services.user_service as user_service
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestLoginService:
    test_correct_form_email = "ceh20002@naver.com"
    test_correct_form_password = "1234"

    def test_return_correct_token(self):
        test_password = "1234"
        hashed_password = bcrypt.hashpw(test_password.encode("utf-8"), bcrypt.gensalt())

        def fake_get_db_connection():
            mocc_con = MagicMock()
            return mocc_con

        def fake_get_select_user_by_email(email: str, cnx):
            if email == "ceh20002@naver.com":
                return schemas.UserInDB(
                    **{
                        "id": 1,
                        "name": "logen",
                        "email": "ceh20002@naver.com",
                        "password": hashed_password.decode("utf-8"),
                    }
                )

        origigianl_get_db_func = db.get_db_connection
        origigianl_select_uesr_by_email = db.select_user_by_email

        db.get_db_connection = fake_get_db_connection
        db.select_user_by_email = fake_get_select_user_by_email

        try:
            # 4단계: 이제 테스트 실행
            print("4단계: 테스트 실행 시작")
            result = user_service.login_service(
                self.test_correct_form_email, self.test_correct_form_password
            )
            print(f"4단계: 테스트 결과 = {result}")

            # 5단계: 결과 확인
            assert result is not None, "로그인 서비스가 None을 반환했습니다"
            print("5단계: 테스트 성공!")

        finally:
            # 6단계: 꼭!! 원래 함수들로 되돌리기 (다른 테스트에 영향 안 주려고)
            db.select_user_by_email = origigianl_get_db_func
            db.get_db_connection = origigianl_select_uesr_by_email
            print("6단계: 원래 함수들로 복구 완료")
