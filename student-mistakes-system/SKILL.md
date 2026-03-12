---
name: student-mistakes-manager
version: 1.0.0
author: student-mistakes-system
description: 智能初中错题管理。支持新增错题（文字/图片）、艾宾浩斯记忆曲线复习、掌握程度管理、QMD搜索。按学科年级存储为独立markdown文件，每题包含复习属性。
triggers:
  - 错题
  - 不会做
  - 错题本
  - 不会
  - 批改
  - 复习错题
  - 今天复习
  - 艾宾浩斯
  - 复习
  - 搜索错题
  - 找错题
  - 抽查
dependencies: []
tools:
  - add_mistake
  - get_due_reviews
  - update_mastery
  - search_mistakes
  - get_statistics
---

# 智能初中错题管理器

帮助初中学生管理错题的 AI 助手。按艾宾浩斯记忆曲线安排复习，支持掌握程度追踪。

## 功能

1. **新增错题** - 文字/图片输入 → 分析 → 存储
2. **艾宾浩斯复习** - 自动计算复习间隔
3. **掌握程度管理** - forgotten/fuzzy/remembered/mastered
4. **QMD 搜索** - 全文搜索错题
5. **统计面板** - 查看学习进度

## 目录结构

```
mistakes/
├── math/
│   ├── grade7/
│   │   └── 2026-03-12-001.md
│   ├── grade8/
│   └── grade9/
├── chinese/
├── english/
├── physics/
└── chemistry/
```

## 使用示例

### 新增错题

```
用户: 这道数学题我不会做：已知直角三角形的两直角边分别为3和4，求斜边长

AI: 分析题目...
   - 学科：数学
   - 知识点：勾股定理
   - 难度：简单

解题：斜边 = √(3² + 4²) = 5

是否存入错题本？请告诉我年级。
```

### 复习

```
用户: 今天要复习

AI: 今日待复习错题（共3道）：
1. [数学-初二] 勾股定理 - fuzzy
2. [数学-初二] 一元二次方程 - remembered  
3. [英语-初三] 语法填空 - forgotten

请依次回答，格式：题号 + 答案 + 掌握程度
```

### 搜索

```
用户: 搜索勾股定理相关错题

AI: 找到2道相关错题：
1. 数学-初二-2026-03-12-001 (remembered)
2. 数学-初二-2026-03-10-005 (fuzzy)
```

## Markdown 模板

每道错题一个 md 文件：

```markdown
---
subject: math
grade: grade8
date: 2026-03-12
source: homework
type: application
difficulty: medium
tags: [勾股定理, 几何]

review:
  count: 0
  last_review: null
  next_review: 2026-03-13
  mastery: forgotten

ebb:
  stage: 0
  intervals: [1, 3, 7, 15, 30, 60, 90]
  last_mastered: null
---

# 错题记录

## 基本信息
- 学科: 数学
- 年级: 初二
- 日期: 2026-03-12
- 来源: 作业
- 类型: 应用题
- 难度: 中等
- 知识点: 勾股定理

## 题目
已知直角三角形的两直角边分别为3和4，求斜边长。

## 错误原因
对勾股定理理解不深

## 正确答案
斜边长为5

## 解析
1. 已知 a=3, b=4
2. 根据勾股定理: c² = a² + b² = 9 + 16 = 25
3. c = √25 = 5
```

## 掌握程度

| mastery | 含义 | 复习间隔 |
|---------|------|----------|
| forgotten | 完全不会 | 1天 |
| fuzzy | 会但不确定 | 1天 |
| remembered | 正确且有把握 | 艾宾浩斯阶段 |
| mastered | 精通掌握 | 60天抽查 |

## 艾宾浩斯阶段

| stage | 复习次数 | 间隔(天) |
|-------|----------|----------|
| 0 | 0 | 1 |
| 1 | 1 | 1 |
| 2 | 2 | 3 |
| 3 | 3 | 7 |
| 4 | 4 | 15 |
| 5 | 5 | 30 |
| 6 | 6 | 60 |
| 7+ | 7+ | 90 |

## 配置

在 `~/.openclaw/config.json` 中配置：

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

## 工具

### add_mistake

新增错题到存储。

**参数：**
- `subject` (string): 学科
- `grade` (string): 年级
- `content` (string): 题目内容
- `userAnswer` (string): 用户答案
- `correctAnswer` (string): 正确答案
- `analysis` (string): 解析
- `tags` (string[]): 知识点标签
- `source` (string): 来源
- `type` (string): 题目类型
- `difficulty` (string): 难度

### get_due_reviews

获取今日待复习错题。

**参数：**
- `subject` (string, optional): 按学科筛选
- `grade` (string, optional): 按年级筛选

### update_mastery

更新错题掌握程度。

**参数：**
- `filePath` (string): 错题文件路径
- `mastery` (string): forgotten/fuzzy/remembered/mastered
- `answer` (string): 用户答案

### search_mistakes

搜索错题。

**参数：**
- `query` (string): 搜索关键词
- `subject` (string, optional): 学科筛选
- `limit` (number, optional): 返回数量

### get_statistics

获取错题统计。

**参数：**
- 无

## 注意事项

1. 只存错题/不会的题，做对的不要存入
2. 图片题目需先 OCR 识别文字
3. 复习间隔根据掌握程度自动计算
4. mastered 题目60天后抽查
