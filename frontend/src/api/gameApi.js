import axios from 'axios'

// 创建一个带有基础配置的axios实例
const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    console.log(`API请求: ${config.method.toUpperCase()} ${config.baseURL}${config.url}`, config.data || '')
    return config
  },
  error => {
    console.error('API请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    console.log(`API响应: ${response.config.url}`, response.data)
    return response
  },
  error => {
    if (error.response) {
      console.error(`API错误 ${error.response.status}:`, error.response.data)
    } else if (error.request) {
      console.error('API错误: 没有收到响应', error.request)
    } else {
      console.error('API错误:', error.message)
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
  
  // 开始游戏
  startGame: (playerResponse) => {
    return api.post('/game/start', { playerResponse })
  },
  
  // 提交每天的选择
  submitDayChoice: (day, choice) => {
    return api.post(`/game/day${day}`, { choice })
  },
  
  // 分析勇者信息
  analyzeHero: (playerResponse) => {
    return api.post('/hero/analyze', { playerResponse })
  },
  
  // 创建世界（包含勇者信息分析和世界生成）
  createWorld: (playerResponse) => {
    return api.post('/world/create', { playerResponse })
  }
}

export default gameApi
