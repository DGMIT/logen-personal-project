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
    QListWidget, QListWidgetItem, QMenu, QInputDialog, QTextEdit, QComboBox, QDateEdit, QCheckBox, QScrollArea, QButtonGroup
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
        # Remove button_bar and related logic
        # self.button_bar = QWidget() ...
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
    def toggle_done(self, state):
        api_client.update_todo(self.todo['id'], done=bool(state))
        self.refresh_callback()
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
        self._filter = "all"
        self.refresh()

    def set_filter(self, filter_key):
        self._filter = filter_key
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
        elif self._filter in ("업무", "개인", "학습"):
            params["category"] = self._filter
        resp = api_client.list_todos(**params)
        todos = resp.get('data', {}).get('todos', []) if resp.get('success') else []
        for todo in todos:
            item = TodoItemWidget(todo, self.refresh)
            self.layout.addWidget(item)
        self.layout.addStretch(1)

class TodoAddWidget(QWidget):
    def __init__(self, on_add_callback):
        super().__init__()
        self.on_add_callback = on_add_callback
        self.edit_mode = False
        self.edit_todo_id = None
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)
        # 제목
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("할일 제목을 입력하세요")
        layout.addWidget(QLabel("제목"))
        layout.addWidget(self.title_input)
        # 설명
        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("상세 설명을 입력하세요")
        self.desc_input.setFixedHeight(48)
        layout.addWidget(QLabel("설명"))
        layout.addWidget(self.desc_input)
        # 카테고리
        self.category_input = QComboBox()
        self.category_input.addItems(["업무", "개인", "학습", "기타"])
        layout.addWidget(QLabel("카테고리"))
        layout.addWidget(self.category_input)
        # 우선순위
        self.priority_input = QComboBox()
        self.priority_input.addItems(["높음", "보통", "낮음"])
        layout.addWidget(QLabel("우선순위"))
        layout.addWidget(self.priority_input)
        style = """
            QComboBox {
                background-color: white;
                color: black;
            }
            QComboBox QListView::item:hover {
                color: black; /* 호버 시 글씨 색 */
                background-color: #e0e0e0; /* 호버 시 배경 */
            }
            QComboBox QListView::item:selected {
                color: white; /* 선택된 항목 텍스트 */
                background-color: #0078d7; /* 선택된 항목 배경 */
            }
        """
        self.category_input.setStyleSheet(style)
        self.priority_input.setStyleSheet(style)
        # 마감일
        self.due_input = QDateEdit()
        self.due_input.setCalendarPopup(True)
        self.due_input.setDate(QDate.currentDate())
        layout.addWidget(QLabel("마감일"))
        layout.addWidget(self.due_input)
        # 추가/수정 버튼
        self.add_btn = QPushButton("할일 추가")
        self.add_btn.setStyleSheet("background:#22c55e;color:white;border-radius:8px;padding:10px 0;font-weight:bold;font-size:16px;")
        self.add_btn.clicked.connect(self.on_btn_clicked)
        layout.addWidget(self.add_btn)
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

class TodoSidebar(QWidget):
    def __init__(self, on_todo_added=None):
        super().__init__()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        # 할일 추가 컴포넌트
        self.add_widget = TodoAddWidget(on_todo_added)
        layout.addWidget(self.add_widget)
        # 예시 타이틀
        title = QLabel("사이드바")
        title.setStyleSheet("font-weight: bold; font-size: 18px;")
        layout.addWidget(title)
        layout.addStretch(1)
        self.setLayout(layout)
        self.setFixedWidth(320)
        self.setStyleSheet("background: #f8fafc; border-radius: 8px;")

    def set_edit_mode(self, todo):
        self.add_widget.set_edit_mode(todo)

class TodoMainFrame(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        # 필터 바 추가
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(8)
        self.filter_group = QButtonGroup(self)
        self.filter_buttons = {}
        filter_names = [
            ("전체", "all"),
            ("완료", "done"),
            ("미완료", "not_done"),
            ("업무", "업무"),
            ("개인", "개인"),
            ("학습", "학습"),
        ]
        for label, key in filter_names:
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setStyleSheet("QPushButton {padding:6px 18px;border-radius:8px;} QPushButton:checked {background:#2563eb;color:white;}")
            self.filter_group.addButton(btn)
            self.filter_buttons[key] = btn
            filter_layout.addWidget(btn)
        self.filter_buttons["all"].setChecked(True)
        layout.addLayout(filter_layout)
        title = QLabel("할일 목록")
        title.setStyleSheet("font-weight: bold; font-size: 18px;")
        layout.addWidget(title)
        self.todo_list = TodoListWidget()
        layout.addWidget(self.todo_list)
        self.setLayout(layout)
        self.setStyleSheet("background: #fff; border-radius: 8px;")
        self.current_filter = "all"
        self.filter_group.buttonClicked.connect(self.on_filter_changed)

    def on_filter_changed(self, btn):
        for key, button in self.filter_buttons.items():
            if button is btn:
                self.current_filter = key
                break
        self.todo_list.set_filter(self.current_filter)

    def refresh_with_current_filter(self):
        self.todo_list.set_filter(self.current_filter)

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
        self.setStyleSheet("background: #f6f8fb;")

    def set_edit_mode(self, todo):
        self.sidebar.set_edit_mode(todo)

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
