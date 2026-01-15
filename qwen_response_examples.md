# Qwen3-vl-plus Structured JSON Response Examples

## Example 1: Math Equation Error
```json
{
  "questions_found": ["解方程: x² + 5x + 6 = 0"],
  "correct_answers": ["x = -2 或 x = -3"],
  "error_type": "calculation",
  "confidence": 0.92,
  "root_cause": "学生在使用求根公式时，判别式计算正确（b²-4ac = 25-24 = 1），但在开方后的符号处理出现错误，误认为√1 = -1，导致最终答案符号相反。",
  "insights": [
    "求根公式中，√1 = 1，不是-1",
    "注意二次项系数为正时，两根之和等于-b/a，这里应该是-5，验证答案是否正确",
    "建议多做求根公式的练习，特别注意符号的处理",
    "可以用因式分解验证答案：(x+2)(x+3)=x²+5x+6"
  ],
  "similar_questions": [
    "练习1: 解方程 x² - 7x + 12 = 0",
    "练习2: 解方程 2x² + 8x + 6 = 0"
  ]
}
```

## Example 2: Geometry Concept Error
```json
{
  "questions_found": ["已知三角形ABC中，∠A = 60°，∠B = 80°，求∠C的度数"],
  "correct_answers": ["∠C = 40°"],
  "error_type": "conceptual",
  "confidence": 0.88,
  "root_cause": "学生忘记了三角形内角和定理，即三角形三个内角的和等于180°。这是一个基本几何概念，需要加强理解。",
  "insights": [
    "牢记三角形内角和定理：∠A + ∠B + ∠C = 180°",
    "可以通过画图和实际测量来加深理解",
    "建议多做不同类型三角形的内角计算练习",
    "可以记忆特殊三角形的内角组合，如等边三角形(60°,60°,60°)"
  ],
  "similar_questions": [
    "练习1: 等腰三角形中，已知顶角为40°，求底角的度数",
    "练习2: 直角三角形中，已知一个锐角为35°，求另一个锐角"
  ]
}
```

## Example 3: Reading Comprehension Error
```json
{
  "questions_found": ["题目：小明有10个苹果，给了小红3个，又买了5个，请问小明现在有多少个苹果？"],
  "correct_answers": ["12个苹果"],
  "error_type": "misreading",
  "confidence": 0.85,
  "root_cause": "学生没有仔细阅读题目，忽略了'又买了5个'这个条件，只计算了10-3=7，遗漏了后续的加法运算。",
  "insights": [
    "读题时要圈出关键数字和操作词",
    "建议用笔标记每个条件的含义",
    "可以按照题目顺序逐步列出计算过程",
    "养成检查答案是否符合题目所有条件的习惯"
  ],
  "similar_questions": [
    "练习1: 小华有15本书，借给同学4本，又买了3本，现在有多少本？",
    "练习2: 停车场有20辆车，开走了8辆，又开来了6辆，现在有多少辆？"
  ]
}
```

## Key Features of Structured Output:

1. **questions_found**: 准确识别图片中的题目
2. **correct_answers**: 提供正确的解题答案
3. **error_type**: 标准化错误类型（calculation/conceptual/misreading/other）
4. **confidence**: AI分析的置信度（0.0-1.0）
5. **root_cause**: 详细具体的错误原因分析
6. **insights**: 可操作的学习建议（3-4条）
7. **similar_questions**: 相关的练习题推荐（2-3道）

这种结构化输出确保了：
- ✅ 数据的一致性和可靠性
- ✅ 前端展示的美观性和可读性
- ✅ 数据库存储的规范性
- ✅ API响应的标准化