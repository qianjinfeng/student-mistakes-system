# 错题 Markdown 模板

## 完整模板

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
- **学科**: 数学
- **年级**: 初二
- **日期**: 2026-03-12
- **来源**: 作业
- **类型**: 应用题
- **难度**: 中等
- **知识点**: 勾股定理、几何计算

## 题目
已知直角三角形的两直角边分别为3和4，求斜边长。

## 你的答案
[无 / 答案内容]

## 错误原因
对勾股定理理解不深，未能正确应用公式

## 正确答案与解析
### 正确答案
斜边长为 5

### 详细步骤
1. 已知两直角边 a=3, b=4
2. 根据勾股定理: c² = a² + b²
3. c² = 3² + 4² = 9 + 16 = 25
4. c = √25 = 5
5. 斜边长为 5

### 知识点讲解
**勾股定理**：在直角三角形中，两直角边的平方和等于斜边的平方。
公式：a² + b² = c²
其中 a、b 为直角边，c 为斜边。

## 复习记录
| 日期 | 掌握程度 | 备注 |
|------|----------|------|
| 2026-03-12 | forgotten | 首次记录 |
```

## 字段说明

### YAML Frontmatter

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| subject | string | 学科 | math/chinese/english/physics/chemistry |
| grade | string | 年级 | grade7/grade8/grade9 |
| date | string | 错题日期 | 2026-03-12 |
| source | string | 来源 | homework/test/exam/practice |
| type | string | 题目类型 | choice/fill/answer/application |
| difficulty | string | 难度 | easy/medium/hard |
| tags | array | 知识点标签 | [勾股定理, 几何] |

### review 对象

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| count | number | 复习次数 | 0 |
| last_review | string/null | 上次复习日期 | 2026-03-12 |
| next_review | string | 下次复习日期 | 2026-03-13 |
| mastery | string | 掌握程度 | forgotten/fuzzy/remembered/mastered |

### ebb 对象

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| stage | number | 艾宾浩斯阶段 | 0 |
| intervals | array | 各阶段间隔天数 | [1,3,7,15,30,60,90] |
| last_mastered | string/null | 首次达到精通的日期 | null |

## subject 映射

| subject | 学科 |
|---------|------|
| math | 数学 |
| chinese | 语文 |
| english | 英语 |
| physics | 物理 |
| chemistry | 化学 |

## grade 映射

| grade | 年级 |
|-------|------|
| grade7 | 初一 |
| grade8 | 初二 |
| grade9 | 初三 |

## type 映射

| type | 题目类型 |
|------|----------|
| choice | 选择题 |
| fill | 填空题 |
| answer | 解答题 |
| judgment | 判断题 |
| application | 应用题 |

## difficulty 映射

| difficulty | 难度 |
|------------|------|
| easy | 简单 |
| medium | 中等 |
| hard | 困难 |

## mastery 说明

| mastery | 中文 | 说明 |
|---------|------|------|
| forgotten | 忘记 | 完全不会做，答错 |
| fuzzy | 模糊 | 会做但不确定 |
| remembered | 记住 | 正确且有把握 |
| mastered | 精通 | 完全掌握，滚瓜烂熟 |
