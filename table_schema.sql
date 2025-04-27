


CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL
);


CREATE TABLE generated_arguments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    case_id VARCHAR(255),
    generated_arguments TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_solved BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES users(id)
);


CREATE TABLE blacklisted_tokens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at DATETIME NOT NULL
);

CREATE INDEX idx_token ON blacklisted_tokens (token);
CREATE INDEX idx_expires_at ON blacklisted_tokens (expires_at);



-- You might also want to periodically clean up expired tokens using:
DELETE FROM blacklisted_tokens WHERE expires_at < NOW();