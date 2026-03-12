# Student Mistakes Manager

智能初中错题管理 OpenClaw Skill。

## 功能

- 📝 新增错题（文字输入）
- 🔄 艾宾浩斯记忆曲线复习
- 📊 掌握程度管理
- 🔍 QMD 全文搜索
- 📈 统计面板

## 支持学科

- 数学 (math)
- 语文 (chinese)
- 英语 (english)
- 物理 (physics)
- 化学 (chemistry)

## 安装

```bash
openclaw skill install student-mistakes-manager
```

或从本地安装：

```bash
cp -r student-mistakes-system ~/.openclaw/workspace/skills/
```

## 配置

在 `~/.openclaw/config.json` 中添加：

```json
{
  "skills": {
    "student-mistakes-manager": {
      "mistakesDir": "./mistakes",
      "qmdEnabled": true
    }
  }
}
```

## 使用

### 新增错题

```
用户: 这道数学题我不会做：已知直角三角形的两直角边分别为3和4，求斜边长
```

### 复习

```
用户: 今天要复习
```

### 搜索

```
用户: 搜索勾股定理相关错题
```

## 掌握程度

| 程度 | 含义 | 复习间隔 |
|------|------|----------|
| forgotten | 完全不会 | 1天 |
| fuzzy | 会但不确定 | 1天 |
| remembered | 正确且有把握 | 艾宾浩斯阶段 |
| mastered | 精通掌握 | 60天抽查 |

## 艾宾浩斯间隔

| 阶段 | 复习次数 | 间隔(天) |
|------|----------|----------|
| 0 | 0 | 1 |
| 1 | 1 | 1 |
| 2 | 2 | 3 |
| 3 | 3 | 7 |
| 4 | 4 | 15 |
| 5 | 5 | 30 |
| 6 | 6 | 60 |
| 7+ | 7+ | 90 |

## 目录结构

```
mistakes/
├── math/
│   ├── grade7/
│   ├── grade8/
│   └── grade9/
├── chinese/
├── english/
├── physics/
└── chemistry/
```

## 工具

- `add_mistake` - 新增错题
- `get_due_reviews` - 获取今日待复习
- `update_mastery` - 更新掌握程度
- `search_mistakes` - 搜索错题
- `get_statistics` - 获取统计

## 依赖

- QMD (可选): `npm install -g @tobilu/qmd`

## License

MIT
