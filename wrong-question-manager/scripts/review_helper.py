#!/usr/bin/env python3
"""
错题复习辅助脚本
用于查找待复习错题、更新掌握程度
"""

import os
import re
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional

MISTAKES_DIR = Path("mistakes")

SUBJECT_MAP = {
    "math": "数学",
    "chinese": "语文", 
    "english": "英语",
    "physics": "物理",
    "chemistry": "化学"
}

GRADE_MAP = {
    "grade7": "初一",
    "grade8": "初二",
    "grade9": "初三"
}

MASTERY_MAP = {
    "forgotten": "忘记",
    "fuzzy": "模糊",
    "remembered": "记住",
    "mastered": "精通"
}


def parse_frontmatter(content: str) -> Dict:
    """解析 YAML frontmatter"""
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return {}
    
    frontmatter = {}
    for line in match.group(1).split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            
            if value.startswith('[') and value.endswith(']'):
                frontmatter[key] = [v.strip() for v in value[1:-1].split(',')]
            elif value == 'null':
                frontmatter[key] = None
            else:
                frontmatter[key] = value
    
    return frontmatter


def get_all_mistakes() -> List[Dict]:
    """获取所有错题"""
    mistakes = []
    
    if not MISTAKES_DIR.exists():
        return mistakes
    
    for subject_dir in MISTAKES_DIR.iterdir():
        if not subject_dir.is_dir():
            continue
        
        subject = subject_dir.name
        
        for grade_dir in subject_dir.iterdir():
            if not grade_dir.is_dir():
                continue
            
            grade = grade_dir.name
            
            for md_file in grade_dir.glob("*.md"):
                content = md_file.read_text(encoding='utf-8')
                fm = parse_frontmatter(content)
                
                mistakes.append({
                    "file": str(md_file),
                    "subject": subject,
                    "grade": grade,
                    "date": fm.get("date"),
                    "source": fm.get("source"),
                    "type": fm.get("type"),
                    "difficulty": fm.get("difficulty"),
                    "tags": fm.get("tags", []),
                    "review": fm.get("review", {}),
                    "ebb": fm.get("ebb", {})
                })
    
    return mistakes


def get_due_reviews(target_date: str = None) -> List[Dict]:
    """获取指定日期需要复习的错题"""
    if target_date is None:
        target_date = datetime.now().strftime("%Y-%m-%d")
    
    all_mistakes = get_all_mistakes()
    due = []
    
    for m in all_mistakes:
        next_review = m.get("review", {}).get("next_review")
        mastery = m.get("review", {}).get("mastery", "forgotten")
        
        # mastered 且不是抽查时间的不需要复习
        if mastery == "mastered":
            ebb = m.get("ebb", {})
            last_mastered = ebb.get("last_mastered")
            if last_mastered:
                last_mastered_date = datetime.strptime(last_mastered, "%Y-%m-%d")
                days_since = (datetime.now() - last_mastered_date).days
                # 60天抽查一次
                if days_since < 60:
                    continue
        
        if next_review and next_review <= target_date:
            due.append(m)
    
    return sorted(due, key=lambda x: x.get("date", ""))


def get_today_reviews() -> List[Dict]:
    """获取今日待复习"""
    today = datetime.now().strftime("%Y-%m-%d")
    return get_due_reviews(today)


def update_mastery(file_path: str, mastery: str, count: int = None) -> bool:
    """更新错题的掌握程度"""
    try:
        content = Path(file_path).read_text(encoding='utf-8')
        fm = parse_frontmatter(content)
        
        review = fm.get("review", {})
        ebb = fm.get("ebb", {})
        
        today = datetime.now().strftime("%Y-%m-%d")
        intervals = ebb.get("intervals", [1, 3, 7, 15, 30, 60, 90])
        
        old_mastery = review.get("mastery", "forgotten")
        old_count = review.get("count", 0)
        old_stage = ebb.get("stage", 0)
        
        # 更新复习次数
        if count is not None:
            new_count = count
        else:
            new_count = old_count + 1
        
        # 计算下次复习日期
        if mastery == "mastered":
            new_stage = old_stage
            next_review_date = datetime.now() + timedelta(days=60)
            if not ebb.get("last_mastered"):
                ebb["last_mastered"] = today
        elif mastery == "remembered":
            new_stage = min(old_stage + 1, len(intervals) - 1)
            next_review_date = datetime.now() + timedelta(days=intervals[new_stage])
        else:
            # forgotten 或 fuzzy 保持在当前阶段
            new_stage = old_stage
            next_review_date = datetime.now() + timedelta(days=intervals[0])
        
        # 更新 review
        review["count"] = new_count
        review["last_review"] = today
        review["next_review"] = next_review_date.strftime("%Y-%m-%d")
        review["mastery"] = mastery
        
        # 更新 ebb
        ebb["stage"] = new_stage
        
        # 重新生成文件内容
        new_frontmatter = f"""subject: {fm.get('subject')}
grade: {fm.get('grade')}
date: {fm.get('date')}
source: {fm.get('source')}
type: {fm.get('type')}
difficulty: {fm.get('difficulty')}
tags: {fm.get('tags', [])}

review:
  count: {review['count']}
  last_review: {review['last_review']}
  next_review: {review['next_review']}
  mastery: {review['mastery']}

ebb:
  stage: {ebb['stage']}
  intervals: {intervals}
  last_mastered: {ebb.get('last_mastered')}"""
        
        new_content = content.replace(re.match(r'^---.*?^---', content, re.DOTALL).group(0), 
                                      f"---\n{new_frontmatter}\n---", 1)
        
        Path(file_path).write_text(new_content, encoding='utf-8')
        return True
    
    except Exception as e:
        print(f"更新失败: {e}")
        return False


def get_statistics() -> Dict:
    """获取错题统计"""
    all_mistakes = get_all_mistakes()
    
    stats = {
        "total": len(all_mistakes),
        "by_subject": {},
        "by_grade": {},
        "by_mastery": {"forgotten": 0, "fuzzy": 0, "remembered": 0, "mastered": 0},
        "due_today": len(get_today_reviews())
    }
    
    for m in all_mistakes:
        subject = m.get("subject", "unknown")
        grade = m.get("grade", "unknown")
        mastery = m.get("review", {}).get("mastery", "forgotten")
        
        stats["by_subject"][subject] = stats["by_subject"].get(subject, 0) + 1
        stats["by_grade"][grade] = stats["by_grade"].get(grade, 0) + 1
        stats["by_mastery"][mastery] = stats["by_mastery"].get(mastery, 0) + 1
    
    return stats


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="错题复习辅助工具")
    parser.add_argument("command", choices=["due", "stats", "update"],
                        help="命令: due-待复习, stats-统计, update-更新")
    parser.add_argument("--file", help="错题文件路径")
    parser.add_argument("--mastery", choices=["forgotten", "fuzzy", "remembered", "mastered"],
                        help="掌握程度")
    parser.add_argument("--count", type=int, help="复习次数")
    
    args = parser.parse_args()
    
    if args.command == "due":
        reviews = get_today_reviews()
        print(f"今日待复习 ({len(reviews)}道):\n")
        for i, r in enumerate(reviews, 1):
            print(f"{i}. [{SUBJECT_MAP.get(r['subject'], r['subject'])}-{GRADE_MAP.get(r['grade'], r['grade'])}] {r.get('tags', [])[0] if r.get('tags') else ''}")
            print(f"   掌握程度: {MASTERY_MAP.get(r['review'].get('mastery'), r['review'].get('mastery'))}")
            print(f"   复习次数: {r['review'].get('count', 0)}")
            print()
    
    elif args.command == "stats":
        stats = get_statistics()
        print("错题统计:")
        print(f"  总数: {stats['total']}")
        print(f"  今日待复习: {stats['due_today']}")
        print("\n按学科:")
        for k, v in stats["by_subject"].items():
            print(f"  {SUBJECT_MAP.get(k, k)}: {v}")
        print("\n按年级:")
        for k, v in stats["by_grade"].items():
            print(f"  {GRADE_MAP.get(k, k)}: {v}")
        print("\n按掌握程度:")
        for k, v in stats["by_mastery"].items():
            print(f"  {MASTERY_MAP.get(k, k)}: {v}")
    
    elif args.command == "update":
        if not args.file or not args.mastery:
            print("请指定 --file 和 --mastery")
            return
        
        success = update_mastery(args.file, args.mastery, args.count)
        if success:
            print(f"已更新 {args.file}")
        else:
            print("更新失败")


if __name__ == "__main__":
    main()
