const Achievements = () => {
  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">我的成就</h1>
        <p className="text-gray-600">展示您的学习成果和里程碑</p>
      </div>

      <div className="bg-white rounded-lg shadow p-8 text-center">
        <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
        </svg>
        <h3 className="mt-2 text-sm font-medium text-gray-900">成就系统开发中</h3>
        <p className="mt-1 text-sm text-gray-500">
          即将展示您的学习成就和获得的奖章
        </p>
      </div>
    </div>
  )
}

export default Achievements