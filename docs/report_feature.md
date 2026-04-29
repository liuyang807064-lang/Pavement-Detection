# 危险路段上报功能使用说明

## 📋 功能概述

危险路段上报功能允许用户在地图上选择位置并提交路面风险信息，系统会将这些信息存储到数据库中，等待管理员审核后显示在地图上。

## 🎯 主要特性

### 1. 地图选点
- 集成高德地图 API
- 点击地图选择风险点位置
- 支持拖动标记微调位置
- 实时显示经纬度坐标

### 2. 风险信息填报
- **风险类型**（必填）：
  - 🕳️ 坑洼 (Pothole)
  - ↔️ 纵向裂缝 (Longitudinal Crack)
  - ↕️ 横向裂缝 (Transverse Crack)
  - 🐊 网状裂缝 (Alligator Crack)
  - ➖ 纵向补丁 (Longitudinal Patch)
  - ➗ 横向补丁 (Transverse Patch)
  - ⭕ 井盖 (Manhole Cover)
  - 🔶 其他 (Other)

- **风险等级**（可选）：
  - 低 - 轻微影响，注意即可
  - 中 - 需要减速慢行（默认）
  - 高 - 建议绕行

- **问题描述**（可选）：详细描述风险情况

- **联系方式**（可选）：便于后续核实

### 3. 历史记录
- 显示所有上报记录
- 状态标识：
  - ✅ 已提交：已通过审核，显示在地图上
  - ⏳ 待审核：等待管理员审核
- 点击记录可定位到相应风险点

## 🚀 使用步骤

### 第一步：访问上报页面
1. 登录系统（演示账号：admin / 123456）
2. 点击首页"危险路段上报"卡片中的"我要上报"按钮
3. 或直接访问：`http://localhost:5000/report`

### 第二步：选择风险点位置
1. 在地图上点击想要上报的位置
2. 地图上会出现一个可拖动的标记
3. 可以拖动标记微调位置
4. 经纬度坐标会实时更新

### 第三步：填写风险信息
1. 选择风险类型（必填）
2. 选择风险等级（可选，默认为"中"）
3. 填写问题描述（可选）
4. 填写联系方式（可选）

### 第四步：提交上报
1. 点击"立即上报"按钮
2. 等待系统处理
3. 收到成功提示后，上报完成

### 第五步：查看历史记录
1. 右侧面板会显示所有上报记录
2. 可以查看每条记录的状态
3. 点击记录可在地图上定位

## 🗄️ 数据库配置

### 更新数据库表结构

执行以下 SQL 脚本添加新字段：

```bash
# 方法 1：使用 MySQL 命令行
mysql -u liuyang -p road_risk_detection < database/update_schema.sql

# 方法 2：在 MySQL 客户端中执行
USE road_risk_detection;
SOURCE database/update_schema.sql;
```

### 新增字段说明
- `risk_level`: 风险等级（VARCHAR(20)），默认值 'medium'
- `description`: 问题描述（TEXT），可为空
- `contact`: 联系方式（VARCHAR(100)），可为空

## 🔧 后端接口

### 1. 提交上报接口
```
POST /api/report/submit
Content-Type: application/json

请求体：
{
    "latitude": 39.90923,
    "longitude": 116.397428,
    "risk_type": "Pothole",
    "risk_level": "medium",
    "description": "路面有一个直径约 20cm 的坑洼",
    "contact": "example@email.com"
}

响应：
{
    "success": true,
    "message": "上报成功，等待审核",
    "id": 123
}
```

### 2. 获取历史记录接口
```
GET /api/report/history

响应：
{
    "success": true,
    "data": [
        {
            "id": 123,
            "latitude": 39.90923,
            "longitude": 116.397428,
            "risk_type": "Pothole",
            "risk_level": "medium",
            "description": "路面有一个直径约 20cm 的坑洼",
            "contact": "example@email.com",
            "is_submitted": 0,
            "detection_time": "2026-03-27 10:30:00"
        }
    ]
}
```

## 📱 移动端适配

上报页面完全支持移动端：
- 响应式设计，自适应各种屏幕尺寸
- 触摸友好的交互界面
- 手机端可通过首页访问

## 🔐 权限说明

当前版本：
- 所有用户（包括未登录）都可以访问上报页面
- 提交上报不需要登录验证
- 历史记录显示所有用户的上报记录

未来改进方向：
- 添加用户认证，只显示当前用户的上报记录
- 管理员可以审核、删除上报记录
- 添加举报反馈机制

## ⚠️ 注意事项

1. **高德地图 API 配置**
   - 需要在高德开放平台申请 Key
   - 替换 `report_form.html` 中的安全密钥和 Key
   ```html
   <script type="text/javascript">
       window._AMapSecurityConfig = {
           securityJsCode: '您的高德地图安全密钥'
       };
   </script>
   <script src="https://webapi.amap.com/maps?v=2.0&key=您的高德地图 Key"></script>
   ```

2. **数据审核流程**
   - 新提交的上报数据 `is_submitted = 0`（待审核）
   - 管理员审核后设置为 `is_submitted = 1`（已提交）
   - 只有已提交的数据才会显示在地图上

3. **坐标系统**
   - 使用高德地图 GCJ-02 坐标系
   - 存储到数据库时会自动转换

## 🎨 界面预览

### 桌面端
- 左侧：地图 + 上报表单
- 右侧：历史记录列表

### 移动端
- 上下布局，依次显示地图、表单、历史记录
- 所有功能完整支持

## 💡 使用技巧

1. **快速定位**：点击历史记录可以快速定位到该风险点
2. **拖动微调**：标记可以拖动，方便精确定位
3. **风险等级**：根据实际危害程度选择合适的等级
4. **详细描述**：建议填写详细描述，便于后续处理

## 📞 技术支持

如有问题，请联系：
- 检查浏览器控制台错误信息
- 确认网络连接正常
- 验证高德地图 API Key 配置正确
