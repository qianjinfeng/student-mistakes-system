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
  const [saved, setSaved] = useState(false)

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

  const saveMistake = () => {
    setSaved(true)
  }

  const discardMistake = async () => {
    if (!result) return

    try {
      const response = await fetch(`/api/mistakes/${result.mistake.id}`, {
        method: 'DELETE'
      })

      if (!response.ok) {
        throw new Error('Failed to discard mistake')
      }

      resetForm()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to discard mistake')
    }
  }

  const resetForm = () => {
    setResult(null)
    setError('')
    setSubject('')
    setSaved(false)
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
          <div className={`border rounded-md p-6 ${saved ? 'bg-green-50 border-green-200' : 'bg-blue-50 border-blue-200'}`}>
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className={`h-5 w-5 ${saved ? 'text-green-400' : 'text-blue-400'}`} viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-gray-800">
                  {saved ? '错题已保存！' : '分析完成，请选择操作'}
                </h3>
                <div className="mt-2 text-sm text-gray-700">
                  {saved ? (
                    <p>已获得 {result.points_awarded} 积分</p>
                  ) : (
                    <p>AI 已完成分析，您可以选择保存此错题或放弃</p>
                  )}
                </div>
              </div>
            </div>
          </div>

           <div className="bg-white rounded-lg shadow-lg overflow-hidden">
             <div className="bg-gradient-to-r from-blue-500 to-purple-600 px-6 py-4">
               <h3 className="text-xl font-semibold text-white flex items-center">
                 <svg className="w-6 h-6 mr-2" fill="currentColor" viewBox="0 0 20 20">
                   <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.293l-3-3a1 1 0 00-1.414 0l-3 3a1 1 0 101.414 1.414L9 9.414V13a1 1 0 102 0V9.414l1.293 1.293a1 1 0 001.414-1.414z" clipRule="evenodd" />
                 </svg>
                 AI 智能分析结果
               </h3>
             </div>

             <div className="p-6 space-y-6">
               {/* 基本信息卡片 */}
               <div className="bg-gray-50 rounded-lg p-4">
                 <h4 className="text-sm font-semibold text-gray-700 mb-3 flex items-center">
                   <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                     <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                   </svg>
                   分析概览
                 </h4>

                 <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                   <div className="space-y-2">
                     <div className="flex items-center justify-between">
                       <span className="text-sm text-gray-600">错误类型</span>
                       <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                         result.analysis.error_type === 'conceptual' ? 'bg-red-100 text-red-800 border border-red-200' :
                         result.analysis.error_type === 'calculation' ? 'bg-yellow-100 text-yellow-800 border border-yellow-200' :
                         result.analysis.error_type === 'misreading' ? 'bg-blue-100 text-blue-800 border border-blue-200' :
                         'bg-gray-100 text-gray-800 border border-gray-200'
                       }`}>
                         {result.analysis.error_type === 'conceptual' ? '🧠 概念错误' :
                          result.analysis.error_type === 'calculation' ? '🔢 计算错误' :
                          result.analysis.error_type === 'misreading' ? '👁️ 读题错误' : '❓ 其他错误'}
                       </span>
                     </div>

                     <div>
                       <div className="flex items-center justify-between mb-1">
                         <span className="text-sm text-gray-600">分析置信度</span>
                         <span className="text-sm font-medium text-gray-900">{Math.round(result.analysis.confidence * 100)}%</span>
                       </div>
                       <div className="w-full bg-gray-200 rounded-full h-2">
                         <div
                           className={`h-2 rounded-full transition-all duration-300 ${
                             result.analysis.confidence > 0.8 ? 'bg-green-500' :
                             result.analysis.confidence > 0.6 ? 'bg-yellow-500' : 'bg-red-500'
                           }`}
                           style={{ width: `${result.analysis.confidence * 100}%` }}
                         ></div>
                       </div>
                     </div>
                   </div>
                 </div>
               </div>

               {/* 错误根本原因 */}
               {result.mistake.ai_insights && result.mistake.ai_insights.root_cause && (
                 <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                   <h4 className="text-sm font-semibold text-red-800 mb-3 flex items-center">
                     <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                       <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 000 16zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                     </svg>
                     错误根本原因
                   </h4>
                   <div className="bg-white rounded-md p-4 border border-red-100">
                     <p className="text-sm text-red-900 leading-relaxed">
                       {result.mistake.ai_insights.root_cause}
                     </p>
                   </div>
                 </div>
               )}

               {/* 学习建议 */}
               <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                 <h4 className="text-sm font-semibold text-blue-800 mb-3 flex items-center">
                   <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                     <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                   </svg>
                   个性化学习建议
                 </h4>
                 <div className="space-y-3">
                   {result.analysis.insights.map((insight: string, index: number) => (
                     <div key={index} className="bg-white rounded-md p-3 border border-blue-100 shadow-sm">
                       <div className="flex items-start">
                         <span className="text-blue-500 mr-3 mt-0.5 flex-shrink-0">
                           <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                             <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                           </svg>
                         </span>
                         <p className="text-sm text-blue-900 leading-relaxed">{insight}</p>
                       </div>
                     </div>
                   ))}
                 </div>
               </div>

               {/* 推荐练习题目 */}
               {result.analysis.similar_questions && result.analysis.similar_questions.length > 0 && (
                 <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                   <h4 className="text-sm font-semibold text-green-800 mb-3 flex items-center">
                     <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                       <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                     </svg>
                     推荐练习题目
                   </h4>
                   <div className="space-y-2">
                     {result.analysis.similar_questions.map((question: string, index: number) => (
                       <div key={index} className="bg-white rounded-md p-3 border border-green-100">
                         <div className="flex items-start">
                           <span className="text-green-600 mr-3 mt-0.5 flex-shrink-0 text-sm font-medium">
                             {index + 1}.
                           </span>
                           <p className="text-sm text-green-900 leading-relaxed">{question}</p>
                         </div>
                       </div>
                     ))}
                   </div>
                 </div>
               )}

               {/* 识别的题目 */}
               {result.mistake.ai_insights && result.mistake.ai_insights.questions_found && result.mistake.ai_insights.questions_found.length > 0 && (
                 <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                   <h4 className="text-sm font-semibold text-purple-800 mb-3 flex items-center">
                     <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                       <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clipRule="evenodd" />
                     </svg>
                     识别的题目内容
                   </h4>
                   <div className="bg-white rounded-md p-4 border border-purple-100">
                     <ul className="space-y-2">
                       {result.mistake.ai_insights.questions_found.map((question: string, index: number) => (
                         <li key={index} className="text-sm text-purple-900 flex items-start">
                           <span className="text-purple-600 mr-3 mt-0.5 flex-shrink-0 font-medium">
                             Q{index + 1}.
                           </span>
                           <span className="leading-relaxed">{question}</span>
                         </li>
                       ))}
                     </ul>
                   </div>
                 </div>
               )}
             </div>
           </div>

           <div className="flex justify-center space-x-4">
             {!saved ? (
               <>
                 <button
                   onClick={saveMistake}
                   className="px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
                 >
                   💾 保存错题
                 </button>
                 <button
                   onClick={discardMistake}
                   className="px-6 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
                 >
                   🗑️ 放弃
                 </button>
               </>
             ) : (
               <button
                 onClick={resetForm}
                 className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
               >
                 上传另一个错题
               </button>
             )}
           </div>
        </div>
      )}
    </div>
  )
}

export default UploadMistake
