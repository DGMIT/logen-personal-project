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
    QFrame,
    QLineEdit,
    QFormLayout,
    QStackedWidget,
    QHBoxLayout,
    QFrame,
    QSizePolicy,
    QListWidget, QListWidgetItem, QMenu, QInputDialog, QTextEdit, QComboBox, QDateEdit, QCheckBox, QScrollArea, QButtonGroup, QProgressBar
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

    def clear_fields(self):
        if hasattr(self, 'email') and self.email:
            self.email.setText("")
        if hasattr(self, 'password') and self.password:
            self.password.setText("")

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

    def clear_fields(self):
        if hasattr(self, 'email') and self.email:
            self.email.setText("")
        if hasattr(self, 'password') and self.password:
            self.password.setText("")
        if hasattr(self, 'name') and self.name:
            self.name.setText("")

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
                border: 1.5px solid black;
                background: #f3f6fd;
                color: black;
            }
        """)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(18)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 30))
        self.setGraphicsEffect(shadow)
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
        # Remove button_bar and related logic
        # self.button_bar = QWidget() ...
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
    def toggle_done(self, state):
        # API 응답이 완료된 후에만 새로고침 (동기라면 바로, 비동기라면 QTimer로 약간 딜레이)
        api_client.update_todo(self.todo['id'], done=bool(state))
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(150, self.refresh_callback)  # 150ms 후 새로고침
    def toggle_done_btn(self):
        self.checkbox.setChecked(not self.checkbox.isChecked())
    def show_context_menu(self, pos: QPoint):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: white;
                color: black; /* 기본 텍스트 색 */
            }
            QMenu::item:selected {
                background-color: #0078d7;
                color: white; /* 선택된 항목 텍스트 색 */
            }
            QMenu::item:hover {
                background-color: #e0e0e0;
                color: black; /* 호버 시 텍스트 색 */
            }
        """)
        edit_action = menu.addAction("수정")
        delete_action = menu.addAction("삭제")
        action = menu.exec(self.mapToGlobal(pos))
        if action == edit_action:
            self.edit_todo_custom()
        elif action == delete_action:
            self.delete_todo()
    def mousePressEvent(self, event):
        super().mousePressEvent(event)
    def edit_todo(self):
        new_title, ok = QInputDialog.getText(self, "할일 수정", "새 제목:", text=self.todo.get('title', ''))
        if ok and new_title.strip():
            api_client.update_todo(self.todo['id'], title=new_title.strip())
            self.refresh_callback()
    def delete_todo(self):
        api_client.delete_todo(self.todo['id'])
        self.refresh_callback()

    def edit_todo_custom(self):
        # 부모 계층에서 TodoMainPage를 찾아 set_edit_mode 호출
        parent = self.parent()
        while parent is not None:
            if isinstance(parent, TodoMainPage):
                parent.set_edit_mode(self.todo)
                break
            parent = parent.parent()

class TodoListWidget(QWidget):
    def __init__(self, stats_callback=None):
        super().__init__()
        self.stats_callback = stats_callback
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
        self._filter = "all"
        self._search = ""
        self.refresh()

    def set_filter(self, filter_key, search_term=""):
        self._filter = filter_key
        self._search = search_term
        self.refresh()

    def refresh(self):
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        # 필터링 로직
        params = {"limit": 100}
        if self._filter == "done":
            params["done"] = True
        elif self._filter == "not_done":
            params["done"] = False
        elif self._filter in ("업무", "개인", "학습","기타"):
            params["category"] = self._filter
        if self._search:
            params["search"] = self._search
        resp = api_client.list_todos(**params)
        todos = resp.get('data', {}).get('todos', []) if resp.get('success') else []
        priority_order = {"높음": 1, "보통": 2, "낮음": 3}

        sorted_todos = sorted(todos, key=lambda x: priority_order[x["priority"]])
        for todo in sorted_todos:
            item = TodoItemWidget(todo, self.refresh)
            self.layout.addWidget(item)
        self.layout.addStretch(1)
        # 현황 콜백
        if self.stats_callback is not None:
            self.stats_callback(todos)

class TodoAddWidget(QWidget):
    def __init__(self, on_add_callback):
        super().__init__()
        self.on_add_callback = on_add_callback
        self.edit_mode = False
        self.edit_todo_id = None
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)
        # 상단: 새 할일 추가 + * 필수 입력사항 안내
        top_layout = QHBoxLayout()
        self.title_label = QLabel("새 할일 추가")
        self.title_label.setStyleSheet("font-size: 18px;")
        top_layout.addWidget(self.title_label, alignment=Qt.AlignmentFlag.AlignLeft)
        required_label = QLabel('<span style="color:#e74c3c;font-size:15px;font-weight:bold;">*</span> <span style="color:#888;font-size:13px;">필수 입력사항</span>')
        required_label.setTextFormat(Qt.TextFormat.RichText)
        top_layout.addStretch(1)
        top_layout.addWidget(required_label, alignment=Qt.AlignmentFlag.AlignRight)
        layout.addLayout(top_layout)
        # 제목
        title_label = QLabel('<span>제목 <span style="color:#e74c3c">*</span></span>')
        title_label.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(title_label)
        self.title_input = QLineEdit()
        style = """
            QLineEdit {
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                padding: 4px 6px;
                background-color: white;
                color: black;
            }
        """
        self.title_input.setStyleSheet(style)
        layout.addWidget(self.title_input)
        # 설명
        desc_label = QLabel('<span>설명 <span style="color:#e74c3c">*</span></span>')
        desc_label.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(desc_label)
        self.desc_input = QTextEdit()
        style = """
            QTextEdit {
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                padding: 4px 6px;
                background-color: white;
                color: black;
            }
        """
        self.desc_input.setStyleSheet(style)
        layout.addWidget(self.desc_input)
        # 카테고리
        cat_label = QLabel('<span>카테고리 <span style="color:#e74c3c">*</span></span>')
        cat_label.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(cat_label)
        self.category_input = QComboBox()
        self.category_input.addItems(["업무", "개인", "학습", "기타"])
        style = """
            QComboBox {
                border: 1px solid #e5e7eb;
                border-radius: 8px;
            }
        """
        self.category_input.setStyleSheet(style)
        layout.addWidget(self.category_input)
        # 우선순위
        prio_label = QLabel('<span>우선순위 <span style="color:#e74c3c">*</span></span>')
        prio_label.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(prio_label)
        self.priority_input = QComboBox()
        self.priority_input.addItems(["높음", "보통", "낮음"])
        style = """
            QComboBox {
                border: 1px solid #e5e7eb;
                border-radius: 8px;
            }
        """
        self.priority_input.setStyleSheet(style)
        layout.addWidget(self.priority_input)
        # 마감일
        layout.addWidget(QLabel("마감일"))
        self.due_input = QDateEdit()
        self.due_input.setCalendarPopup(True)
        self.due_input.setDate(QDate.currentDate())
        layout.addWidget(self.due_input)
        # 추가/수정 버튼
        self.add_btn = QPushButton("할일 추가")
        self.add_btn.setStyleSheet("background:#22c55e;color:white;border-radius:8px;padding:10px 0;font-weight:bold;font-size:16px;")
        self.add_btn.clicked.connect(self.on_btn_clicked)
        layout.addWidget(self.add_btn)
        # 수정중 상태 취소 버튼 (초기에는 숨김)
        self.cancel_btn = QPushButton("수정중 상태 취소")
        self.cancel_btn.setStyleSheet("background:#e5e7eb;color:#222;border-radius:8px;padding:8px 0;font-weight:bold;font-size:15px;")
        self.cancel_btn.clicked.connect(self.reset_mode)
        self.cancel_btn.setVisible(False)
        layout.addWidget(self.cancel_btn)
        layout.addStretch(1)
        self.setLayout(layout)

    def on_btn_clicked(self):
        if self.edit_mode:
            self.update_todo()
        else:
            self.add_todo()

    def set_edit_mode(self, todo):
        self.edit_mode = True
        self.edit_todo_id = todo.get("id")
        self.title_input.setText(todo.get("title", ""))
        self.desc_input.setText(todo.get("description", ""))
        cat = todo.get("category", "기타")
        prio = todo.get("priority", "보통")
        duedate = todo.get("duedate", "")
        idx_cat = self.category_input.findText(cat)
        if idx_cat >= 0:
            self.category_input.setCurrentIndex(idx_cat)
        idx_prio = self.priority_input.findText(prio)
        if idx_prio >= 0:
            self.priority_input.setCurrentIndex(idx_prio)
        if duedate:
            try:
                self.due_input.setDate(QDate.fromString(duedate, "yyyy-MM-dd"))
            except Exception:
                pass
        self.add_btn.setText("할일 수정하기")
        self.add_btn.setStyleSheet("background:#2563eb;color:white;border-radius:8px;padding:10px 0;font-weight:bold;font-size:16px;")
        self.cancel_btn.setVisible(True)

    def reset_mode(self):
        self.edit_mode = False
        self.edit_todo_id = None
        self.title_input.clear()
        self.desc_input.clear()
        self.category_input.setCurrentIndex(0)
        self.priority_input.setCurrentIndex(0)
        self.due_input.setDate(QDate.currentDate())
        self.add_btn.setText("할일 추가")
        self.add_btn.setStyleSheet("background:#22c55e;color:white;border-radius:8px;padding:10px 0;font-weight:bold;font-size:16px;")
        self.cancel_btn.setVisible(False)

    def add_todo(self):
        title = self.title_input.text().strip()
        desc = self.desc_input.toPlainText().strip()
        category = self.category_input.currentText()
        priority = self.priority_input.currentText()
        duedate = self.due_input.date().toString("yyyy-MM-dd")
        if not title or not desc:
            QMessageBox.warning(self, "입력 오류", "제목과 설명을 모두 입력하세요.")
            return
        resp = api_client.create_todo(title, desc, category, duedate, priority)
        if resp.get("success"):
            QMessageBox.information(self, "추가 완료", "할일이 추가되었습니다.")
            self.reset_mode()
            self.on_add_callback()
        else:
            msg = resp.get("message") or resp.get("detail") or "할일 추가 실패"
            if isinstance(msg, list):
                msg = "\n".join(item.get("msg", str(item)) for item in msg)
            QMessageBox.warning(self, "추가 실패", msg)

    def update_todo(self):
        title = self.title_input.text().strip()
        desc = self.desc_input.toPlainText().strip()
        category = self.category_input.currentText()
        priority = self.priority_input.currentText()
        duedate = self.due_input.date().toString("yyyy-MM-dd")
        if not title or not desc:
            QMessageBox.warning(self, "입력 오류", "제목과 설명을 모두 입력하세요.")
            return
        resp = api_client.update_todo(self.edit_todo_id, title=title, description=desc, category=category, duedate=duedate, priority=priority)
        if resp.get("success"):
            QMessageBox.information(self, "수정 완료", "할일이 수정되었습니다.")
            self.reset_mode()
            self.on_add_callback()
        else:
            msg = resp.get("message") or resp.get("detail") or "할일 수정 실패"
            if isinstance(msg, list):
                msg = "\n".join(item.get("msg", str(item)) for item in msg)
            QMessageBox.warning(self, "수정 실패", msg)

class TodoStatsWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(0, 12, 0, 0)
        title = QLabel("📊 진행 현황")
        title.setStyleSheet("font-weight: bold; font-size: 16px; margin-bottom: 8px;")
        layout.addWidget(title)
        # 총 할일
        stat_total = QHBoxLayout()
        icon_total = QLabel("<img src='https://img.icons8.com/ios-filled/20/000000/todo-list.png'/>")
        stat_total.addWidget(icon_total)
        self.total_label = QLabel("0")
        self.total_label.setStyleSheet("color:#2563eb;font-size:22px;font-weight:bold;")
        stat_total.addWidget(self.total_label)
        stat_total.addWidget(QLabel("총 할일"))
        stat_total.addStretch(1)
        layout.addLayout(stat_total)
        # 완료
        stat_done = QHBoxLayout()
        icon_done = QLabel("<img src='https://img.icons8.com/ios-filled/20/22c55e/checked-checkbox.png'/>")
        stat_done.addWidget(icon_done)
        self.done_label = QLabel("0")
        self.done_label.setStyleSheet("color:#22c55e;font-size:22px;font-weight:bold;")
        stat_done.addWidget(self.done_label)
        stat_done.addWidget(QLabel("완료"))
        stat_done.addStretch(1)
        layout.addLayout(stat_done)
        # 대기
        stat_wait = QHBoxLayout()
        icon_wait = QLabel("<img src='https://img.icons8.com/ios-filled/20/f59e42/hourglass.png'/>")
        stat_wait.addWidget(icon_wait)
        self.wait_label = QLabel("0")
        self.wait_label.setStyleSheet("color:#f59e42;font-size:22px;font-weight:bold;")
        stat_wait.addWidget(self.wait_label)
        stat_wait.addWidget(QLabel("대기"))
        stat_wait.addStretch(1)
        layout.addLayout(stat_wait)
        # 프로그래스바
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(18)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet("""
        QProgressBar {
            border-radius: 8px;
            background: #e5e7eb;  /* 연한 회색 배경 */
            color: white;          /* 글씨 색상 */
            font-weight: bold;     /* 글씨 굵게 */
            text-align: center;    /* 텍스트 가운데 정렬 */
        }
        QProgressBar::chunk {
            background: #32CD32;  /* 진한 연두색 (LimeGreen) */
            border-radius: 8px;
        }
""")

        layout.addWidget(self.progress_bar)
        self.setLayout(layout)
        self.update_stats(0, 0, 0)

    def update_stats(self, total, done, wait):
        self.total_label.setText(str(total))
        self.done_label.setText(str(done))
        self.wait_label.setText(str(wait))
        percent = int((done / total) * 100) if total > 0 else 0
        self.progress_bar.setValue(percent)
        self.progress_bar.setFormat(f"{percent}% 완료")

class TodoSidebar(QFrame):
    def __init__(self, on_todo_added=None):
        super().__init__()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        # 할일 추가 컴포넌트
        self.add_widget = TodoAddWidget(on_todo_added)
        layout.addWidget(self.add_widget)
        # 진행 현황 통계
        self.stats_widget = TodoStatsWidget()
        layout.addWidget(self.stats_widget)
        # 로그아웃/탈퇴 버튼
        self.logout_btn = QPushButton("로그아웃")
        self.logout_btn.setStyleSheet("background:#e5e7eb;color:gray;font-weight:bold; padding:12px 0;font-size:15px;margin-top:16px;")
        self.logout_btn.clicked.connect(self.show_logout_dialog)
        layout.addWidget(self.logout_btn)
        self.withdraw_btn = QPushButton("회원탈퇴")
        self.withdraw_btn.setStyleSheet("background:#e74c3c;color:#fff0f0;font-weight:bold; padding:12px 0; font-size:15px;margin-top:8px;")
        self.withdraw_btn.clicked.connect(self.show_withdraw_dialog)
        layout.addWidget(self.withdraw_btn)
        layout.addStretch(1)
        self.setLayout(layout)
        self.setFixedWidth(320)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        from PyQt6.QtGui import QPalette, QColor
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor("white"))
        self.setPalette(palette)
        self.setAutoFillBackground(True)
        self.setStyleSheet("background: white; border-radius: 8px;")
        self.user_name = ""
        self.user_email = ""
        # fetch_user_info는 로그인 성공 후에만 호출

    def fetch_user_info(self):
        from api_client import load_token
        if not load_token():
            return  # 로그인 전이면 아무것도 하지 않음
        try:
            resp = api_client.get_me()
            if resp.get("success"):
                user_data = resp.get("data", {})
                self.user_name = user_data.get("name", "")
                self.user_email = user_data.get("email", "")
                # self.stats_widget.update_stats(0, 0, 0)  # 이 줄을 제거
            # 로그인 전/실패 시 에러 메시지 표시하지 않음
        except Exception:
            pass

    def set_edit_mode(self, todo):
        self.add_widget.set_edit_mode(todo)

    def update_stats(self, total, done, wait):
        self.stats_widget.update_stats(total, done, wait)

    def show_logout_dialog(self):
        dialog = LogoutDialog(self.user_name, self.user_email, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            mw = self.window()
            if hasattr(mw, "logout"):
                mw.logout()

    def show_withdraw_dialog(self):
        dialog = WithdrawDialog(self.user_name, self.user_email, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            mw = self.window()
            if hasattr(mw, "withdraw"):
                mw.withdraw()

class TodoMainFrame(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        # --- 상단: 할일 목록 + 검색창 ---
        top_layout = QHBoxLayout()
        top_layout.setSpacing(12)
        title = QLabel("할일 목록")
        title.setStyleSheet("font-weight: bold; font-size: 20px;")
        top_layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignVCenter)
        top_layout.addStretch(1)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("제목으로 검색...")
        self.search_input.setFixedWidth(220)
        self.search_input.setStyleSheet("border: 1.5px solid #e5e7eb; border-radius: 8px; padding: 6px 10px; font-size: 15px;")
        self.search_input.textChanged.connect(self.on_search)
        top_layout.addWidget(self.search_input, alignment=Qt.AlignmentFlag.AlignVCenter)
        layout.addLayout(top_layout)
        # --- 두 번째 줄: 카테고리(필터) 버튼들 ---
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(6)
        self.filter_group = QButtonGroup(self)
        self.filter_buttons = {}
        filter_names = [
            ("전체", "all"),
            ("완료", "done"),
            ("미완료", "not_done"),
            ("업무", "업무"),
            ("개인", "개인"),
            ("학습", "학습"),
            ("기타", "기타"),
        ]
        for label, key in filter_names:
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setStyleSheet("QPushButton {padding:3px 10px; min-width: 0; min-height: 0; font-size: 13px; border-radius:6px;} QPushButton:checked {background:#2563eb;color:white;}")
            self.filter_group.addButton(btn)
            self.filter_buttons[key] = btn
            filter_layout.addWidget(btn)
        self.filter_buttons["all"].setChecked(True)
        filter_layout.addStretch(1)
        layout.addLayout(filter_layout)
        self.todo_list = TodoListWidget(self.update_stats_from_list)
        layout.addWidget(self.todo_list)
        self.setLayout(layout)
        self.setStyleSheet("background: #fff; border-radius: 8px;")
        self.current_filter = "all"
        self.current_search = ""
        self.filter_group.buttonClicked.connect(self.on_filter_changed)

    def on_filter_changed(self, btn):
        for key, button in self.filter_buttons.items():
            if button is btn:
                self.current_filter = key
                break
        self.todo_list.set_filter(self.current_filter, self.current_search)

    def on_search(self):
        self.current_search = self.search_input.text().strip()
        self.todo_list.set_filter(self.current_filter, self.current_search)

    def refresh_with_current_filter(self):
        self.todo_list.set_filter(self.current_filter, self.current_search)

    def update_stats_from_list(self, todos):
        total = len(todos)
        done = sum(1 for t in todos if t.get('done'))
        wait = total - done
        # TodoSidebar 인스턴스 찾아서 update_stats 호출
        parent = self.parent()
        while parent is not None:
            if hasattr(parent, 'sidebar'):
                parent.sidebar.update_stats(total, done, wait)
                break
            parent = parent.parent()

# 전체 배경 QSS
class TodoMainPage(QWidget):
    def __init__(self):
        super().__init__()
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(16)
        # 할일 추가 시 목록 새로고침 콜백 연결
        self.main_frame = TodoMainFrame()
        self.sidebar = TodoSidebar(on_todo_added=self.main_frame.refresh_with_current_filter)
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.main_frame, stretch=1)
        self.setLayout(main_layout)

    def set_edit_mode(self, todo):
        self.sidebar.set_edit_mode(todo)

class LogoutDialog(QDialog):
    def __init__(self, user_name, user_email, parent=None):
        super().__init__(parent)
        self.setWindowTitle("")
        self.setFixedWidth(420)
        layout = QVBoxLayout()
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(18)
        # 아이콘
        icon = QLabel()
        icon.setText("<span style='font-size:38px;'>📄</span>")
        icon.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(icon)
        # 제목
        title = QLabel("로그아웃")
        title.setStyleSheet("font-size: 22px; font-weight: bold; margin-bottom: 2px;")
        title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(title)
        # 확인 문구
        msg = QLabel("정말 로그아웃하시겠습니까?")
        msg.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        msg.setStyleSheet("font-size: 15px; margin-bottom: 8px;")
        layout.addWidget(msg)
        # 유저 정보 카드
        user_card = QLabel(f"<b>{user_name}님</b><br><span style='color:#888'>{user_email}</span>")
        user_card.setStyleSheet("background:#f6f8fb;border-radius:8px;padding:14px 18px;font-size:15px;margin-bottom:8px;border:1.5px solid #e5e7eb;")
        layout.addWidget(user_card)
        # 안내문구
        info1 = QLabel("로그아웃하면 현재 세션이 종료됩니다.")
        info2 = QLabel("다시 로그인해야 서비스를 이용할 수 있습니다.")
        info1.setStyleSheet("color:#444;margin-bottom:0px;")
        info2.setStyleSheet("color:#444;margin-bottom:0px;")
        layout.addWidget(info1)
        layout.addWidget(info2)
        # 버튼
        btns = QDialogButtonBox()
        btn_cancel = QPushButton("취소")
        btn_cancel.setStyleSheet("background:#f6f8fb;color:#222;border-radius:8px;padding:10px 0;font-weight:bold;font-size:15px;")
        btn_ok = QPushButton("로그아웃")
        btn_ok.setStyleSheet("background:#222;color:white;border-radius:8px;padding:10px 0;font-weight:bold;font-size:15px;")
        btns.addButton(btn_cancel, QDialogButtonBox.ButtonRole.RejectRole)
        btns.addButton(btn_ok, QDialogButtonBox.ButtonRole.AcceptRole)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)
        self.setLayout(layout)

class WithdrawDialog(QDialog):
    def __init__(self, user_name, user_email, parent=None):
        super().__init__(parent)
        self.setWindowTitle("")
        self.setFixedWidth(480)
        layout = QVBoxLayout()
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(18)
        # 경고 아이콘
        icon = QLabel()
        icon.setText("<span style='font-size:38px;color:#f59e42;'>⚠️</span>")
        icon.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(icon)
        # 제목
        title = QLabel("회원탈퇴")
        title.setStyleSheet("font-size: 22px; font-weight: bold; margin-bottom: 2px;")
        title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(title)
        # 확인 문구
        msg = QLabel("정말로 탈퇴하시겠습니까?")
        msg.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        msg.setStyleSheet("font-size: 15px; margin-bottom: 8px;")
        layout.addWidget(msg)
        # 유저 정보 카드
        user_card = QLabel(f"<b>{user_name}님</b><br><span style='color:#888'>{user_email}</span>")
        user_card.setStyleSheet("background:#f6f8fb;border-radius:8px;padding:14px 18px;font-size:15px;margin-bottom:8px;border:1.5px solid #e5e7eb;")
        layout.addWidget(user_card)
        # 주의사항
        warn = QLabel("""
        <div style='background:#fff0f0;border:2px solid #e74c3c;padding:10px 14px;border-radius:8px;margin:8px 0;'>
        <b style='color:#e74c3c;'>⚠️ 주의사항</b><br>
        <span style='color:#e74c3c;'>탈퇴 후 계정은 복구할 수 없습니다.<br>
        모든 데이터가 영구적으로 삭제됩니다.</span>
        </div>
        """)
        warn.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(warn)
        # 삭제 정보 리스트
        info = QLabel("""
        <div style='margin:8px 0 0 0;'>
        <b>회원탈퇴 시 다음 정보들이 모두 삭제됩니다:</b><br>
        <ul style='margin:0 0 0 16px;'>
        <li>프로필 정보 및 계정 데이터</li>
        <li>작성한 게시물 및 댓글</li>
        <li>포인트 및 쿠폰 정보</li>
        <li>구매 내역 및 결제 정보</li>
        </ul>
        </div>
        """)
        info.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(info)
        # 체크박스
        self.agree_chk = QCheckBox("위 내용을 확인했으며, 회원탈퇴에 동의합니다.")
        layout.addWidget(self.agree_chk)
        # 버튼
        btns = QDialogButtonBox()
        btn_cancel = QPushButton("취소")
        btn_cancel.setStyleSheet("background:#f6f8fb;color:#222;border-radius:8px;padding:10px 0;font-weight:bold;font-size:15px;")
        self.btn_ok = QPushButton("탈퇴하기")
        self.btn_ok.setStyleSheet("background:#e74c3c;color:white;border-radius:8px;padding:10px 0;font-weight:bold;font-size:15px;")
        self.btn_ok.setEnabled(False)
        btns.addButton(btn_cancel, QDialogButtonBox.ButtonRole.RejectRole)
        btns.addButton(self.btn_ok, QDialogButtonBox.ButtonRole.AcceptRole)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)
        self.setLayout(layout)
        self.agree_chk.stateChanged.connect(self.on_check)
    def on_check(self, state):
        self.btn_ok.setEnabled(self.agree_chk.isChecked())

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
        self.login_widget.clear_fields()
        self.stack.setCurrentIndex(0)
        if hasattr(self.main_widget, 'main_frame') and hasattr(self.main_widget.main_frame, 'todo_list'):
            self.main_widget.main_frame.todo_list.set_filter('all', '')

    def show_register(self):
        self.register_widget.clear_fields()
        self.stack.setCurrentIndex(1)

    def show_main(self):
        self.stack.setCurrentIndex(2)
        if hasattr(self.main_widget, 'main_frame') and hasattr(self.main_widget.main_frame, 'todo_list'):
            self.main_widget.main_frame.todo_list.set_filter('all', '')
        if hasattr(self.main_widget, 'sidebar'):
            self.main_widget.sidebar.fetch_user_info()

    def _main_content_widget(self):
        return TodoMainPage()

    def logout(self):
        api_client.logout()
        self.show_login()

    def withdraw(self):
        api_client.withdraw()
        self.show_login()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
