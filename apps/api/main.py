import database as db
import schemas
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBearer
from mysql.connector.connection import MySQLConnection
from utils import create_access_token

app = FastAPI()


security = HTTPBearer()


@app.post(
    "/login",
    response_model=schemas.LoginResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": schemas.ErrorResponse, "description": "입력값 오류"},
        401: {"model": schemas.ErrorResponse, "description": "비밀번호 불일치"},
        404: {"model": schemas.ErrorResponse, "description": "존재하지 않는 이메일"},
        500: {"model": schemas.ErrorResponse, "description": "DB 연결 실패"},
    },
)
def login(
    request: schemas.LoginRequest, cnx: MySQLConnection = Depends(db.get_db_connection)
):
    try:
        email = request.email
        password = request.password
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="이메일을 입력해주세요."
            )
        if not password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="비밀번호를 입력해주세요",
            )
        user = db.select_user_by_email_and_password(email, password, cnx)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 유저입니다.",
            )
        user_id, user_name, user_email = user
        return schemas.LoginResponse(
            success=True,
            message="로그인에 성공하셨습니다.",
            data=schemas.LoginData(
                token=create_access_token(
                    data={"sub": str(user_id), "email": user_email}
                ),
                user=schemas.PublicUser(id=user_id, email=user_email, name=user_name),
            ),
        )
    except HTTPException:
        raise
    except Exception as error:
        print("Login Unexpected error:", error)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="서버 오류로 로그인에 실패하였습니다.",
        )


@app.post(
    "/register",
    response_model=schemas.RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": schemas.ErrorResponse, "description": "입력값 오류"},
        409: {"model": schemas.ErrorResponse, "description": "이미 존재하는 이메일"},
        500: {"model": schemas.ErrorResponse, "description": "DB 연결 실패"},
    },
)
def register(
    request: schemas.RegisterRequest,
    cnx: MySQLConnection = Depends(db.get_db_connection),
):
    try:
        email = request.email
        password = request.password
        name = request.name
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="이메일을 입력해주세요."
            )
        if not password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="비밀번호를 입력해주세요",
            )
        if not name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="이름을 입력해주세요"
            )
        user_id = db.insert_user(email, password, name, cnx)
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="이미 존재하는 이메일입니다.",
            )

        return schemas.RegisterResponse(
            success=True,
            message="회원가입에 성공하셨습니다.",
            data=schemas.PublicUser(id=user_id, email=email, name=name),
        )
    except HTTPException:
        raise
    except Exception as err:
        # 내부 로그만 출력하고 사용자에겐 일반 메시지
        print("Register Unexpected error:", err)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="서버 오류로 회원가입에 실패했습니다.",
        )


@app.post(
    "/logout",
    response_model=schemas.LogoutResponse,
    status_code=status.HTTP_200_OK,
    responses={
        500: {"model": schemas.ErrorResponse, "description": "DB 연결 실패"},
    },
)
def logout():
    try:
        return schemas.LogoutResponse(success=True, message="로그아웃 성공")
    except HTTPException:
        raise
    except Exception as error:
        print("서버 오류로 로그아웃에 실패하였습니다.", error)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="서버 오류로 회원탈퇴에 실패하였싑니다.",
        )


@app.post(
    "/withdraw",
    response_model=schemas.WithdrawResponse,
    status_code=status.HTTP_200_OK,
    responses={
        500: {"model": schemas.ErrorResponse, "description": "DB 연결 실패"},
    },
)
def withdraw(
    current_user: schemas.PublicUser = Depends(db.get_current_user),
    cnx: MySQLConnection = Depends(db.get_db_connection),
):
    try:
        db.delete_user(current_user.id, cnx)
        return schemas.WithdrawResponse(success=True, message="회원탈퇴 성공")
    except HTTPException:
        raise
    except Exception as error:
        print("withdraw Unexpected error:", error)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="서버 오류로 회원탈퇴에 실패하였습니다.",
        )


@app.get(
    "/user",
    response_model=schemas.MeResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": schemas.ErrorResponse, "description": "인증 필요"},
        500: {"model": schemas.ErrorResponse, "description": "DB 연결 실패"},
    },
)
def info_me(current_user: schemas.PublicUser = Depends(db.get_current_user)):
    try:
        return schemas.MeResponse(
            success=True, message="유저 본인정보 조회 성공", data=current_user
        )
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"서버 오류로 유저 정보 조회에 실패하였습니다. {err}",
        )
