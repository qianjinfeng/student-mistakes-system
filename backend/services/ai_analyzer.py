"""
AI Analyzer using Qwen3-vl-plus vision models for direct image analysis and mistake classification
"""

import asyncio
import json
from typing import List, Optional
from pathlib import Path
import structlog
from PIL import Image
import base64
import io
import os
import dashscope
from config.settings import settings


logger = structlog.get_logger()


class MistakeAnalysis:
    """Analysis result for a mistake"""
    def __init__(
        self,
        error_type: str,
        confidence: float,
        insights: List[str],
        questions_found: List[str] = None,
        correct_answers: List[str] = None,
        root_cause: str = None,
        similar_questions: Optional[List[str]] = None
    ):
        self.error_type = error_type
        self.confidence = confidence
        self.insights = insights
        self.questions_found = questions_found or []
        self.correct_answers = correct_answers or []
        self.root_cause = root_cause
        self.similar_questions = similar_questions or []


class AIAnalyzer:
    """AI analyzer using Qwen3-vl-plus vision model for direct image analysis and mistake classification"""

    def __init__(self):
        self.initialized = False
        self.api_key = None

    async def _initialize_client(self):
        """Initialize Qwen vision client"""
        if not self.initialized:
            logger.info("Initializing Qwen3-vl-plus analyzer")
            
            # Set up DashScope API
            dashscope.base_http_api_url = settings.ai.qwen_base_url
            self.api_key = settings.ai.qwen_api_key.get_secret_value() if settings.ai.qwen_api_key else os.getenv('DASHSCOPE_API_KEY')
            
            if not self.api_key:
                logger.error("DASHSCOPE_API_KEY not configured")
                raise ValueError("DASHSCOPE_API_KEY environment variable or qwen_api_key setting is required")
            
            self.initialized = True
            logger.info("Qwen3-vl-plus analyzer initialized successfully")

    def _encode_image_to_base64(self, image_path: str) -> str:
        """Encode image to base64 for Qwen API"""
        try:
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Resize if too large (Qwen has size limits)
                max_size = (1024, 1024)
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                # Convert to base64
                buffered = io.BytesIO()
                img.save(buffered, format="JPEG")
                return base64.b64encode(buffered.getvalue()).decode('utf-8')
        except Exception as e:
            logger.error("Failed to encode image", image_path=image_path, error=str(e))
            raise

    def _parse_qwen_response(self, response_text: str) -> dict:
        """Parse Qwen JSON response into structured analysis"""
        # Clean and validate input
        if not response_text or not response_text.strip():
            logger.error("Empty response received from Qwen")
            return self._create_fallback_analysis("响应为空", "Qwen返回空响应")
        
        response_text = response_text.strip()
        
        try:
            # Try to extract JSON from the response (in case it's wrapped in markdown or other text)
            json_text = self._extract_json_from_response(response_text)
            
            if not json_text:
                logger.error("No JSON found in response", response_text=response_text[:200])
                return self._create_fallback_analysis("JSON提取失败", "响应中未找到有效的JSON")
            
            # Parse JSON response (Qwen3-vl-plus with response_format='json_object')
            analysis_data = json.loads(json_text)
            
            # Validate and normalize the response
            normalized_analysis = {
                "questions_found": self._ensure_list(analysis_data.get("questions_found", [])),
                "correct_answers": self._ensure_list(analysis_data.get("correct_answers", [])),
                "error_type": self._validate_error_type(analysis_data.get("error_type", "other")),
                "confidence": self._validate_confidence(analysis_data.get("confidence", 0.7)),
                "root_cause": self._ensure_string(analysis_data.get("root_cause", "未提供根本原因分析")),
                "insights": self._ensure_list(analysis_data.get("insights", [])),
                "similar_questions": self._ensure_list(analysis_data.get("similar_questions", []))
            }
            
            logger.info("Successfully parsed Qwen JSON response", 
                       error_type=normalized_analysis["error_type"],
                       confidence=normalized_analysis["confidence"])
            
            return normalized_analysis
            
        except json.JSONDecodeError as e:
            logger.error("JSON parsing failed", 
                       error=str(e), 
                       response_preview=response_text[:300],
                       response_length=len(response_text))
            return self._create_fallback_analysis("JSON解析失败", f"解析错误: {str(e)}")
        except Exception as e:
            logger.error("Failed to parse Qwen response", error=str(e))
            return self._create_fallback_analysis("响应解析失败", str(e))

    def _extract_json_from_response(self, response_text: str) -> str:
        """Extract JSON from response, handling various formats"""
        try:
            # Case 1: Direct JSON
            if response_text.startswith('{') and response_text.endswith('}'):
                return response_text
            
            # Case 2: JSON in markdown code blocks
            if '```json' in response_text:
                start = response_text.find('```json') + 7
                end = response_text.find('```', start)
                if end > start:
                    return response_text[start:end].strip()
            
            # Case 3: JSON in code blocks without language
            if '```' in response_text:
                start = response_text.find('```') + 3
                end = response_text.find('```', start)
                if end > start:
                    json_candidate = response_text[start:end].strip()
                    if json_candidate.startswith('{'):
                        return json_candidate
            
            # Case 4: Find JSON object boundaries
            start_idx = response_text.find('{')
            if start_idx == -1:
                return ""
            
            # Find matching closing brace
            brace_count = 0
            end_idx = -1
            for i in range(start_idx, len(response_text)):
                if response_text[i] == '{':
                    brace_count += 1
                elif response_text[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end_idx = i + 1
                        break
            
            if end_idx > start_idx:
                return response_text[start_idx:end_idx]
            
            return ""
            
        except Exception as e:
            logger.error("Failed to extract JSON from response", error=str(e))
            return ""

    def _ensure_list(self, value) -> list:
        """Ensure value is a list"""
        if value is None:
            return []
        if isinstance(value, list):
            return [str(item) for item in value if item is not None]
        if isinstance(value, str):
            return [value]
        return [str(value)]

    def _ensure_string(self, value) -> str:
        """Ensure value is a string"""
        if value is None:
            return ""
        return str(value)

    def _validate_error_type(self, error_type: str) -> str:
        """Validate error_type is one of allowed values"""
        valid_types = {"calculation", "conceptual", "misreading", "other"}
        error_type = str(error_type).lower()
        return error_type if error_type in valid_types else "other"

    def _validate_confidence(self, confidence) -> float:
        """Validate confidence is between 0.0 and 1.0"""
        try:
            conf = float(confidence)
            return max(0.0, min(1.0, conf))
        except (ValueError, TypeError):
            return 0.7

    def _create_fallback_analysis(self, error_msg: str, details: str = "") -> dict:
        """Create fallback analysis when parsing fails"""
        return {
            "questions_found": ["解析失败"],
            "correct_answers": [],
            "error_type": "unknown",
            "confidence": 0.0,
            "root_cause": f"AI响应解析失败: {error_msg}",
            "insights": [f"请重试或联系技术支持。错误详情: {details}"],
            "similar_questions": []
        }

    async def analyze_image(self, image_path: str) -> MistakeAnalysis:
        """
        Analyze image directly with Qwen3-vl-plus to segment questions, analyze correctness, and identify root causes

        Args:
            image_path: Path to image file

        Returns:
            MistakeAnalysis with detailed question analysis, correctness evaluation, and root cause analysis
        """
        try:
            await self._initialize_client()
            
            if not Path(image_path).exists():
                return MistakeAnalysis(
                    error_type="unknown",
                    confidence=0.0,
                    insights=["图像文件不存在"],
                    questions_found=[],
                    correct_answers=[],
                    root_cause="无法访问图像文件"
                )

            logger.info("Analyzing image with Qwen3-vl-plus", image_path=image_path)

            # Encode image to base64
            image_base64 = self._encode_image_to_base64(image_path)

            # Prepare messages for Qwen API with system prompt
            system_prompt = """你是一个专业的教育AI助手，专门分析学生错题图片。请仔细分析图片中的错题，并以JSON格式返回结构化结果。

分析要求：
1. 识别图片中的所有题目
2. 判断学生答案的正确性
3. 分析错误类型（必须是以下之一：calculation/conceptual/misreading/other）
4. 深入分析错误的根本原因
5. 提供3-4条具体的学习建议
6. 推荐2-3道类似的练习题

JSON输出格式：
{
  "questions_found": ["题目1", "题目2"],
  "correct_answers": ["正确答案1", "正确答案2"],
  "error_type": "calculation/conceptual/misreading/other",
  "confidence": 0.85,
  "root_cause": "详细说明错误根本原因，要具体、准确",
  "insights": ["建议1", "建议2", "建议3"],
  "similar_questions": ["类似练习题1", "类似练习题2"]
}

注意：
- error_type 必须是：calculation（计算错误）、conceptual（概念错误）、misreading（读题错误）、other（其他错误）
- confidence 是分析的置信度，范围0.0-1.0
- 如果图片中没有明显错误，confidence应该较低
- root_cause 要具体说明为什么出错
- insights 要提供可操作的学习建议
- similar_questions 要提供相关的练习题目"""

            user_prompt = "请分析这张学生错题图片，提取题目、答案，分析错误类型和根本原因，并提供学习建议和类似练习题。请严格按照指定的JSON格式返回结果。"

            messages = [
                {
                    "role": "system",
                    "content": [{"text": system_prompt}]
                },
                {
                    "role": "user",
                    "content": [
                        {"image": f"data:image/jpeg;base64,{image_base64}"},
                        {"text": user_prompt}
                    ]
                }
            ]

            # Call Qwen3-vl-plus API with structured JSON response and retry logic
            max_retries = 3
            response = None
            
            for attempt in range(max_retries):
                try:
                    response = dashscope.MultiModalConversation.call(
                        api_key=self.api_key,
                        model='qwen3-vl-plus',
                        messages=messages,
                        response_format={'type': 'json_object'}
                    )
                    break  # Success, exit retry loop
                except Exception as api_error:
                    if attempt == max_retries - 1:
                        logger.error("All Qwen API retry attempts failed", error=str(api_error))
                        return MistakeAnalysis(
                            error_type="unknown",
                            confidence=0.0,
                            insights=["AI服务连接失败，请稍后重试"],
                            questions_found=[],
                            correct_answers=[],
                            root_cause="网络连接或API服务问题"
                        )
                    logger.warning(f"Qwen API call failed, retrying ({attempt + 1}/{max_retries})", error=str(api_error))
                    await asyncio.sleep(1 * (attempt + 1))  # Exponential backoff

            # Check if we got a valid response
            if not response or response.status_code != 200:
                error_msg = getattr(response, 'message', 'Unknown API error') if response else 'No response received'
                status_code = getattr(response, 'status_code', 'N/A') if response else 'N/A'
                logger.error("Qwen API call failed", status_code=status_code, message=error_msg)
                return MistakeAnalysis(
                    error_type="unknown",
                    confidence=0.0,
                    insights=[f"AI分析失败: {error_msg}"],
                    questions_found=[],
                    correct_answers=[],
                    root_cause="AI服务暂时不可用"
                )

            # Extract JSON response with error handling
            try:
                json_string = response.output.choices[0].message.content[0]["text"]
                logger.info("Qwen JSON response received", response_length=len(json_string))
                
                # Log the raw response for debugging
                logger.debug("Raw Qwen response", json_string=json_string[:500])
                
            except (KeyError, IndexError, TypeError) as e:
                logger.error("Failed to extract JSON from Qwen response", error=str(e))
                return MistakeAnalysis(
                    error_type="unknown",
                    confidence=0.0,
                    insights=["AI响应格式错误"],
                    questions_found=[],
                    correct_answers=[],
                    root_cause="API返回数据格式不正确"
                )

            # Parse JSON response
            analysis_data = self._parse_qwen_response(json_string)

            return MistakeAnalysis(
                error_type=analysis_data["error_type"],
                confidence=analysis_data["confidence"],
                insights=analysis_data["insights"],
                questions_found=analysis_data["questions_found"],
                correct_answers=analysis_data["correct_answers"],
                root_cause=analysis_data["root_cause"],
                similar_questions=analysis_data["similar_questions"]
            )

        except Exception as e:
            logger.error("Qwen vision analysis failed", error=str(e))
            return MistakeAnalysis(
                error_type="unknown",
                confidence=0.0,
                insights=["视觉分析暂时不可用"],
                questions_found=[],
                correct_answers=[],
                root_cause="分析服务暂时不可用"
            )

    # Keep the old method for backward compatibility during transition
    async def analyze_mistake(self, ocr_text: str) -> MistakeAnalysis:
        """Legacy method - redirects to image analysis with warning"""
        logger.warning("Using deprecated analyze_mistake method, consider migrating to analyze_image")
        
        if not ocr_text.strip():
            return MistakeAnalysis(
                error_type="unknown",
                confidence=0.0,
                insights=["无法分析文本内容"],
                questions_found=[],
                correct_answers=[],
                root_cause="文本为空"
            )

        # Simple text-based analysis as fallback
        if "解方程" in ocr_text or "方程" in ocr_text:
            error_type = "calculation"
            insights = ["方程求解相关问题"]
        elif "概念" in ocr_text or "定义" in ocr_text:
            error_type = "conceptual"
            insights = ["概念理解相关问题"]
        else:
            error_type = "other"
            insights = ["综合性问题"]

        return MistakeAnalysis(
            error_type=error_type,
            confidence=0.7,
            insights=insights,
            questions_found=[ocr_text[:100] + "..."],
            correct_answers=[],
            root_cause="基于文本的简单分析",
            similar_questions=["建议使用图像分析获得更准确结果"]
        )