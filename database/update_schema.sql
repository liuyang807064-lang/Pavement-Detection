-- 数据库更新脚本：为 road_risks 表添加新字段
-- 创建时间：2026-03-27
-- 用途：支持危险路段上报功能增强

USE road_risk_detection;

-- 检查字段是否存在，如果不存在则添加
-- 添加 risk_level 字段（风险等级）
ALTER TABLE road_risks 
ADD COLUMN IF NOT EXISTS risk_level VARCHAR(20) DEFAULT 'medium' 
COMMENT '风险等级：low-低，medium-中，high-高' 
AFTER risk_type;

-- 添加 description 字段（问题描述）
ALTER TABLE road_risks 
ADD COLUMN IF NOT EXISTS description TEXT 
COMMENT '问题描述' 
AFTER risk_level;

-- 添加 contact 字段（联系方式）
ALTER TABLE road_risks 
ADD COLUMN IF NOT EXISTS contact VARCHAR(100) 
COMMENT '联系方式' 
AFTER description;

-- 添加 risk_level 索引
ALTER TABLE road_risks 
ADD INDEX IF NOT EXISTS idx_risk_level (risk_level);

-- 显示表结构
DESC road_risks;

-- 显示所有索引
SHOW INDEX FROM road_risks;
