import { z } from 'zod';
import * as fs from 'fs';
import * as path from 'path';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

const MistakesDir = './mistakes';

const SubjectMap: Record<string, string> = {
  math: '数学',
  chinese: '语文',
  english: '英语',
  physics: '物理',
  chemistry: '化学'
};

const GradeMap: Record<string, string> = {
  grade7: '初一',
  grade8: '初二',
  grade9: '初三'
};

function getMistakesDir(): string {
  return path.resolve(process.cwd(), MistakesDir);
}

function ensureDir(dir: string): void {
  if (!)) {
    fs.mkdirSync(dir, { recursive: truefs.existsSync(dir });
  }
}

function parseFrontmatter(content: string): Record<string, unknown> {
  const match = content.match(/^---\n([\s\S]*?)\n---/);
  if (!match) return {};

  const fm: Record<string, unknown> = {};
  for (const line of match[1].split('\n')) {
    const colonIdx = line.indexOf(':');
    if (colonIdx === -1) continue;
    const key = line.slice(0, colonIdx).trim();
    let value = line.slice(colonIdx + 1).trim();
    
    if (value === 'null') {
      fm[key] = null;
    } else if (value.startsWith('[') && value.endsWith(']')) {
      fm[key] = value.slice(1, -1).split(',').map(v => v.trim());
    } else {
      fm[key] = value;
    }
  }
  return fm;
}

function formatDate(date: Date): string {
  return date.toISOString().split('T')[0];
}

function addDays(date: Date, days: number): Date {
  const result = new Date(date);
  result.setDate(result.getDate() + days);
  return result;
}

function getIntervals(): number[] {
  return [1, 3, 7, 15, 30, 60, 90];
}

export const addMistake = {
  name: 'add_mistake',
  description: 'Add a new mistake question to the collection',
  parameters: z.object({
    subject: z.enum(['math', 'chinese', 'english', 'physics', 'chemistry']),
    grade: z.enum(['grade7', 'grade8', 'grade9']),
    content: z.string(),
    userAnswer: z.string().optional(),
    correctAnswer: z.string(),
    analysis: z.string(),
    tags: z.array(z.string()),
    source: z.enum(['homework', 'test', 'exam', 'practice']).default('practice'),
    type: z.enum(['choice', 'fill', 'answer', 'judgment', 'application']).default('answer'),
    difficulty: z.enum(['easy', 'medium', 'hard']).default('medium'),
  }),
  
  async run(params: {
    subject: string;
    grade: string;
    content: string;
    userAnswer?: string;
    correctAnswer: string;
    analysis: string;
    tags: string[];
    source?: string;
    type?: string;
    difficulty?: string;
  }) {
    const baseDir = getMistakesDir();
    const subjectDir = path.join(baseDir, params.subject);
    const gradeDir = path.join(subjectDir, params.grade);
    
    ensureDir(gradeDir);
    
    const today = formatDate(new Date());
    const existingFiles = fs.readdirSync(gradeDir).filter(f => f.startsWith(today));
    const nextNum = existingFiles.length + 1;
    const filename = `${today}-${String(nextNum).padStart(3, '0')}.md`;
    const filepath = path.join(gradeDir, filename);
    
    const intervals = getIntervals();
    const tomorrow = formatDate(addDays(new Date(), 1));
    
    const markdown = `---
subject: ${params.subject}
grade: ${params.grade}
date: ${today}
source: ${params.source}
type: ${params.type}
difficulty: ${params.difficulty}
tags: [${params.tags.join(', ')}]

review:
  count: 0
  last_review: null
  next_review: ${tomorrow}
  mastery: forgotten

ebb:
  stage: 0
  intervals: [${intervals.join(', ')}]
  last_mastered: null
---

# 错题记录

## 基本信息
- **学科**: ${SubjectMap[params.subject] || params.subject}
- **年级**: ${GradeMap[params.grade] || params.grade}
- **日期**: ${today}
- **来源**: ${params.source}
- **类型**: ${params.type}
- **难度**: ${params.difficulty}
- **知识点**: ${params.tags.join(', ')}

## 题目
${params.content}

## 你的答案
${params.userAnswer || '无'}

## 正确答案
${params.correctAnswer}

## 解析
${params.analysis}

## 复习记录
| 日期 | 掌握程度 | 备注 |
|------|----------|------|
| ${today} | forgotten | 首次记录 |
`;
    
    fs.writeFileSync(filepath, markdown, 'utf-8');
    
    // Update QMD index
    try {
      await execAsync('qmd update');
    } catch (e) {
      console.log('QMD update skipped');
    }
    
    return {
      success: true,
      filepath,
      message: `错题已保存到 ${SubjectMap[params.subject]}-${GradeMap[params.grade]}-${filename}`
    };
  }
};

export const getDueReviews = {
  name: 'get_due_reviews',
  description: 'Get mistakes due for review today',
  parameters: z.object({
    subject: z.enum(['math', 'chinese', 'english', 'physics', 'chemistry']).optional(),
    grade: z.enum(['grade7', 'grade8', 'grade9']).optional(),
  }),
  
  async run(params: { subject?: string; grade?: string }) {
    const baseDir = getMistakesDir();
    const today = formatDate(new Date());
    const due: Array<{
      file: string;
      subject: string;
      grade: string;
      tags: string[];
      mastery: string;
      next_review: string;
      count: number;
    }> = [];
    
    const subjects = params.subject ? [params.subject] : ['math', 'chinese', 'english', 'physics', 'chemistry'];
    
    for (const subject of subjects) {
      const subjectDir = path.join(baseDir, subject);
      if (!fs.existsSync(subjectDir)) continue;
      
      const grades = fs.readdirSync(subjectDir);
      for (const grade of grades) {
        if (params.grade && grade !== params.grade) continue;
        
        const gradeDir = path.join(subjectDir, grade);
        if (!fs.statSync(gradeDir).isDirectory()) continue;
        
        const files = fs.readdirSync(gradeDir).filter(f => f.endsWith('.md'));
        for (const file of files) {
          const filepath = path.join(gradeDir, file);
          const content = fs.readFileSync(filepath, 'utf-8');
          const fm = parseFrontmatter(content);
          
          const review = fm.review as Record<string, unknown> || {};
          const mastery = review.mastery as string || 'forgotten';
          const nextReview = review.next_review as string || '';
          
          // Skip mastered questions not due for spot check
          if (mastery === 'mastered') {
            const ebb = fm.ebb as Record<string, unknown> || {};
            const lastMastered = ebb.last_mastered as string | null;
            if (lastMastered) {
              const daysSince = Math.floor((new Date().getTime() - new Date(lastMastered).getTime()) / (1000 * 60 * 60 * 24));
              if (daysSince < 60) continue;
            }
          }
          
          if (nextReview && nextReview <= today) {
            due.push({
              file: filepath,
              subject,
              grade,
              tags: (fm.tags as string[]) || [],
              mastery,
              next_review: nextReview,
              count: (review.count as number) || 0
            });
          }
        }
      }
    }
    
    due.sort((a, b) => {
      const masteryOrder = { forgotten: 0, fuzzy: 1, remembered: 2, mastered: 3 };
      return (masteryOrder[a.mastery as keyof typeof masteryOrder] || 0) - 
             (masteryOrder[b.mastery as keyof typeof masteryOrder] || 0);
    });
    
    return {
      total: due.length,
      due: due.map(d => ({
        file: d.file,
        subject: SubjectMap[d.subject] || d.subject,
        grade: GradeMap[d.grade] || d.grade,
        tags: d.tags,
        mastery: d.mastery,
        review_count: d.count
      }))
    };
  }
};

export const updateMastery = {
  name: 'update_mastery',
  description: 'Update mastery level of a mistake after review',
  parameters: z.object({
    filePath: z.string(),
    mastery: z.enum(['forgotten', 'fuzzy', 'remembered', 'mastered']),
    answer: z.string().optional(),
  }),
  
  async run(params: { filePath: string; mastery: string; answer?: string }) {
    if (!fs.existsSync(params.filePath)) {
      return { success: false, error: '文件不存在' };
    }
    
    const content = fs.readFileSync(params.filePath, 'utf-8');
    const fm = parseFrontmatter(content);
    
    const review = fm.review as Record<string, unknown> || {};
    const ebb = fm.ebb as Record<string, unknown> || {};
    
    const oldMastery = review.mastery as string || 'forgotten';
    const oldCount = review.count as number || 0;
    const oldStage = ebb.stage as number || 0;
    const intervals = (ebb.intervals as number[]) || getIntervals();
    
    const today = formatDate(new Date());
    let newStage = oldStage;
    let nextReview: string;
    
    if (params.mastery === 'mastered') {
      newStage = oldStage;
      nextReview = formatDate(addDays(new Date(), 60));
      if (!ebb.last_mastered) {
        (ebb as Record<string, unknown>).last_mastered = today;
      }
    } else if (params.mastery === 'remembered') {
      newStage = Math.min(oldStage + 1, intervals.length - 1);
      nextReview = formatDate(addDays(new Date(), intervals[newStage]));
    } else {
      newStage = oldStage;
      nextReview = formatDate(addDays(new Date(), intervals[0]));
    }
    
    (review as Record<string, unknown>).count = oldCount + 1;
    (review as Record<string, unknown>).last_review = today;
    (review as Record<string, unknown>).next_review = nextReview;
    (review as Record<string, unknown>).mastery = params.mastery;
    (ebb as Record<string, unknown>).stage = newStage;
    
    // Update markdown
    const newContent = content.replace(
      /^---[\s\S]*?^---/m,
      `---
subject: ${fm.subject}
grade: ${fm.grade}
date: ${fm.date}
source: ${fm.source}
type: ${fm.type}
difficulty: ${fm.difficulty}
tags: ${JSON.stringify(fm.tags)}

review:
  count: ${review.count}
  last_review: ${review.last_review}
  next_review: ${review.next_review}
  mastery: ${review.mastery}

ebb:
  stage: ${ebb.stage}
  intervals: ${JSON.stringify(ebb.intervals)}
  last_mastered: ${ebb.last_mastered}
---`
    );
    
    // Add review record
    const masteryText = {
      forgotten: '忘记',
      fuzzy: '模糊', 
      remembered: '记住',
      mastered: '精通'
    }[params.mastery] || params.mastery;
    
    const newReviewRecord = `| ${today} | ${masteryText} | ${params.answer || ''} |`;
    const updatedContent = newContent.replace(
      /\| 日期 \| 掌握程度 \| 备注 \|/,
      `| 日期 | 掌握程度 | 备注 |\n${newReviewRecord}`
    );
    
    fs.writeFileSync(params.filePath, updatedContent, 'utf-8');
    
    return {
      success: true,
      message: `已更新掌握程度为 ${masteryText}，下次复习: ${nextReview}`,
      next_review: nextReview,
      stage: newStage
    };
  }
};

export const searchMistakes = {
  name: 'search_mistakes',
  description: 'Search mistakes using QMD or file search',
  parameters: z.object({
    query: z.string(),
    subject: z.enum(['math', 'chinese', 'english', 'physics', 'chemistry']).optional(),
    limit: z.number().default(10),
  }),
  
  async run(params: { query: string; subject?: string; limit?: number }) {
    const baseDir = getMistakesDir();
    
    // Try QMD first
    try {
      const subjectFilter = params.subject ? `-c ${params.subject}` : '-c mistakes';
      const { stdout } = await execAsync(
        `qmd search "${params.query}" ${subjectFilter} -n ${params.limit} --json 2>/dev/null`
      );
      
      if (stdout.trim()) {
        const results = JSON.parse(stdout);
        return {
          source: 'qmd',
          total: results.length,
          results: results.map((r: { title: string; path: string; score: number; snippet: string }) => ({
            title: r.title,
            path: r.path,
            score: r.score,
            snippet: r.snippet
          }))
        };
      }
    } catch (e) {
      console.log('QMD search failed, falling back to grep');
    }
    
    // Fallback to grep
    const results: Array<{ file: string; line: string }> = [];
    const subjects = params.subject ? [params.subject] : ['math', 'chinese', 'english', 'physics', 'chemistry'];
    
    for (const subject of subjects) {
      const subjectDir = path.join(baseDir, subject);
      if (!fs.existsSync(subjectDir)) continue;
      
      try {
        const { stdout } = await execAsync(
          `grep -r "${params.query}" "${subjectDir}" --include="*.md" -l | head -${params.limit}`
        );
        
        for (const file of stdout.trim().split('\n').filter(Boolean)) {
          results.push({ file, line: '' });
        }
      } catch (e) {
        // ignore
      }
    }
    
    return {
      source: 'grep',
      total: results.length,
      results: results.slice(0, params.limit)
    };
  }
};

export const getStatistics = {
  name: 'get_statistics',
  description: 'Get mistake statistics',
  parameters: z.object({}),
  
  async run() {
    const baseDir = getMistakesDir();
    
    const stats = {
      total: 0,
      by_subject: {} as Record<string, number>,
      by_grade: {} as Record<string, number>,
      by_mastery: { forgotten: 0, fuzzy: 0, remembered: 0, mastered: 0 },
      by_difficulty: { easy: 0, medium: 0, hard: 0 },
    };
    
    if (!fs.existsSync(baseDir)) {
      return stats;
    }
    
    const subjects = fs.readdirSync(baseDir);
    for (const subject of subjects) {
      const subjectDir = path.join(baseDir, subject);
      if (!fs.statSync(subjectDir).isDirectory()) continue;
      
      stats.by_subject[subject] = 0;
      const grades = fs.readdirSync(subjectDir);
      
      for (const grade of grades) {
        const gradeDir = path.join(subjectDir, grade);
        if (!fs.statSync(gradeDir).isDirectory()) continue;
        
        stats.by_grade[grade] = (stats.by_grade[grade] || 0) + 1;
        
        const files = fs.readdirSync(gradeDir).filter(f => f.endsWith('.md'));
        stats.by_subject[subject] += files.length;
        stats.total += files.length;
        
        for (const file of files) {
          const filepath = path.join(gradeDir, file);
          const content = fs.readFileSync(filepath, 'utf-8');
          const fm = parseFrontmatter(content);
          
          const review = fm.review as Record<string, unknown> || {};
          const mastery = review.mastery as string || 'forgotten';
          if (mastery in stats.by_mastery) {
            stats.by_mastery[mastery as keyof typeof stats.by_mastery]++;
          }
          
          const difficulty = fm.difficulty as string || 'medium';
          if (difficulty in stats.by_difficulty) {
            stats.by_difficulty[difficulty as keyof typeof stats.by_difficulty]++;
          }
        }
      }
    }
    
    return stats;
  }
};

export default {
  add_mistake: addMistake,
  get_due_reviews: getDueReviews,
  update_mastery: updateMastery,
  search_mistakes: searchMistakes,
  get_statistics: getStatistics,
};
