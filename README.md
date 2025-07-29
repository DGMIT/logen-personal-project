물론입니다! 아래는 현재 내용을 구조적으로 정리하고 표현을 매끄럽게 다듬은 버전입니다. 핵심은 **가독성 향상**, **중복 제거**, **표현 통일**입니다:

---

## 📋 프로젝트 개요

### 1. 프로젝트명

**Smart Task Manager**
: 개인과 팀의 업무 효율성을 높이기 위한 데스크톱 기반 태스크 관리 애플리케이션

---

### 2. 개요 및 목표

* **목표**: 직관적인 UI와 강력한 API 백엔드를 갖춘 스마트 태스크 관리 앱 구현
* **대상 사용자**: 개발자 및 소규모 팀

---

### 3. 주요 기능

#### 사용자 인증

* 회원가입, 로그인, 로그아웃
* bcrypt 비밀번호 해싱, JWT 기반 인증 토큰 발급 및 관리

#### 할일 관리 (CRUD)

* **생성**: 제목, 설명, 카테고리, 우선순위, 마감일 입력
* **조회**: 전체 목록 및 상세 정보
* **수정**: 항목 수정 및 완료 상태 토글
* **삭제**: 할일 삭제

#### 분류 및 우선순위

* 카테고리: 업무, 개인, 학습, 기타
* 우선순위: 높음 🔴 / 보통 🟠 / 낮음 🟢
* 우선순위 기준 자동 정렬

#### 검색 및 필터링

* 제목 기반 실시간 검색
* 카테고리 및 완료 상태별 필터 기능

#### 통계 및 대시보드

* 전체 및 카테고리별 완료율/개수
* 프로그래스 바 시각화 제공

---

### 4. 기술 스택

| 구분    | 사용 기술              | 설명                       |
| ----- | ------------------ | ------------------------ |
| 프론트엔드 | PyQt6 (v6.9.1)     | 크로스 플랫폼 데스크톱 GUI         |
| 백엔드   | FastAPI (v0.104.1) | 현대적 비동기 Python API 프레임워크 |
| DB    | MariaDB            | 관계형 데이터베이스               |
| 인프라   | Docker             | 컨테이너 기반 환경 구성 및 배포       |

---

### 5. 디렉토리 구조

```
├── README.md
│
├── apps/
│   ├── api/                             # 백엔드 (FastAPI)
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   ├── schemas.py
│   │   └── utils.py
│   │
│   ├── desktop/                         # 프론트엔드 (PyQt6)
│   │   ├── api_client.py
│   │   ├── app_image.png
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   └── smarttaskmanager.spec
│   │
│   └── infra/                           # 인프라 (Docker, SQL)
│       ├── docker-compose.yml
│       └── init_db.sql
```

---

### 6. 주요 화면 구성

<p align="center">
  <img src="https://github.com/user-attachments/assets/8fca244c-88f9-4986-ab1d-21b93c275e70" width="400" />
  <img src="https://github.com/user-attachments/assets/fd1a9699-4462-40a8-adb5-23c5adbc43f5" width="400" />
  <img src="https://github.com/user-attachments/assets/7c174262-5267-4a4d-a6b2-bfdbdfd06a2d" width="400" />
  <img src="https://github.com/user-attachments/assets/ca055cff-3d20-4ab9-a5a2-56bee7eacc6e" width="400" />
  <img src="https://github.com/user-attachments/assets/90ec6578-4da8-493d-b5cb-c4aaf6651d89" width="400" />
</p>

---

### 7. 기능별 사용자 흐름도

<img width="400" alt="사용자 흐름도" src="https://github.com/user-attachments/assets/96e82eeb-f0f0-423c-815e-f1e977f6392d" />

---

### 8. API 명세

[📄 상세 명세 보기](https://confused-dietician-c17.notion.site/API-2257caa087bd80b1949de14394631552?source=copy_link)

#### 🔐 인증

```
POST   /api/register
POST   /api/login
POST   /api/logout
POST   /api/withdraw
GET    /api/me
```

#### 📋 할일 관리

```
GET    /api/todos
POST   /api/todos
GET    /api/todos/{id}
PUT    /api/todos/{id}
DELETE /api/todos/{id}
PATCH  /api/todos/{id}/toggle
```

---

### 9. 데이터베이스 구조 및 쿼리

#### ERD

<img width="799" height="248" alt="ERD" src="https://github.com/user-attachments/assets/5a346f4e-a56b-4d2a-a541-7fd5c280fa5b" />

#### SQL + Index

```sql
CREATE DATABASE IF NOT EXISTS todo_app;
USE todo_app;

CREATE TABLE IF NOT EXISTS usr (
    usr_id INT AUTO_INCREMENT PRIMARY KEY,
    usr_nm VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    pwd VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS todo (
    todo_id INT AUTO_INCREMENT PRIMARY KEY,
    todo_title VARCHAR(100) NOT NULL,
    todo_dtl TEXT,
    yn_done TINYINT(1) DEFAULT 0,
    ctgy ENUM('업무', '개인', '학습', '기타') DEFAULT '기타',
    priority_lvl ENUM('낮음', '보통', '높음') DEFAULT '보통',
    due_dt DATE NOT NULL,
    created_dt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usr_id INT NOT NULL,
    FOREIGN KEY (usr_id) REFERENCES usr(usr_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_todo_usr_id ON todo(usr_id);
CREATE INDEX IF NOT EXISTS idx_todo_due_dt ON todo(due_dt);
CREATE INDEX IF NOT EXISTS idx_todo_yn_done ON todo(yn_done);
CREATE INDEX IF NOT EXISTS idx_todo_usr_priority_lvl ON todo(usr_id, priority_lvl);
```

---

### 10. 실행 방법

#### 🐳 백엔드 실행

1. `.env` 파일 생성 (`apps/api` 내부):

```
DB_HOST=127.0.0.1
DB_USER=root
DB_PASSWORD=1234
DB_NAME=todo_app
JWT_SECRET_KEY=your_secret_key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
```

2. MariaDB 초기화 및 실행:

```bash
cd apps/infra
docker-compose down -v
docker-compose up -d
```

3. 가상환경 및 라이브러리 설치:

```bash
cd ../api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

4. FastAPI 서버 실행:

```bash
uvicorn main:app --reload
```

#### 🖥️ 프론트엔드 실행

1. 가상환경 및 라이브러리 설치:

```bash
cd apps/desktop
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. 실행:

```bash
python main.py
```

---

### 프론트엔드 실행파일 생성 방법
프론트엔드 루트 경로로 이동합니다.

```bash
pyinstaller --noconfirm --noconsole --onefile main.py --name smarttaskmanager
```
- 만약 icon을 추가하고싶다면 현재 디렉토리 기준 아래와같이 작성하면 됩니다.
```bash
pyinstaller --noconfirm --noconsole --onefile --name smarttaskmanager --icon=./app_image.png main.py
```

* `--noconsole`: GUI 앱이라 콘솔 창이 뜨지 않도록
* `--onefile`: 모든 코드를 하나의 실행파일로 묶음
* `--name`: 실행파일 이름 지정

### 결과 및 실행

* `dist/` 폴더 안에 `smarttaskmanager.exe`(Windows) 또는 `smarttaskmanager.app`(macOS)이 생성됩니다.
* 더블클릭 또는 커맨드라인에서 실행 가능합니다.
  * ${경로}/dist/smarttaskmanager 로 터미널에서도 실행이 가능합니다.
  * open ${경로}/dist/smarttaskmanager.app 로 터미널에서도 실행이 가능합니다.
  * smarttaskmanager 또는 smarttaskmanager.exe 또는 smarttaskmanager.app 파일을 더블 클릭으로 실행 가능합니다.
* macOS `.app`은 압축하지 않고 공유하면 손상되니, 반드시 `.zip`으로 압축 후 전달해야 합니다.
