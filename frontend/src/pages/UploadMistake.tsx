import React, { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'

interface MistakeAnalysis {
  error_type: string
  confidence: number
  insights: string[]
  similar_questions?: string[]
}

interface UploadResponse {
  mistake: {
    id: string
    error_type?: string
    confidence?: number
    ai_insights?: any
  }
  analysis: MistakeAnalysis
  points_awarded: number
}

const UploadMistake = () => {
  const [uploading, setUploading] = useState(false)
  const [result, setResult] = useState<UploadResponse | null>(null)
  const [error, setError] = useState('')
  const [subject, setSubject] = useState('')

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0]
    if (!file) return

    setUploading(true)
    setError('')
    setResult(null)

    try {
      const formData = new FormData()
      formData.append('file', file)
      if (subject) {
        formData.append('subject', subject)
      }

      const response = await fetch('/api/mistakes/upload', {
        method: 'POST',
        body: formData
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || '上传失败')
      }

      const data: UploadResponse = await response.json()
      setResult(data)

    } catch (err) {
      setError(err instanceof Error ? err.message : '上传过程中发生错误')
    } finally {
      setUploading(false)
    }
  }, [subject])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg']
    },
    maxSize: 5 * 1024 * 1024, // 5MB
    multiple: false
  })

  const resetForm = () => {
    setResult(null)
    setError('')
    setSubject('')
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">上传错题</h1>
        <p className="text-gray-600">上传您的错题图片，我们将为您分析错误类型并提供学习建议</p>
      </div>

      {!result && (
        <div className="space-y-6">
          <div>
            <label htmlFor="subject" className="block text-sm font-medium text-gray-700 mb-2">
              科目（可选）
            </label>
            <select
              id="subject"
              value={subject}
              onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setSubject(e.target.value)}
              className="block w-full max-w-xs px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">选择科目</option>
              <option value="math">数学</option>
              <option value="physics">物理</option>
              <option value="chemistry">化学</option>
              <option value="biology">生物</option>
              <option value="chinese">语文</option>
              <option value="english">英语</option>
              <option value="history">历史</option>
              <option value="geography">地理</option>
              <option value="other">其他</option>
            </select>
          </div>

          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
              isDragActive
                ? 'border-blue-400 bg-blue-50'
                : 'border-gray-300 hover:border-gray-400'
            }`}
          >
            <input {...getInputProps()} />
            <div className="space-y-4">
              <div className="mx-auto w-12 h-12 text-gray-400">
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
              </div>
              {uploading ? (
                <div>
                  <p className="text-lg font-medium text-gray-900">正在分析题目...</p>
                  <p className="text-sm text-gray-500">请稍等，我们正在处理您的图片</p>
                </div>
              ) : isDragActive ? (
                <div>
                  <p className="text-lg font-medium text-blue-600">松开鼠标上传图片</p>
                  <p className="text-sm text-gray-500">支持 PNG、JPG 格式，大小不超过 5MB</p>
                </div>
              ) : (
                <div>
                  <p className="text-lg font-medium text-gray-900">拖拽图片到此处，或点击选择文件</p>
                  <p className="text-sm text-gray-500">支持 PNG、JPG 格式，大小不超过 5MB</p>
                </div>
              )}
            </div>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-md p-4">
              <div className="flex">
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-red-800">上传失败</h3>
                  <div className="mt-2 text-sm text-red-700">
                    <p>{error}</p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {result && (
        <div className="space-y-6">
          <div className="bg-green-50 border border-green-200 rounded-md p-6">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-green-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-green-800">分析完成！</h3>
                <div className="mt-2 text-sm text-green-700">
                  <p>已获得 {result.points_awarded} 积分</p>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">AI 分析结果</h3>
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <span className="text-sm font-medium text-gray-500">错误类型：</span>
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ml-2 ${
                    result.analysis.error_type === 'conceptual' ? 'bg-red-100 text-red-800' :
                    result.analysis.error_type === 'calculation' ? 'bg-yellow-100 text-yellow-800' :
                    result.analysis.error_type === 'misreading' ? 'bg-blue-100 text-blue-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {result.analysis.error_type === 'conceptual' ? '概念错误' :
                     result.analysis.error_type === 'calculation' ? '计算错误' :
                     result.analysis.error_type === 'misreading' ? '读题错误' : '其他错误'}
                  </span>
                </div>

                <div>
                  <span className="text-sm font-medium text-gray-500">分析置信度：</span>
                  <span className="text-sm text-gray-900 ml-2">
                    {Math.round(result.analysis.confidence * 100)}%
                  </span>
                </div>
              </div>

              {result.mistake.ai_insights && result.mistake.ai_insights.root_cause && (
                <div>
                  <span className="text-sm font-medium text-gray-500 block mb-2">错误根本原因：</span>
                  <p className="text-sm text-gray-700 bg-gray-50 rounded p-3">
                    {result.mistake.ai_insights.root_cause}
                  </p>
                </div>
              )}

              <div>
                <span className="text-sm font-medium text-gray-500 block mb-2">学习建议：</span>
                <ul className="space-y-2">
                  {result.analysis.insights.map((insight: string, index: number) => (
                    <li key={index} className="text-sm text-gray-700 flex items-start bg-blue-50 rounded p-3">
                      <span className="text-blue-500 mr-2 mt-0.5">💡</span>
                      {insight}
                    </li>
                  ))}
                </ul>
              </div>

              {result.analysis.similar_questions && result.analysis.similar_questions.length > 0 && (
                <div>
                  <span className="text-sm font-medium text-gray-500 block mb-2">推荐练习题目：</span>
                  <ul className="space-y-2">
                    {result.analysis.similar_questions.map((question: string, index: number) => (
                      <li key={index} className="text-sm text-gray-700 flex items-start bg-green-50 rounded p-3">
                        <span className="text-green-500 mr-2 mt-0.5">📚</span>
                        {question}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {result.mistake.ai_insights && result.mistake.ai_insights.questions_found && result.mistake.ai_insights.questions_found.length > 0 && (
                <div>
                  <span className="text-sm font-medium text-gray-500 block mb-2">识别的题目：</span>
                  <ul className="space-y-1">
                    {result.mistake.ai_insights.questions_found.map((question: string, index: number) => (
                      <li key={index} className="text-sm text-gray-700 flex items-start">
                        <span className="text-gray-500 mr-2">•</span>
                        {question}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>

          <div className="flex justify-center">
            <button
              onClick={resetForm}
              className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            >
              上传另一个错题
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default UploadMistake
