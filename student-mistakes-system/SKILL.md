---
name: student-mistakes-manager
version: 1.0.0
author: student-mistakes-system
description: 智能初中错题管理。用户只需提供题目内容（文字或图片），自动识别学科、知识点、难度，存入错题本。按艾宾浩斯记忆曲线安排复习。
triggers:
  - 错题
  - 不会做
  - 错题本
  - 批改
  - 复习错题
  - 今天复习
  - 艾宾浩斯
  - 复习
  - 搜索错题
dependencies: []
tools:
  - add_mistake
  - get_due_reviews
  - update_mastery
  - search_mistakes
  - get_statistics
---

# 智能初中错题管理器

帮助初中学生管理错题的 AI 助手。用户只需提供题目，其他自动处理。

## 功能

1. **自动识别** - 根据题目内容自动识别学科、知识点、难度
2. **一键存储** - 用户只需给题目，其他自动完成
3. **艾宾浩斯复习** - 自动计算复习间隔
4. **掌握程度追踪** - forgotten/fuzzy/remembered/mastered

## 目录结构

```
mistakes/
├── math/
│   └── 2026-03-12.md
├── chinese/
├── english/
├── physics/
└── chemistry/
```

## 使用方式

### 添加错题

```
用户: 这道题不会做：已知直角三角形的两直角边分别为3和4，求斜边长
```

**自动处理：**
- 识别学科：数学
- 识别知识点：勾股定理
- 评估难度：简单
- 存入对应学科文件

### 复习

```
用户: 今天要复习
```

### 搜索

```
用户: 搜索勾股定理相关错题
```

## 存储格式

每月一个文件：

```markdown
---
subject: math
date: 2026-03-12
tags: [勾股定理, 几何]

review:
  count: 0
  next_review: 2026-03-13
  mastery: forgotten
  stage: 0
---

# 错题

## 001 - 2026-03-12

**题目**: 已知直角三角形的两直角边分别为3和4，求斜边长

**答案**: 5

**解析**: 根据勾股定理，c² = a² + b² = 9 + 16 = 25，c = √25 = 5
```

## 掌握程度

| mastery | 含义 | 复习间隔 |
|---------|------|----------|
| forgotten | 完全不会 | 1天 |
| fuzzy | 会但不确定 | 1天 |
| remembered | 正确且有把握 | 艾宾浩斯 |
| mastered | 精通 | 60天抽查 |

## 艾宾浩斯间隔

| 阶段 | 间隔(天) |
|------|----------|
| 0 | 1 |
| 1 | 1 |
| 2 | 3 |
| 3 | 7 |
| 4 | 15 |
| 5 | 30 |
| 6 | 60 |
| 7+ | 90 |

## 工具

### add_mistake

**参数：**
- `content` (string): 题目内容（必需）
- `answer` (string): 正确答案（可选）
- `analysis` (string): 解析（可选）

### get_due_reviews

获取今日待复习。

### update_mastery

更新掌握程度。

### search_mistakes

搜索错题。

### get_statistics

获取统计。
