import axios from 'axios'

// 创建一个带有基础配置的axios实例
const api = axios.create({
  baseURL: '/api',
  timeout: 30000, // 增加到30秒，适应一般API调用
  headers: {
    'Content-Type': 'application/json'
  }
})

// 创建一个用于游戏行动处理的长超时实例
const longTimeoutApi = axios.create({
  baseURL: '/api',
  timeout: 90000, // 90秒超时，适应LLM调用
  headers: {
    'Content-Type': 'application/json'
  }
})

// 为普通API添加请求拦截器
api.interceptors.request.use(
  config => {
    console.log(`[API请求] ${config.method.toUpperCase()} ${config.baseURL}${config.url}`, config.data || '')
    console.log(`[API请求] 超时时间: ${config.timeout}ms`)
    return config
  },
  error => {
    console.error('[API请求错误]:', error)
    return Promise.reject(error)
  }
)

// 为长超时API添加请求拦截器
longTimeoutApi.interceptors.request.use(
  config => {
    console.log(`[长超时API请求] ${config.method.toUpperCase()} ${config.baseURL}${config.url}`, config.data || '')
    console.log(`[长超时API请求] 超时时间: ${config.timeout}ms`)
    console.log(`[长超时API请求] 开始时间: ${new Date().toLocaleTimeString()}`)
    return config
  },
  error => {
    console.error('[长超时API请求错误]:', error)
    return Promise.reject(error)
  }
)

// 为普通API添加响应拦截器
api.interceptors.response.use(
  response => {
    console.log(`[API响应] ${response.config.url}`, response.data)
    return response
  },
  error => {
    console.error('[API响应错误]:', error)
    if (error.response) {
      console.error('[错误状态码]:', error.response.status)
      console.error('[错误数据]:', error.response.data)
    } else if (error.request) {
      console.error('[请求未收到响应]:', error.request)
    } else if (error.code === 'ECONNABORTED') {
      console.error('[请求超时]:', error.message)
    } else {
      console.error('[请求配置错误]:', error.message)
    }
    return Promise.reject(error)
  }
)

// 为长超时API添加响应拦截器
longTimeoutApi.interceptors.response.use(
  response => {
    console.log(`[长超时API响应] ${response.config.url}`)
    console.log(`[长超时API响应] 完成时间: ${new Date().toLocaleTimeString()}`)
    console.log(`[长超时API响应] 数据:`, response.data)
    return response
  },
  error => {
    console.error('[长超时API响应错误]:', error)
    console.error(`[长超时API错误] 错误时间: ${new Date().toLocaleTimeString()}`)
    if (error.response) {
      console.error('[错误状态码]:', error.response.status)
      console.error('[错误数据]:', error.response.data)
    } else if (error.request) {
      console.error('[请求未收到响应]:', error.request)
    } else if (error.code === 'ECONNABORTED') {
      console.error('[请求超时]:', error.message)
    } else {
      console.error('[请求配置错误]:', error.message)
    }
    return Promise.reject(error)
  }
)

// 游戏相关API
const gameApi = {
  // 获取开场白
  getPrologue: () => {
    return api.get('/game/prologue')
  },

  // 创建世界（包含勇者信息分析和世界生成）- 使用长超时
  createWorld: (playerResponse) => {
    console.log('[createWorld] 开始创建世界，使用长超时API')
    return longTimeoutApi.post('/world/create', { playerResponse })
  },

  // 处理游戏行动 - 核心接口，使用长超时
  processAction: (gameId, action) => {
    console.log('[processAction] 开始处理游戏行动，使用长超时API')
    console.log('[processAction] 游戏ID:', gameId)
    console.log('[processAction] 行动内容:', action)
    return longTimeoutApi.post('/game/action', {
      game_id: gameId,
      action: action
    })
  },

  // 获取游戏状态
  getGameState: (gameId) => {
    return api.get(`/game/session/${gameId}/state`)
  },

  // 创建游戏会话
  createSession: (initialData) => {
    return api.post('/game/session/create', initialData)
  },

  // 获取会话信息
  getSession: (gameId) => {
    return api.get(`/game/session/${gameId}`)
  },

  // 推进游戏天数
  advanceGameDay: (gameId) => {
    console.log('[advanceGameDay] 推进游戏天数')
    return api.post(`/game/session/${gameId}/advance-day`)
  },

  // 健康检查
  healthCheck: () => {
    return api.get('/game/health')
  },

  // 获取指定天数的固定事件
  getFixedEventsForDay: (day) => {
    return api.get(`/events/fixed/day/${day}`)
  }
}

export default gameApi
