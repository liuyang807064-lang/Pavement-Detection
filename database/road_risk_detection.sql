-- 骑行路面检测与实时预警系统数据库
-- 数据库类型：MySQL
-- 创建时间：2026-03-08
-- 适用于云端部署

-- 创建数据库
CREATE DATABASE IF NOT EXISTS road_risk_detection 
DEFAULT CHARACTER SET utf8mb4 
DEFAULT COLLATE utf8mb4_unicode_ci;

USE road_risk_detection;

-- ===================================================================
-- 用户表
-- ===================================================================
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,                -- 用户 ID，主键，自增
    username VARCHAR(50) NOT NULL UNIQUE,             -- 账号，唯一
    password VARCHAR(255) NOT NULL,                   -- 密码（明文）
    is_admin TINYINT(1) DEFAULT 0,                    -- 是否管理员：1-是，0-否
    INDEX idx_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci 
COMMENT='用户信息表';

-- ===================================================================
-- 道路风险点表
-- ===================================================================
DROP TABLE IF EXISTS road_risks;

CREATE TABLE road_risks (
    id INT AUTO_INCREMENT PRIMARY KEY,                -- 风险点 ID，主键，自增
    latitude DECIMAL(10, 8) NOT NULL,                 -- 纬度（范围：-90 到 90）
    longitude DECIMAL(11, 8) NOT NULL,                -- 经度（范围：-180 到 180）
    risk_type VARCHAR(50) NOT NULL,                   -- 风险类型
    risk_level VARCHAR(20) DEFAULT 'medium',          -- 风险等级：low-低，medium-中，high-高
    description TEXT,                                 -- 问题描述
    contact VARCHAR(100),                             -- 联系方式
    detection_time DATETIME DEFAULT CURRENT_TIMESTAMP, -- 检测时间
    is_submitted TINYINT(1) DEFAULT 0,                -- 是否已提交：1-是，0-否
    INDEX idx_location (latitude, longitude),
    INDEX idx_risk_type (risk_type),
    INDEX idx_risk_level (risk_level),
    INDEX idx_detection_time (detection_time),
    INDEX idx_is_submitted (is_submitted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci 
COMMENT='道路风险点数据表';


