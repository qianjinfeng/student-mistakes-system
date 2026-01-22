#!/usr/bin/env python3
"""
Test script for AI analyzer
"""

import asyncio
import sys
import os
sys.path.append('/home/z0038h3f/workspace/student-mistakes-system/backend')

from services.ai_analyzer import AIAnalyzer

async def test_ai():
    try:
        analyzer = AIAnalyzer()
        # Test with a simple text analysis instead of image
        result = await analyzer.analyze_mistake("Test mistake analysis")
        print("AI Analyzer test successful:")
        print(f"Error type: {result.error_type}")
        print(f"Confidence: {result.confidence}")
        print(f"Insights: {result.insights}")
        return True
    except Exception as e:
        print(f"AI Analyzer test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_ai())
    sys.exit(0 if success else 1)