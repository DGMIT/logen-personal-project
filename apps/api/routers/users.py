import database as db
import schemas
import services.user_service as user_service
from fastapi import APIRouter, Depends, HTTPException, status
from mysql.connector.connection import MySQLConnection
from sqlalchemy.orm import Session
from utils import create_access_token

router = APIRouter(
    responses={
        401: {"description": "유효하지 않은 토큰입니다. 다시 로그인해 주세요."},
        500: {"description": "DB 연결 실패"},
    },
)


@router.post(
    "/login",
    response_model=schemas.LoginResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": schemas.ErrorResponse, "description": "입력값 오류"},
        401: {"model": schemas.ErrorResponse, "description": "비밀번호 불일치"},
        404: {"model": schemas.ErrorResponse, "description": "존재하지 않는 이메일"},
    },
)
def login(request: schemas.LoginRequest, session: Session = Depends(db.get_db)):
    try:
        email = request.email
        password = request.password
        user = user_service.login_service(email, password, session)
        return schemas.LoginResponse(
            success=True,
            message="로그인에 성공하셨습니다.",
            data=schemas.LoginData(
                token=create_access_token(
                    data={"sub": str(user.id), "email": user.email}
                ),
                user=schemas.PublicUser(id=user.id, email=user.email, name=user.name),
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


@router.post(
    "/register",
    response_model=schemas.RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": schemas.ErrorResponse, "description": "입력값 오류"},
        409: {"model": schemas.ErrorResponse, "description": "이미 존재하는 이메일"},
    },
)
def register(
    request: schemas.RegisterRequest,
    session: Session = Depends(db.get_db),
):
    try:
        email = request.email
        password = request.password
        name = request.name
        user_id = user_service.register_service(email, password, name, session)
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


@router.post(
    "/logout", response_model=schemas.LogoutResponse, status_code=status.HTTP_200_OK
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


@router.post(
    "/withdraw", response_model=schemas.WithdrawResponse, status_code=status.HTTP_200_OK
)
def withdraw(
    current_user: schemas.PublicUser = Depends(db.get_current_user),
    session: Session = Depends(db.get_db),
):
    try:
        db.delete_user(current_user.id, session)
        return schemas.WithdrawResponse(success=True, message="회원탈퇴 성공")
    except HTTPException:
        raise
    except Exception as error:
        print("withdraw Unexpected error:", error)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="서버 오류로 회원탈퇴에 실패하였습니다.",
        )


@router.get(
    "/user",
    response_model=schemas.MeResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": schemas.ErrorResponse, "description": "인증 필요"},
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
