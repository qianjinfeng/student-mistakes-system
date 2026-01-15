#!/usr/bin/env python3
"""
Test script for JSON parsing improvements
"""

import json
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

def test_json_parsing():
    """Test various JSON parsing scenarios"""
    
    from services.ai_analyzer import AIAnalyzer
    
    analyzer = AIAnalyzer()
    
    # Test cases
    test_cases = [
        # Case 1: Valid JSON
        '{"questions_found": ["Q1"], "correct_answers": ["A1"], "error_type": "calculation", "confidence": 0.8, "root_cause": "test", "insights": ["test"], "similar_questions": ["test"]}',
        
        # Case 2: JSON in markdown
        '```json\n{"questions_found": ["Q1"], "correct_answers": ["A1"], "error_type": "calculation", "confidence": 0.8, "root_cause": "test", "insights": ["test"], "similar_questions": ["test"]}\n```',
        
        # Case 3: Malformed JSON
        '{"questions_found": ["Q1", "correct_answers": ["A1"], "error_type": "calculation", "confidence": 0.8, "root_cause": "test", "insights": ["test"], "similar_questions": ["test"]}',
        
        # Case 4: Empty response
        '',
        
        # Case 5: JSON with extra text
        'Here is the analysis:\n{"questions_found": ["Q1"], "correct_answers": ["A1"], "error_type": "calculation", "confidence": 0.8, "root_cause": "test", "insights": ["test"], "similar_questions": ["test"]}\nEnd of analysis.'
    ]
    
    for i, test_input in enumerate(test_cases):
        print(f"\n--- Test Case {i + 1} ---")
        print(f"Input: {test_input[:100]}...")
        
        try:
            result = analyzer._parse_qwen_response(test_input)
            print(f"✅ Parsed successfully:")
            print(f"   Error type: {result.get('error_type')}")
            print(f"   Confidence: {result.get('confidence')}")
            print(f"   Questions: {result.get('questions_found')}")
            print(f"   Root cause: {result.get('root_cause')}")
            
        except Exception as e:
            print(f"❌ Parse failed: {e}")
    
    print(f"\n--- JSON Extraction Test ---")
    
    # Test JSON extraction specifically
    extraction_test_cases = [
        '{"a": 1, "b": 2}',
        '```json\n{"a": 1, "b": 2}\n```',
        'Text before {"a": 1, "b": 2} text after',
        '{"nested": {"inner": {"value": 42}}}',
        '{"unclosed": {"inner": "value"}'
    ]
    
    for i, test_input in enumerate(extraction_test_cases):
        print(f"\nExtraction Test {i + 1}: {test_input}")
        extracted = analyzer._extract_json_from_response(test_input)
        print(f"Extracted: {extracted}")
        
        if extracted:
            try:
                parsed = json.loads(extracted)
                print(f"✅ Valid JSON: {parsed}")
            except json.JSONDecodeError as e:
                print(f"❌ Invalid JSON: {e}")

if __name__ == "__main__":
    test_json_parsing()