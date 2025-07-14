## 📋 프로젝트 기획서

### 1. 프로젝트명

**Smart Task Manager**

: 개인과 팀의 업무 효율성을 높이기 위한 데스크톱 기반 태스크 관리 애플리케이션

---

### 2. 프로젝트 개요

- **목표**: 직관적인 UI와 강력한 API 백엔드를 갖춘 스마트 태스크 관리 앱 구현
- **대상 사용자**: 개발자 및 소규모 팀

---

### 3. 주요 기능

### 3.1 사용자 인증

- 회원가입, 로그인, 로그아웃
- bcrypt 비밀번호 해싱, JWT 기반 인증 토큰 관리
- 자동 로그인, 사용자 정보 조회 기능

### 3.2 할일 관리 (CRUD)

- 생성: 제목, 설명, 카테고리, 우선순위, 마감일 입력
- 조회: 할일 목록, 상세정보
- 수정: 항목 수정, 완료 상태 토글
- 삭제: 할일 삭제

### 3.3 분류 및 우선순위

- 4가지 카테고리: 업무, 개인, 학습, 기타
- 3단계 우선순위: 높음(🔴), 보통(🟠), 낮음(🟢)
- 스마트 정렬: 우선순위 > 마감일 > 생성일

### 3.4 검색 및 필터링

- 제목 기반 실시간 검색
- 카테고리 및 완료 상태별 필터링 기능

### 3.5 통계 및 대시보드

- 전체/카테고리별 완료율 및 개수 표시
- 프로그래스 바로 시각화

---

### 4. 기술 스택

| 구분 | 사용 기술 (버전) | 주요 역할 / 특징 |
| --- | --- | --- |
| 프론트 | PyQt6 (v6.9.1) | 크로스-플랫폼 데스크톱 GUI 프레임워크 |
| API | FastAPI (v0.104.1) | 비동기 지원, 타이핑 기반의 현대적 Python 웹 프레임워크 |
| 자동화 | Playwright (v1.42.0) | 브라우저 자동화, E2E 테스트 및 크롤링 도구 |
| 컨테이너화 | Docker | 애플리케이션 컨테이너 빌드, 배포, 실행 환경 |
| DB 스키마 관리 | Flyway | 버전 기반 데이터베이스 마이그레이션 관리 |
| 데이터베이스 | MariaDB | 메인 관계형 데이터베이스 관리 시스템 |

## 5. 디렉토리 구조

---

```
├── README.md
├── .gitignore
├── docker-compose.yml               # Docker로 DB 실행용
│
├── backend/                         # FastAPI 백엔드
│   ├── main.py                     # 🚀 여기서 시작! FastAPI 앱
│   ├── database.py                 # DB 연결 코드
│   ├── models.py                   # 사용자, 할일 데이터 구조
│   ├── auth.py                     # 로그인 관련 함수들
│   ├── requirements.txt            # 필요한 라이브러리 목록
│   └── .env                        # DB 비밀번호 등 (git에 안올림)
│
├── frontend/                        # PyQt6 데스크톱 앱
│   ├── main.py                     # 🎯 앱 시작점
│   ├── login_window.py             # 로그인 창
│   ├── main_window.py              # 메인 창 (할일 목록)
│   ├── add_task_dialog.py          # 할일 추가 창
│   ├── api_client.py               # 백엔드와 통신하는 코드
│   └── requirements.txt            # PyQt6 등 필요한 것들
│
├── database/                        # 데이터베이스 파일들
│   ├── setup.sql                   # 테이블 만드는 SQL
│   └── sample_data.sql             # 테스트용 데이터
│
└── docs/                           # 나중에 문서 정리용
    └── api_test.md                 # API 테스트 방법 메모
```

## 6. 주요 화면 구성안

<p align="center">
  <img src="https://github.com/user-attachments/assets/8fca244c-88f9-4986-ab1d-21b93c275e70" width="400" alt="로그인" />
  <img src="https://github.com/user-attachments/assets/fd1a9699-4462-40a8-adb5-23c5adbc43f5" width="400" alt="회원가입" />
  <img src="https://github.com/user-attachments/assets/7c174262-5267-4a4d-a6b2-bfdbdfd06a2d" width="400" alt="메인화면1" />
  <img src="https://github.com/user-attachments/assets/ca055cff-3d20-4ab9-a5a2-56bee7eacc6e" width="400" alt="메인화면2" />
  <img src="https://github.com/user-attachments/assets/90ec6578-4da8-493d-b5cb-c4aaf6651d89" width="400" alt="통계화면" />
</p>

## 7. 기능별 사용자 흐름도
<img width="400" alt="스크린샷 2025-07-10 오후 4 47 03" src="https://github.com/user-attachments/assets/96e82eeb-f0f0-423c-815e-f1e977f6392d" />

## 8. Api 명세 초안
- [상세 명세 링크](https://confused-dietician-c17.notion.site/API-2257caa087bd80b1949de14394631552?source=copy_link)
### 인증 관련

```
POST   /api/auth/register      # 회원가입
POST   /api/auth/login         # 로그인
POST   /api/auth/logout        # 로그아웃
POST   /api/auth/withdraw      # 회원탈퇴
GET    /api/auth/me            # 내 정보 보기
```

### 할일 관리

```
GET    /api/todos               # 할일 목록 조회
POST   /api/todos               # 새 할일 생성
GET    /api/todos/{id}          # 특정 할일 조회
PUT    /api/todos/{id}          # 할일 수정
DELETE /api/todos/{id}          # 할일 삭제
PATCH  /api/todos/{id}/toggle   # 완료 상태 토글
```

## 9. ERD 및 SQL query
### ERD
<img width="799" height="248" alt="스크린샷 2025-07-12 오후 7 54 44" src="https://github.com/user-attachments/assets/5a346f4e-a56b-4d2a-a541-7fd5c280fa5b" />

### SQL query + Index
user
```
CREATE TABLE user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);
```

todo
```
CREATE TABLE todo (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    done TINYINT(1) DEFAULT 0,
    category ENUM('업무', '개인', '학습', '기타') DEFAULT '기타',
    priority ENUM('낮음', '보통', '높음') DEFAULT '보통',
    duedate DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
);
```

index
```
CREATE INDEX idx_todo_user_id ON todo(user_id);
CREATE INDEX idx_todo_duedate ON todo(duedate);
CREATE INDEX idx_todo_done ON todo(done);
CREATE INDEX idx_todo_user_priority ON todo(user_id, priority);
```
