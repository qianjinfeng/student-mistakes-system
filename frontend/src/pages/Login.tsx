import { useState } from 'react'
import { apiClient } from '../api/client'

interface LoginProps {
  onLogin: (user: any, token: string) => void
}

const Login = ({ onLogin }: LoginProps) => {
  const [isLogin, setIsLogin] = useState(true)
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    full_name: '',
    password: ''
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const payload = isLogin
        ? new URLSearchParams({
            username: formData.username,
            password: formData.password
          })
        : {
            username: formData.username,
            email: formData.email,
            full_name: formData.full_name,
            password: formData.password
          }

      const data = isLogin
        ? await apiClient.postForm('/api/auth/token', payload as URLSearchParams)
        : await apiClient.post('/api/auth/register', payload as any)

      if (isLogin) {
        // Get user info
        const userData = await apiClient.get('/api/auth/me', data.access_token)
        onLogin(userData, data.access_token)
      } else {
        // Registration successful, switch to login
        setIsLogin(true)
        setError('注册成功，请登录')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '操作失败')
    } finally {
      setLoading(false)
    }
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }))
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            {isLogin ? '登录账户' : '创建账户'}
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            {isLogin ? '欢迎回来！' : '开始您的学习之旅'}
          </p>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="space-y-4">
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-gray-700">
                用户名
              </label>
              <input
                id="username"
                name="username"
                type="text"
                required
                value={formData.username}
                onChange={handleInputChange}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            {!isLogin && (
              <>
                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                    邮箱
                  </label>
                  <input
                    id="email"
                    name="email"
                    type="email"
                    required
                    value={formData.email}
                    onChange={handleInputChange}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label htmlFor="full_name" className="block text-sm font-medium text-gray-700">
                    姓名
                  </label>
                  <input
                    id="full_name"
                    name="full_name"
                    type="text"
                    value={formData.full_name}
                    onChange={handleInputChange}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </>
            )}

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                密码
              </label>
              <input
                id="password"
                name="password"
                type="password"
                required
                value={formData.password}
                onChange={handleInputChange}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>

          {error && (
            <div className="text-red-600 text-sm text-center">
              {error}
            </div>
          )}

          <div>
            <button
              type="submit"
              disabled={loading}
              className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              {loading ? '处理中...' : (isLogin ? '登录' : '注册')}
            </button>
          </div>

          <div className="text-center">
            <button
              type="button"
              onClick={() => setIsLogin(!isLogin)}
              className="text-sm text-blue-600 hover:text-blue-500"
            >
              {isLogin ? '还没有账户？点击注册' : '已有账户？点击登录'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default Login