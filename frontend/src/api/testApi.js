import gameApi from './gameApi'

// 测试获取开场白API
console.log('开始测试API...')

// 测试获取开场白
gameApi.getPrologue()
  .then(response => {
    console.log('开场白API测试成功:', response.data)
  })
  .catch(error => {
    console.error('开场白API测试失败:', error)
  })

console.log('API测试请求已发送，请查看控制台输出')
