import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'

interface UserStats {
  current_streak: number
  longest_streak: number
  total_reviews: number
  total_points: number
  achievements_count: number
  last_review_date?: string
}

interface DailyReview {
  id: string
  mistake_id: string
  scheduled_date: string
  interval_days: number
  ease_factor: number
  repetitions: number
  is_completed: boolean
}

interface ReviewPlan {
  date: string
  reviews: DailyReview[]
  total_count: number
}

const Dashboard = () => {
  const [stats, setStats] = useState<UserStats | null>(null)
  const [reviewPlan, setReviewPlan] = useState<ReviewPlan | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchUserStats()
    fetchReviewPlan()
  }, [])

  const fetchUserStats = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch('/api/achievements/stats', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        setStats(data)
      }
    } catch (error) {
      console.error('Failed to fetch user stats:', error)
    }
  }

  const fetchReviewPlan = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch('/api/reviews/daily-plan', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        setReviewPlan(data)
      }
    } catch (error) {
      console.error('Failed to fetch review plan:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-gray-600">加载中...</div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">学习概览</h1>
        <p className="text-gray-600">跟踪您的学习进度和成就</p>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-lg">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">当前连续天数</p>
                <p className="text-2xl font-bold text-gray-900">{stats.current_streak}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-lg">
                <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">总复习次数</p>
                <p className="text-2xl font-bold text-gray-900">{stats.total_reviews}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-2 bg-yellow-100 rounded-lg">
                <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">总积分</p>
                <p className="text-2xl font-bold text-gray-900">{stats.total_points}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-2 bg-purple-100 rounded-lg">
                <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">成就数量</p>
                <p className="text-2xl font-bold text-gray-900">{stats.achievements_count}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Today's Review Plan */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-gray-900">今日复习计划</h2>
          <Link
            to="/review"
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 text-sm font-medium"
          >
            开始复习
          </Link>
        </div>

        {reviewPlan ? (
          reviewPlan.total_count > 0 ? (
            <div>
              <p className="text-gray-600 mb-4">
                今日共有 {reviewPlan.total_count} 个复习任务
              </p>
              <div className="space-y-3">
                {reviewPlan.reviews.slice(0, 3).map((review) => (
                  <div key={review.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div>
                      <p className="text-sm font-medium text-gray-900">
                        复习任务 #{review.mistake_id.slice(-8)}
                      </p>
                      <p className="text-xs text-gray-500">
                        间隔: {review.interval_days}天 | 重复: {review.repetitions}次
                      </p>
                    </div>
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      review.is_completed ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {review.is_completed ? '已完成' : '待复习'}
                    </span>
                  </div>
                ))}
                {reviewPlan.total_count > 3 && (
                  <p className="text-sm text-gray-500 text-center">
                    还有 {reviewPlan.total_count - 3} 个任务...
                  </p>
                )}
              </div>
            </div>
          ) : (
            <div className="text-center py-8">
              <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <h3 className="mt-2 text-sm font-medium text-gray-900">今日暂无复习任务</h3>
              <p className="mt-1 text-sm text-gray-500">
                继续上传错题来建立您的复习计划
              </p>
              <div className="mt-6">
                <Link
                  to="/upload"
                  className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
                >
                  上传错题
                </Link>
              </div>
            </div>
          )
        ) : (
          <div className="text-center py-8">
            <div className="text-gray-500">加载复习计划中...</div>
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Link
          to="/upload"
          className="bg-white rounded-lg shadow p-6 hover:shadow-md transition-shadow"
        >
          <div className="flex items-center">
            <div className="p-3 bg-blue-100 rounded-lg">
              <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-medium text-gray-900">上传错题</h3>
              <p className="text-gray-600">添加新的错题进行分析</p>
            </div>
          </div>
        </Link>

        <Link
          to="/achievements"
          className="bg-white rounded-lg shadow p-6 hover:shadow-md transition-shadow"
        >
          <div className="flex items-center">
            <div className="p-3 bg-green-100 rounded-lg">
              <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
              </svg>
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-medium text-gray-900">查看成就</h3>
              <p className="text-gray-600">查看您的学习成就</p>
            </div>
          </div>
        </Link>
      </div>
    </div>
  )
}

export default Dashboard