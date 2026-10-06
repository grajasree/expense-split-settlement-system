-- ============================================================
-- Expense Split and Settlement System - Database Script
-- Run:  mysql -u root -p < schema.sql
-- ============================================================

CREATE DATABASE IF NOT EXISTS expense_split_db;
USE expense_split_db;

-- 1. USERS -------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    email       VARCHAR(150) NOT NULL UNIQUE,
    password    VARCHAR(255) NOT NULL          -- stores a HASH, never plain text
);

-- 2. GROUPS ------------------------------------------------
-- NOTE: `groups` is a reserved word in MySQL 8, so it is always written with backticks.
CREATE TABLE IF NOT EXISTS `groups` (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    group_name  VARCHAR(100) NOT NULL,
    created_by  INT NOT NULL,
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- 3. GROUP MEMBERS -----------------------------------------
CREATE TABLE IF NOT EXISTS group_members (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    group_id    INT NOT NULL,
    user_id     INT NOT NULL,
    UNIQUE KEY unique_member (group_id, user_id),
    FOREIGN KEY (group_id) REFERENCES `groups`(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id)  REFERENCES users(id)
);

-- 4. EXPENSES ----------------------------------------------
CREATE TABLE IF NOT EXISTS expenses (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    group_id    INT NOT NULL,
    description VARCHAR(255) NOT NULL,
    amount      DECIMAL(10,2) NOT NULL,
    paid_by     INT NOT NULL,
    date        DATE NOT NULL,
    FOREIGN KEY (group_id) REFERENCES `groups`(id) ON DELETE CASCADE,
    FOREIGN KEY (paid_by)  REFERENCES users(id)
);

-- 5. EXPENSE SPLITS (extra helper table) -------------------
-- Stores how much each person owes for each expense.
-- Needed to support equal / percentage / custom splits.
CREATE TABLE IF NOT EXISTS expense_splits (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    expense_id   INT NOT NULL,
    user_id      INT NOT NULL,
    share_amount DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (expense_id) REFERENCES expenses(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id)    REFERENCES users(id)
);

-- 6. SETTLEMENTS -------------------------------------------
-- group_id is an extra column so balances can be tracked per group.
CREATE TABLE IF NOT EXISTS settlements (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    group_id    INT NOT NULL,
    from_user   INT NOT NULL,
    to_user     INT NOT NULL,
    amount      DECIMAL(10,2) NOT NULL,
    status      ENUM('pending','completed') NOT NULL DEFAULT 'pending',
    FOREIGN KEY (group_id)  REFERENCES `groups`(id) ON DELETE CASCADE,
    FOREIGN KEY (from_user) REFERENCES users(id),
    FOREIGN KEY (to_user)   REFERENCES users(id)
);
