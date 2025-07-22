import sys
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QMainWindow,
    QPushButton,
    QLabel,
    QVBoxLayout,
    QDialogButtonBox,
    QMessageBox,
    QWidget,
    QLineEdit,
    QFormLayout,
    QStackedWidget,
    QHBoxLayout,
    QFrame,
    QSizePolicy,
    QListWidget, QListWidgetItem, QMenu, QInputDialog, QTextEdit, QComboBox, QDateEdit, QCheckBox, QScrollArea
)
from PyQt6.QtCore import Qt, QPoint, QDate
from PyQt6.QtGui import QFont, QCursor, QColor
import api_client
from PyQt6.QtWidgets import QGraphicsDropShadowEffect

class LoginWidget(QWidget):
    def __init__(self, switch_to_main, switch_to_register):
        super().__init__()
        self.switch_to_main = switch_to_main
        self.switch_to_register = switch_to_register
        self.init_ui()

    def init_ui(self):
        # 전체 레이아웃(중앙 정렬)
        outer_layout = QVBoxLayout()
        outer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        outer_layout.setContentsMargins(0, 60, 0, 0)

        # 상단 카드(아이콘, 타이틀, 설명)
        card_top = QFrame()
        card_top.setObjectName("CardTop")
        card_top.setFixedWidth(420)
        card_top.setStyleSheet("""
            QFrame#CardTop {
                background: white;
                border-radius: 16px;
                padding: 32px 24px 24px 24px;
                border: 1px solid #f0f0f0;
            }
        """)
        vbox_top = QVBoxLayout()
        vbox_top.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon = QLabel("🔒")
        icon.setFont(QFont("Arial", 48))
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vbox_top.addWidget(icon)
        title = QLabel("로그인")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vbox_top.addWidget(title)
        desc = QLabel("Smart Task Manager에 오신 것을 환영합니다.")
        desc.setFont(QFont("Arial", 11))
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setStyleSheet("color: #888;")
        vbox_top.addWidget(desc)
        card_top.setLayout(vbox_top)
        outer_layout.addWidget(card_top)
        outer_layout.addSpacing(24)

        # 입력 카드(폼)
        card = QFrame()
        card.setObjectName("Card")
        card.setFixedWidth(420)
        card.setStyleSheet("""
            QFrame#Card {
                background: white;
                border-radius: 16px;
                padding: 32px 24px 24px 24px;
                border: 1px solid #f0f0f0;
            }
        """)
        vbox = QVBoxLayout()
        vbox.setSpacing(16)
        # 아이디
        id_label = QLabel("아이디 <span style='color:#e74c3c'>*</span>")
        id_label.setTextFormat(Qt.TextFormat.RichText)
        id_label.setFont(QFont("Arial", 11))
        self.email = QLineEdit()
        self.email.setPlaceholderText("example@naver.com")
        self.email.setFixedHeight(38)
        self.email.setFont(QFont("Arial", 11))
        vbox.addWidget(id_label)
        vbox.addWidget(self.email)
        # 비밀번호
        pw_label = QLabel("비밀번호 <span style='color:#e74c3c'>*</span>")
        pw_label.setTextFormat(Qt.TextFormat.RichText)
        pw_label.setFont(QFont("Arial", 11))
        self.password = QLineEdit()
        self.password.setPlaceholderText("password")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.setFixedHeight(38)
        self.password.setFont(QFont("Arial", 11))
        vbox.addWidget(pw_label)
        vbox.addWidget(self.password)
        # 로그인 버튼
        btn_login = QPushButton("로그인")
        btn_login.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_login.setFixedHeight(40)
        btn_login.setStyleSheet("""
            QPushButton {
                background: #2563eb;
                color: white;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #1d4ed8;
            }
        """)
        btn_login.clicked.connect(self.try_login)
        vbox.addWidget(btn_login)
        vbox.addSpacing(8)
        # 하단 회원가입 링크
        hbox = QHBoxLayout()
        hbox.addStretch(1)
        label_no_account = QLabel("계정이 없으신가요?")
        label_no_account.setFont(QFont("Arial", 10))
        hbox.addWidget(label_no_account)
        link_signup = QLabel("<a href='#' style='color:#2563eb;text-decoration:none;'>회원가입</a>")
        link_signup.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        link_signup.setTextFormat(Qt.TextFormat.RichText)
        link_signup.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        link_signup.linkActivated.connect(lambda _: self.switch_to_register())
        hbox.addWidget(link_signup)
        hbox.addStretch(1)
        vbox.addLayout(hbox)
        card.setLayout(vbox)
        outer_layout.addWidget(card)
        outer_layout.addStretch(1)
        self.setLayout(outer_layout)
        self.setStyleSheet("""
            QWidget {
                background: #f6f8fb;
            }
        """)

    def try_login(self):
        email = self.email.text().strip()
        password = self.password.text().strip()
        if not email or not password:
            QMessageBox.warning(self, "입력 오류", "이메일과 비밀번호를 모두 입력하세요.")
            return
        try:
            resp = api_client.login(email, password)
            if resp.get("success"):
                self.switch_to_main()
            else:
                msg = resp.get("message") or resp.get("detail") or "로그인 실패"
                if isinstance(msg, list):
                    msg = "\n".join(
                        item.get("msg", str(item)) for item in msg
                    )
                QMessageBox.warning(self, "로그인 실패", msg)
        except Exception as e:
            QMessageBox.critical(self, "오류", f"서버 오류: {e}")

# RegisterWidget도 동일 스타일로 리팩토링(생략 가능, 필요시 추가)
class RegisterWidget(QWidget):
    def __init__(self, switch_to_login):
        super().__init__()
        self.switch_to_login = switch_to_login
        self.init_ui()

    def init_ui(self):
        outer_layout = QVBoxLayout()
        outer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        outer_layout.setContentsMargins(0, 60, 0, 0)
        card_top = QFrame()
        card_top.setObjectName("CardTop")
        card_top.setFixedWidth(420)
        card_top.setStyleSheet("""
            QFrame#CardTop {
                background: white;
                border-radius: 16px;
                padding: 32px 24px 24px 24px;
                border: 1px solid #f0f0f0;
            }
        """)
        vbox_top = QVBoxLayout()
        vbox_top.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon = QLabel("📝")
        icon.setFont(QFont("Arial", 48))
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vbox_top.addWidget(icon)
        title = QLabel("회원가입")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vbox_top.addWidget(title)
        desc = QLabel("Smart Task Manager에 오신 것을 환영합니다.")
        desc.setFont(QFont("Arial", 11))
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setStyleSheet("color: #888;")
        vbox_top.addWidget(desc)
        card_top.setLayout(vbox_top)
        outer_layout.addWidget(card_top)
        outer_layout.addSpacing(24)
        card = QFrame()
        card.setObjectName("Card")
        card.setFixedWidth(420)
        card.setStyleSheet("""
            QFrame#Card {
                background: white;
                border-radius: 16px;
                padding: 32px 24px 24px 24px;
                border: 1px solid #f0f0f0;
            }
        """)
        vbox = QVBoxLayout()
        vbox.setSpacing(16)
        # 아이디
        id_label = QLabel("아이디 <span style='color:#e74c3c'>*</span>")
        id_label.setTextFormat(Qt.TextFormat.RichText)
        id_label.setFont(QFont("Arial", 11))
        self.email = QLineEdit()
        self.email.setPlaceholderText("example@naver.com")
        self.email.setFixedHeight(38)
        self.email.setFont(QFont("Arial", 11))
        vbox.addWidget(id_label)
        vbox.addWidget(self.email)
        # 비밀번호
        pw_label = QLabel("비밀번호 <span style='color:#e74c3c'>*</span>")
        pw_label.setTextFormat(Qt.TextFormat.RichText)
        pw_label.setFont(QFont("Arial", 11))
        self.password = QLineEdit()
        self.password.setPlaceholderText("password")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.setFixedHeight(38)
        self.password.setFont(QFont("Arial", 11))
        vbox.addWidget(pw_label)
        vbox.addWidget(self.password)
        # 이름
        name_label = QLabel("이름 <span style='color:#e74c3c'>*</span>")
        name_label.setTextFormat(Qt.TextFormat.RichText)
        name_label.setFont(QFont("Arial", 11))
        self.name = QLineEdit()
        self.name.setPlaceholderText("홍길동")
        self.name.setFixedHeight(38)
        self.name.setFont(QFont("Arial", 11))
        vbox.addWidget(name_label)
        vbox.addWidget(self.name)
        # 회원가입 버튼
        btn_register = QPushButton("회원가입")
        btn_register.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_register.setFixedHeight(40)
        btn_register.setStyleSheet("""
            QPushButton {
                background: #2563eb;
                color: white;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #1d4ed8;
            }
        """)
        btn_register.clicked.connect(self.try_register)
        vbox.addWidget(btn_register)
        vbox.addSpacing(8)
        # 하단 로그인 링크
        hbox = QHBoxLayout()
        hbox.addStretch(1)
        label_have_account = QLabel("이미 계정이 있으신가요?")
        label_have_account.setFont(QFont("Arial", 10))
        hbox.addWidget(label_have_account)
        link_login = QLabel("<a href='#' style='color:#2563eb;text-decoration:none;'>로그인</a>")
        link_login.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        link_login.setTextFormat(Qt.TextFormat.RichText)
        link_login.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        link_login.linkActivated.connect(lambda _: self.switch_to_login())
        hbox.addWidget(link_login)
        hbox.addStretch(1)
        vbox.addLayout(hbox)
        card.setLayout(vbox)
        outer_layout.addWidget(card)
        outer_layout.addStretch(1)
        self.setLayout(outer_layout)
        self.setStyleSheet("""
            QWidget {
                background: #f6f8fb;
            }
        """)

    def try_register(self):
        email = self.email.text().strip()
        password = self.password.text().strip()
        name = self.name.text().strip()
        if not email or not password or not name:
            QMessageBox.warning(self, "입력 오류", "모든 항목을 입력하세요.")
            return
        try:
            resp = api_client.register(email, password, name)
            if resp.get("success"):
                QMessageBox.information(self, "회원가입 성공", "회원가입이 완료되었습니다. 로그인 해주세요.")
                self.switch_to_login()
            else:
                msg = resp.get("message") or resp.get("detail") or "회원가입 실패"
                if isinstance(msg, list):
                    msg = "\n".join(
                        item.get("msg", str(item)) for item in msg
                    )
                QMessageBox.warning(self, "회원가입 실패", msg)
        except Exception as e:
            QMessageBox.critical(self, "오류", f"서버 오류: {e}")

class Badge(QLabel):
    def __init__(self, text, color):
        super().__init__(text)
        self.setStyleSheet(f"background: {color}; color: white; border-radius: 12px; padding: 3px 14px; font-size: 13px; font-weight: bold; margin-right: 4px;")
        self.setFont(QFont("Arial", 11, QFont.Weight.Bold))

class TodoItemWidget(QFrame):
    CATEGORY_COLORS = {
        "업무": "#2563eb",
        "개인": "#6366f1",
        "학습": "#06b6d4",
        "기타": "#64748b",
    }
    PRIORITY_COLORS = {
        "높음": "#ef4444",
        "보통": "#f59e42",
        "낮음": "#22c55e",
    }
    def __init__(self, todo, refresh_callback):
        super().__init__()
        self.todo = todo
        self.refresh_callback = refresh_callback
        self.setObjectName("TodoCard")
        self.setStyleSheet("""
            QFrame#TodoCard {
                background: #fff;
                border-radius: 18px;
                border: 1.5px solid #e5e7eb;
                padding: 20px 24px 14px 24px;
                margin-bottom: 0px; /* 카드 간 여백 제거 */
                font-family: 'Arial';
            }
            QFrame#TodoCard:hover {
                border: 1.5px solid #2563eb;
                background: #f3f6fd;
            }
        """)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(18)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 30))
        self.setGraphicsEffect(shadow)
        self.setMinimumHeight(80)
        self.setMaximumHeight(120)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(18)
        # 체크박스
        self.checkbox = QCheckBox()
        self.checkbox.setChecked(todo.get("done", False))
        self.checkbox.stateChanged.connect(self.toggle_done)
        self.checkbox.setStyleSheet("QCheckBox {margin-right: 10px;}")
        main_layout.addWidget(self.checkbox, alignment=Qt.AlignmentFlag.AlignTop)
        # 중앙 정보
        info_layout = QVBoxLayout()
        info_layout.setSpacing(6)
        # 제목
        title = QLabel(f"{todo.get('title')}")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 2px;")
        info_layout.addWidget(title)
        # 메타정보(카테고리, 우선순위, 마감)
        meta_layout = QHBoxLayout()
        meta_layout.setSpacing(10)
        cat = todo.get('category', '기타')
        cat_badge = Badge(cat, self.CATEGORY_COLORS.get(cat, "#64748b"))
        meta_layout.addWidget(cat_badge)
        prio = todo.get('priority', '보통')
        prio_badge = Badge(prio, self.PRIORITY_COLORS.get(prio, "#f59e42"))
        meta_layout.addWidget(prio_badge)
        duedate = todo.get('duedate', '')
        date_label = QLabel(f"🗓 {duedate}")
        date_label.setStyleSheet("color: #64748b; font-size: 13px; font-weight: bold; margin-left: 8px;")
        meta_layout.addWidget(date_label)
        meta_layout.addStretch(1)
        info_layout.addLayout(meta_layout)
        main_layout.addLayout(info_layout, stretch=1)
        self.setLayout(main_layout)
        # 하단 버튼 영역(초기에는 숨김)
        self.button_bar = QWidget()
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(12)
        self.btn_edit = QPushButton("수정")
        self.btn_edit.setStyleSheet("background:#2563eb;color:white;border-radius:8px;padding:8px 28px;font-weight:bold;font-size:15px;")
        self.btn_edit.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.btn_edit.clicked.connect(self.edit_todo)
        self.btn_delete = QPushButton("삭제")
        self.btn_delete.setStyleSheet("background:#ef4444;color:white;border-radius:8px;padding:8px 28px;font-weight:bold;font-size:15px;")
        self.btn_delete.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.btn_delete.clicked.connect(self.delete_todo)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addStretch(1)
        self.button_bar.setLayout(btn_layout)
        self.button_bar.setVisible(False)
        out_layout = QVBoxLayout(self)
        out_layout.setContentsMargins(0, 0, 0, 0)
        out_layout.setSpacing(0)
        out_layout.addLayout(main_layout)
        out_layout.addWidget(self.button_bar)
        self.setLayout(out_layout)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
    def toggle_done(self, state):
        api_client.update_todo(self.todo['id'], done=bool(state))
        self.refresh_callback()
    def toggle_done_btn(self):
        self.checkbox.setChecked(not self.checkbox.isChecked())
    def show_context_menu(self, pos: QPoint):
        self.button_bar.setVisible(True)
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.button_bar.setVisible(False)
        super().mousePressEvent(event)
    def edit_todo(self):
        new_title, ok = QInputDialog.getText(self, "할일 수정", "새 제목:", text=self.todo.get('title', ''))
        if ok and new_title.strip():
            api_client.update_todo(self.todo['id'], title=new_title.strip())
            self.refresh_callback()
    def delete_todo(self):
        api_client.delete_todo(self.todo['id'])
        self.refresh_callback()

class TodoListWidget(QWidget):
    def __init__(self):
        super().__init__()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea {border: none; background: #f8fafc;} QScrollBar:vertical {width: 12px; background: #e5e7eb; border-radius: 6px;} QScrollBar::handle:vertical {background: #2563eb; border-radius: 6px;}")
        content = QWidget()
        self.layout = QVBoxLayout(content)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)  # 카드 간 여백 제거
        scroll.setWidget(content)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)  # 스크롤 영역 여백 제거
        main_layout.setSpacing(0)
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)
        self.refresh()
    def refresh(self):
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        resp = api_client.list_todos(limit=100)
        todos = resp.get('data', {}).get('todos', []) if resp.get('success') else []
        for todo in todos:
            item = TodoItemWidget(todo, self.refresh)
            self.layout.addWidget(item)
        self.layout.addStretch(1)

class TodoSidebar(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        # 예시 타이틀
        title = QLabel("사이드바")
        title.setStyleSheet("font-weight: bold; font-size: 18px;")
        layout.addWidget(title)
        layout.addStretch(1)
        self.setLayout(layout)
        self.setFixedWidth(320)
        self.setStyleSheet("background: #f8fafc; border-radius: 8px;")

class TodoMainFrame(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        title = QLabel("할일 목록")
        title.setStyleSheet("font-weight: bold; font-size: 18px;")
        layout.addWidget(title)
        self.todo_list = TodoListWidget()
        layout.addWidget(self.todo_list)
        self.setLayout(layout)
        self.setStyleSheet("background: #fff; border-radius: 8px;")

# 전체 배경 QSS
class TodoMainPage(QWidget):
    def __init__(self):
        super().__init__()
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(16)
        self.sidebar = TodoSidebar()
        self.main_frame = TodoMainFrame()
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.main_frame, stretch=1)
        self.setLayout(main_layout)
        self.setStyleSheet("background: #f6f8fb;")

# MainWindow의 _main_content_widget을 TodoMainPage로 교체
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("로그인/회원가입 예제")
        self.stack = QStackedWidget()
        self.login_widget = LoginWidget(self.show_main, self.show_register)
        self.register_widget = RegisterWidget(self.show_login)
        self.main_widget = self._main_content_widget()
        self.stack.addWidget(self.login_widget)      # index 0
        self.stack.addWidget(self.register_widget)   # index 1
        self.stack.addWidget(self.main_widget)       # index 2
        self.setCentralWidget(self.stack)
        self.resize(1200, 800)
        self.show_login()

    def show_login(self):
        self.stack.setCurrentIndex(0)

    def show_register(self):
        self.stack.setCurrentIndex(1)

    def show_main(self):
        self.stack.setCurrentIndex(2)

    def _main_content_widget(self):
        return TodoMainPage()

    def logout(self):
        api_client.logout()
        self.show_login()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
