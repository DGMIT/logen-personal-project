from typing import Any
from unittest.mock import MagicMock

import bcrypt
import database as db  # get_current_user, get_db_connection이 정의된 곳
import schemas
import services.user_service as user_service
from fastapi import HTTPException, status
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
            db.select_user_by_email = origigianl_select_uesr_by_email
            db.get_db_connection = origigianl_get_db_func
            print("6단계: 원래 함수들로 복구 완료")


class TestRegisterService:
    def test_return_correct_user_id(self):
        def fake_get_db_connection():
            mock_conn = MagicMock()
            return mock_conn

        def fake_email_exist(email, cnx):
            if email == "ceh2000002@naver.com":
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="이미 존재하는 이메일입니다.",
                )
            return None

        def fake_create_user(email, password, name, cnx):
            return 2

        original_get_db_connection = db.get_db_connection
        original_email_exist = db.email_exist
        original_create_user = db.create_user

        db.get_db_connection = fake_get_db_connection
        db.email_exist = fake_email_exist
        db.create_user = fake_create_user

        test_email = "ceh2000002@naver.com"
        test_email_new = "ceh20002@naver.com"
        password = "1234"
        name = "logen"
        try:
            mock_cnx = db.get_db_connection()
            response = user_service.register_service(
                test_email_new, password, name, mock_cnx
            )
            assert response is not None
        except HTTPException as e:
            raise
        finally:
            db.get_db_connection = original_get_db_connection
            db.email_exist = original_email_exist
            db.create_user = original_create_user


def test_logout_api():
    reponse = client.post("/logout")
    assert reponse.status_code == 200


def test_withdraw_api():

    def fake_get_db_connection():
        mocc_con = MagicMock()
        return mocc_con

    def fake_get_current_user():
        return schemas.PublicUser(id=1, name="testuser", email="test@example.com")

    def fake_delete_user(user_id, cnx):
        return True

    app.dependency_overrides[db.get_db_connection] = fake_get_db_connection
    app.dependency_overrides[db.get_current_user] = fake_get_current_user

    original_delete_user = db.delete_user
    db.delete_user = fake_delete_user

    try:
        response = client.post("/withdraw")
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["success"] == True
        assert response_data["message"] == "회원탈퇴 성공"
    finally:
        app.dependency_overrides.clear()
        db.delete_user = original_delete_user
