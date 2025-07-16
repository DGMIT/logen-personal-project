CREATE DATABASE IF NOT EXISTS todo_app;
USE todo_app;

CREATE TABLE IF NOT EXISTS user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS todo (
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

CREATE INDEX IF NOT EXISTS idx_todo_user_id ON todo(user_id);
CREATE INDEX IF NOT EXISTS idx_todo_duedate ON todo(duedate);
CREATE INDEX IF NOT EXISTS idx_todo_done ON todo(done);
CREATE INDEX IF NOT EXISTS idx_todo_user_priority ON todo(user_id, priority);
