# Student Mistakes Manager

智能初中错题管理 OpenClaw Skill。

## 功能

- 📝 一键添加错题（用户只需给题目）
- 🔄 艾宾浩斯记忆曲线复习
- 📊 掌握程度追踪
- 🔍 QMD 全文搜索

## 安装

```bash
openclaw skill install qianjinfeng/student-mistakes-system
```

或从本地安装：

```bash
cp -r student-mistakes-system ~/.openclaw/workspace/skills/
```

## 使用

### 添加错题

```
用户: 这道题不会做：已知直角三角形的两直角边分别为3和4，求斜边长
```

自动识别学科、知识点、难度。

### 复习

```
用户: 今天要复习
```

### 搜索

```
用户: 搜索勾股定理相关错题
```

## 目录结构

```
mistakes/
├── math/
│   └── 2026-03.md
├── chinese/
├── english/
├── physics/
└── chemistry/
```

## 掌握程度

| 程度 | 含义 | 复习间隔 |
|------|------|----------|
| forgotten | 忘记 | 1天 |
| fuzzy | 模糊 | 1天 |
| remembered | 记住 | 艾宾浩斯 |
| mastered | 精通 | 60天抽查 |

## 依赖

- QMD (可选): `npm install -g @tobilu/qmd`

## License

MIT
