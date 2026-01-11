# 学生错题管理系统 (Student Mistakes Management System)

一个基于AI的智能学生错题管理系统，通过OCR技术识别错题图片，使用Qwen大模型进行错误分析，并通过间隔重复算法优化复习效果。

## 🎯 项目目标

构建一个AI驱动的学生错题管理系统，帮助学习者通过智能追踪、分析和复习错题来提升学习效果。系统结合了**多模态AI (OCR + LLM)**、**间隔重复**和**游戏化**机制来增强学习动力和长期记忆。

## 🧱 核心组件

### 1. 前端 (Frontend)
- **技术栈**: React (TypeScript) + Vite + Tailwind CSS
- **功能**: 图片上传/拍照、错题分析展示、复习任务、成就系统
- **语言**: 简体中文用户界面

### 2. OCR 识别层 (OCR Processor)
- **技术**: PaddleOCR_VL
- **功能**:
  - 鲁棒的中文文本检测与识别
  - 布局感知的题目分割
  - 存储原始OCR结果用于调试

### 3. AI 推理层 (AI Analyzer)
- **技术**: Qwen (Qwen-VL 或 Qwen-Max)
- **功能**:
  - 判断答案正确性
  - 分类错误类型 (概念错误、计算错误、读题错误等)
  - 基于过往相似错误的个性化洞察
  - 可选生成相似练习题

### 4. 后端API (Backend API)
- **技术栈**: FastAPI + Python
- **功能**:
  - RESTful/GraphQL 接口
  - 身份验证 (OAuth2/JWT)
  - 文件安全验证
  - 速率限制

### 5. 数据库 (Database)
- **技术**: PostgreSQL (+ pgvector 用于未来语义相似度)
- **数据表**:
  - `mistakes`: 错题图片、OCR文本、错误类型、AI洞察
  - `users`: 用户信息、进度统计
  - `review_history`: 复习历史记录
  - `scheduled_reviews`: 间隔重复复习计划
  - `achievements`: 成就和奖章

### 6. 复习引擎 (Review Engine)
- **算法**: 间隔重复 (SM-2 或自定义变体)
- **功能**:
  - 基于错误频率的复习计划
  - 知识差距分析
  - 复习时间优化

### 7. 游戏化模块 (Gamification Engine)
- **功能**: 积分系统、连续学习 streak、成就解锁
- **规则**: 可配置的游戏化规则 (无需代码修改)

## 🚀 快速开始

### 使用 Docker Compose (推荐)

1. **克隆项目**
```bash
git clone <repository-url>
cd student-mistakes-system
```

2. **配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件，设置数据库和AI服务配置
```

3. **启动完整系统**
```bash
docker-compose up -d
```

4. **访问应用**
- 前端: http://localhost:3000
- API文档: http://localhost:8000/docs
- 后端API: http://localhost:8000

### 手动安装

#### 后端设置
```bash
cd backend
pip install -r requirements.txt
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

#### 前端设置
```bash
cd frontend
npm install
npm run dev
```

#### 数据库初始化
```bash
# 连接到PostgreSQL
psql -h localhost -U postgres -d student_mistakes -f database/schema.sql
```

## 📊 功能特性

### ✅ 已实现功能
- [x] 用户注册和登录 (JWT认证)
- [x] 错题图片上传和OCR文本提取
- [x] AI驱动的错误分析和洞察
- [x] 基础的间隔重复复习计划
- [x] 积分和成就系统
- [x] 响应式前端界面
- [x] Docker容器化部署
- [x] 完整的API文档

### 🚧 开发中功能
- [ ] 高级复习算法优化
- [ ] 相似题目推荐
- [ ] 学习进度可视化
- [ ] 移动端适配
- [ ] 批量错题导入

### 📋 计划功能
- [ ] 语音识别和语音反馈
- [ ] 学习小组和协作功能
- [ ] 教师端管理界面
- [ ] 数据分析和学习报告
- [ ] 离线学习模式

## 🛠️ 技术栈

### 后端
- **Web框架**: FastAPI
- **数据库**: PostgreSQL + SQLAlchemy
- **身份验证**: JWT + OAuth2
- **AI服务**: OpenAI兼容API (Qwen)
- **OCR**: PaddleOCR
- **任务队列**: Celery + Redis
- **配置**: Pydantic + YAML

### 前端
- **框架**: React 18 + TypeScript
- **构建工具**: Vite
- **样式**: Tailwind CSS
- **状态管理**: React Hooks
- **HTTP客户端**: Axios
- **路由**: React Router

### 基础设施
- **容器化**: Docker + Docker Compose
- **数据库**: PostgreSQL
- **缓存/队列**: Redis
- **反向代理**: (可选) Nginx

## 📏 代码规范

### Python 代码规范
- 使用类型提示 (mypy严格模式)
- Pydantic v2 数据模型
- 自定义异常类
- 异步I/O操作
- 结构化日志

### TypeScript/React 规范
- 函数式组件 + Hooks
- 严格TypeScript配置
- Props接口定义
- Tailwind CSS工具类优先
- 错误边界处理

### 提交规范
```
feat: 新功能
fix: 修复bug
docs: 文档更新
style: 代码风格调整
refactor: 代码重构
test: 测试相关
chore: 构建/工具配置
```

## 🧪 测试

### 运行后端测试
```bash
cd backend
pytest
pytest --cov=src --cov-report=html
```

### 运行前端测试
```bash
cd frontend
npm test
```

### 运行集成测试
```bash
# 需要先启动所有服务
docker-compose up -d
pytest tests/integration/
```

## 🔧 配置说明

### 环境变量 (.env)
```bash
# 数据库
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/student_mistakes

# AI服务
QWEN_API_KEY=your-qwen-api-key
QWEN_BASE_URL=https://dashscope.aliyuncs.com/api/v1

# 安全
SECRET_KEY=your-super-secret-key
ALGORITHM=HS256

# 文件上传
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=5242880
```

### 游戏化配置 (config/settings.yaml)
```yaml
gamification:
  achievements:
    streak_7_days:
      name: "连续学习7天"
      description: "连续7天完成复习任务"
      points: 50
  points:
    mistake_uploaded: 10
    review_completed: 5
```

## 📈 项目架构

```
student-mistakes-system/
├── frontend/                 # React前端应用
│   ├── src/
│   │   ├── components/      # 可复用组件
│   │   ├── pages/          # 页面组件
│   │   ├── hooks/          # 自定义Hooks
│   │   └── services/       # API服务
│   ├── package.json
│   └── Dockerfile
├── backend/                 # FastAPI后端
│   ├── api/                # API路由和主应用
│   ├── models/             # SQLAlchemy模型
│   ├── services/           # 业务逻辑服务
│   ├── config/             # 配置管理
│   ├── requirements.txt
│   └── Dockerfile
├── database/               # 数据库相关
│   └── schema.sql          # PostgreSQL表结构
├── config/                 # 全局配置
│   └── settings.yaml       # 应用配置
├── tests/                  # 测试文件
├── docker-compose.yml      # Docker编排
├── AGENTS.md              # 开发指南
└── README.md
```

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📝 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- [FastAPI](https://fastapi.tiangolo.com/) - 现代Python Web框架
- [React](https://reactjs.org/) - 用户界面库
- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) - OCR引擎
- [Qwen](https://github.com/QwenLM/Qwen) - 大语言模型
- [Tailwind CSS](https://tailwindcss.com/) - 实用优先的CSS框架

---

**让学习成为一种享受！** 🎓✨