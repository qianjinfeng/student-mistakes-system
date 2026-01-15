#!/usr/bin/env python3
"""
Test script for Qwen3-vl-plus integration
"""

import asyncio
import os
from pathlib import Path
import sys

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from services.ai_analyzer import AIAnalyzer

async def test_qwen_integration():
    """Test Qwen3-vl-plus integration with a sample image"""
    
    # Check for API key
    api_key = os.getenv('DASHSCOPE_API_KEY')
    if not api_key:
        print("❌ Error: DASHSCOPE_API_KEY environment variable not set")
        print("Please set it with: export DASHSCOPE_API_KEY=your_api_key")
        return
    
    print("✅ DASHSCOPE_API_KEY found")
    
    # Initialize analyzer
    analyzer = AIAnalyzer()
    
    # Test with a mock image path (this will fail file existence but test initialization)
    test_image_path = "/tmp/test_equation.jpg"
    
    try:
        result = await analyzer.analyze_image(test_image_path)
        print(f"✅ Analyzer initialized successfully")
        print(f"📊 Result error type: {result.error_type}")
        print(f"📊 Result confidence: {result.confidence}")
        print(f"📝 Questions found: {result.questions_found}")
        print(f"✅ Correct answers: {result.correct_answers}")
        print(f"💡 Insights: {result.insights}")
        print(f"❌ Root cause: {result.root_cause}")
        print(f"📚 Similar questions: {result.similar_questions}")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        return
    
    print("✅ Qwen3-vl-plus integration test completed")

if __name__ == "__main__":
    asyncio.run(test_qwen_integration())