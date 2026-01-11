"""
AI Analyzer using Qwen models
"""

import asyncio
from typing import List, Optional
import structlog


logger = structlog.get_logger()


class MistakeAnalysis:
    """Analysis result for a mistake"""
    def __init__(
        self,
        error_type: str,
        confidence: float,
        insights: List[str],
        similar_questions: Optional[List[str]] = None
    ):
        self.error_type = error_type
        self.confidence = confidence
        self.insights = insights
        self.similar_questions = similar_questions or []


class AIAnalyzer:
    """AI analyzer using Qwen models for mistake classification and insights (Mock)"""

    def __init__(self):
        self.initialized = False

    async def _initialize_client(self):
        """Initialize AI client (mock)"""
        if not self.initialized:
            logger.info("Initializing AI analyzer (mock)")
            await asyncio.sleep(0.1)
            self.initialized = True
            logger.info("AI analyzer initialized successfully (mock)")

    async def analyze_mistake(self, ocr_text: str) -> MistakeAnalysis:
        """
        Analyze mistake text and provide classification and insights (mock)

        Args:
            ocr_text: Extracted text from image

        Returns:
            MistakeAnalysis with classification and insights
        """
        try:
            await self._initialize_client()

            if not ocr_text.strip():
                return MistakeAnalysis(
                    error_type="unknown",
                    confidence=0.0,
                    insights=["无法提取题目文本"]
                )

            logger.info("Analyzing mistake text (mock)", text_length=len(ocr_text))

            # Mock analysis based on text content
            if "解方程" in ocr_text or "方程" in ocr_text:
                error_type = "calculation"
                insights = [
                    "解方程时要注意运算顺序",
                    "检查计算过程中是否有符号错误",
                    "建议复习一元二次方程的解法"
                ]
            elif "概念" in ocr_text or "定义" in ocr_text:
                error_type = "conceptual"
                insights = [
                    "概念理解是基础，建议加强基础概念学习",
                    "可以通过画图或举例来帮助理解抽象概念",
                    "建议复习相关章节的基本概念"
                ]
            elif "读题" in ocr_text:
                error_type = "misreading"
                insights = [
                    "读题是解题的第一步，要仔细阅读题目条件",
                    "建议用笔圈出关键信息和已知条件",
                    "读完题目后可以尝试用自己的话重新表述"
                ]
            else:
                error_type = "other"
                insights = [
                    "这是一个综合性问题",
                    "建议分解成多个小问题逐步解决",
                    "检查解题思路是否正确"
                ]

            return MistakeAnalysis(
                error_type=error_type,
                confidence=0.8,
                insights=insights,
                similar_questions=[
                    "练习1: 解方程 x² - 4x + 3 = 0",
                    "练习2: 理解函数的概念和性质"
                ]
            )

        except Exception as e:
            logger.error("AI analysis failed", error=str(e))
            return MistakeAnalysis(
                error_type="unknown",
                confidence=0.0,
                insights=["AI分析暂时不可用"]
            )