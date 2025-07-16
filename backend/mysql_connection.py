import mysql.connector
from mysql.connector import errorcode
from mysql.connector.connection import MySQLConnection


# database.py
def ensure_tables_exist(cnx: MySQLConnection):
    cursor = cnx.cursor()
    cursor.execute(
        """
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = DATABASE() AND table_name IN ('user', 'todo');
    """
    )
    existing_tables = {row[0] for row in cursor.fetchall()}

    if "user" not in existing_tables:
        cursor.execute(
            """
            CREATE TABLE user (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(50) NOT NULL,
                email VARCHAR(100) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL
            );
        """
        )

    if "todo" not in existing_tables:
        cursor.execute(
            """
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
        """
        )
        # 인덱스 생성
        cursor.execute("CREATE INDEX idx_todo_user_id ON todo(user_id);")
        cursor.execute("CREATE INDEX idx_todo_duedate ON todo(duedate);")
        cursor.execute("CREATE INDEX idx_todo_done ON todo(done);")
        cursor.execute(
            "CREATE INDEX idx_todo_user_priority ON todo(user_id, priority);"
        )

    cnx.commit()
    cursor.close()


def get_connection(config):
    print(config)
    try:
        cnx = mysql.connector.connect(**config)
        return cnx
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
        return None


def get_all_users(cnx: MySQLConnection):
    with cnx.cursor() as cursor:
        cursor.execute("SELECT * FROM user")
        rows = cursor.fetchall()
        for row in rows:
            print(row)


def insert_user(email: str, password: str, name: str, cnx: MySQLConnection):
    cursor = cnx.cursor()
    cursor.execute("SELECT COUNT(*) FROM user WHERE email = %s", (email,))
    count = cursor.fetchone()[0]
    if count > 0:
        print("이미 존재하는 이메일입니다.")
        return
    sql = "INSERT INTO user (email,password,name) VALUES (%s, %s, %s)"
    cursor.execute(sql, (email, password, name))
    cnx.commit()
    cursor.close()


def select_user_by_email(email, cnx: MySQLConnection):
    with cnx.cursor() as cursor:
        sql = "SELECT * FROM user WHERE email = %s"
        cursor.execute(sql, (email,))
        print("select_user_by_email", cursor.fetchone())

