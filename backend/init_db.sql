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
