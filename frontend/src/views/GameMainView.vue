<template>
  <div class="game-main-container">
    <!-- 游戏头部信息 -->
    <div class="game-header">
      <div class="day-info">
        <span class="day-counter">第 {{ gameState.day }} 天</span>
        <span class="time-period">{{ currentTimePeriod }}</span>
      </div>
      <div class="header-right">
        <div class="weather-info">{{ gameState.world?.weather || '晴天' }}</div>
        <button class="map-button" @click="showMapModal = true" title="查看地图">
          🗺️
        </button>
      </div>
    </div>

    <!-- 主游戏区域 -->
    <div class="game-main-content">
      <!-- 左侧：游戏内容区 -->
      <div class="game-content-area">
        <!-- 游戏状态加载中 -->
        <div v-if="isLoadingGameState" class="loading-container">
          <div class="loading-spinner"></div>
          <div class="loading-text">正在加载游戏状态...</div>
          <div class="loading-tip">请稍候</div>
        </div>

        <!-- 行动输入面板 -->
        <ActionInputPanel
          v-else-if="!isProcessing && !showResults && gameStateLoaded"
          @submit-action="handleActionSubmit"
          :disabled="isProcessing"
        />

        <!-- 游戏结果展示面板 -->
        <GameResultPanel
          v-else-if="showResults"
          :result="actionResult"
          @continue-game="handleContinueGame"
        />

        <!-- 处理行动加载状态 -->
        <div v-else-if="isProcessing" class="loading-container">
          <div class="loading-spinner"></div>
          <div class="loading-text">正在处理您的行动...</div>
          <div class="loading-tip">AI正在推演游戏世界，请稍候（约30-90秒）</div>
          <div class="loading-detail">系统正在分析您的行动并生成游戏结果</div>
        </div>

        <!-- 游戏状态加载失败提示 -->
        <div v-else-if="!gameStateLoaded" class="error-container">
          <div class="error-icon">⚠️</div>
          <div class="error-text">游戏状态加载失败</div>
          <div class="error-detail">请检查网络连接或重新开始游戏</div>
          <button @click="retryLoadGameState" class="retry-btn">重试</button>
        </div>
      </div>

      <!-- 右侧：游戏状态栏 -->
      <div class="game-sidebar">
        <!-- 玩家状态 -->
        <div class="collapsible-section player-status-section">
          <div class="section-header" @click="toggleSection('player')">
            <h3>{{ getPlayerBasicInfo('name') || '勇者' }}</h3>
            <span class="collapse-icon" :class="{ 'collapsed': collapsedSections.player }">▼</span>
          </div>
          <div class="section-content" v-show="!collapsedSections.player">
            <div class="player-basic-info">
              <div class="info-item">
                <span class="info-label">性别:</span>
                <span class="info-value">{{ getPlayerBasicInfo('gender') || '未知' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">职业:</span>
                <span class="info-value">{{ getPlayerBasicInfo('profession') || '勇者' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">年龄:</span>
                <span class="info-value">{{ getPlayerBasicInfo('age') || '未知' }}</span>
              </div>
            </div>
            <div class="player-stats">
              <div class="stat-item">
                <span class="stat-label">生命值:</span>
                <span class="stat-value">{{ getPlayerStat('hp') }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">魔法值:</span>
                <span class="stat-value">{{ getPlayerStat('mp') }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">力量:</span>
                <span class="stat-value">{{ getPlayerStat('strength') }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">智力:</span>
                <span class="stat-value">{{ getPlayerStat('intelligence') }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">敏捷:</span>
                <span class="stat-value">{{ getPlayerStat('agility') }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">幸运:</span>
                <span class="stat-value">{{ getPlayerStat('luck') }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 世界状态 -->
        <div class="collapsible-section world-status-section">
          <div class="section-header" @click="toggleSection('world')">
            <h3>世界状态</h3>
            <span class="collapse-icon" :class="{ 'collapsed': collapsedSections.world }">▼</span>
          </div>
          <div class="section-content" v-show="!collapsedSections.world">
            <div class="world-info">
              <div class="info-item">
                <span class="info-label">天气:</span>
                <span class="info-value">{{ gameState.world?.weather || '晴天' }}</span>
              </div>
            </div>

            <!-- 当天固定事件 -->
            <div class="fixed-events-container">
              <h4 class="events-title">今日事件</h4>
              <div v-if="todayFixedEvents.length > 0" class="events-list">
                <div
                  v-for="(event, index) in todayFixedEvents"
                  :key="index"
                  class="event-card"
                >
                  <div class="event-header" @click="toggleEventCard(index)">
                    <span class="event-time">{{ getTimePeriodText(event.period) }}</span>
                    <span class="event-collapse-icon" :class="{ 'collapsed': collapsedEvents[index] }">▼</span>
                  </div>
                  <div class="event-content" v-show="!collapsedEvents[index]">
                    <p class="event-description">{{ event.description }}</p>
                  </div>
                </div>
              </div>
              <div v-else class="no-events">
                今日暂无特殊事件
              </div>
            </div>
          </div>
        </div>

        <!-- NPC关系 -->
        <div class="collapsible-section npc-relations-section">
          <div class="section-header" @click="toggleSection('npc')">
            <h3>人物关系</h3>
            <span class="collapse-icon" :class="{ 'collapsed': collapsedSections.npc }">▼</span>
          </div>
          <div class="section-content" v-show="!collapsedSections.npc">
            <div class="npc-list">
              <div
                v-for="(npc, npcId) in gameState.npc"
                :key="npcId"
                class="npc-item"
              >
                <span class="npc-name">{{ npc.name }}</span>
                <span class="npc-relation" :class="getRelationClass(npc.relationship)">
                  {{ getRelationText(npc.relationship) }}
                </span>
              </div>
              <div v-if="!gameState.npc || Object.keys(gameState.npc).length === 0" class="no-npcs">
                暂无人物关系
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 错误提示 -->
    <div v-if="errorMessage" class="error-message">
      {{ errorMessage }}
      <button @click="clearError" class="close-error">×</button>
    </div>

    <!-- 地图弹窗 -->
    <div v-if="showMapModal" class="map-modal-overlay" @click="closeMapModal">
      <div class="map-modal" @click.stop>
        <div class="map-modal-header">
          <h3>艾尔德拉村庄地图</h3>
          <button class="close-button" @click="showMapModal = false">×</button>
        </div>
        <div class="map-modal-content">
          <div class="map-container">
            <img src="/images/map.png" alt="游戏地图" class="map-image" />
          </div>
          <div class="locations-panel">
            <h4>可探索地点 ({{ worldLocations.length }})</h4>
            <div v-if="worldLocations.length === 0" class="no-locations">
              正在加载地点数据...
            </div>
            <div v-else class="locations-list">
              <div
                v-for="location in worldLocations"
                :key="location.id"
                class="location-item"
                :class="getSafetyClass(location.safety_level)"
                @click="selectLocation(location)"
              >
                <div class="location-header">
                  <span class="location-name">{{ location.name }}</span>
                  <span class="location-type">{{ getLocationTypeText(location.type) }}</span>
                </div>
                <div class="location-description">{{ location.description }}</div>
                <div class="location-services" v-if="location.available_services?.length > 0">
                  <span class="services-label">可用服务:</span>
                  <span class="services-list">{{ location.available_services.join('、') }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import ActionInputPanel from '@/components/ActionInputPanel.vue'
import GameResultPanel from '@/components/GameResultPanel.vue'
import gameApi from '@/api/gameApi'

export default {
  name: 'GameMainView',
  components: {
    ActionInputPanel,
    GameResultPanel
  },
  setup() {
    const route = useRoute()
    const router = useRouter()
    
    // 响应式数据
    const gameState = reactive({
      day: 1,
      player: {},
      world: {},
      npc: {},
      history: []
    })

    const isProcessing = ref(false)
    const showResults = ref(false)
    const actionResult = ref(null)
    const errorMessage = ref('')
    const gameId = ref('')
    const isLoadingGameState = ref(true)
    const gameStateLoaded = ref(false)

    // 地图相关状态
    const showMapModal = ref(false)
    const worldLocations = ref([])

    // 折叠状态管理
    const collapsedSections = reactive({
      player: false,
      world: false,
      npc: false
    })

    // 固定事件相关
    const todayFixedEvents = ref([])
    const collapsedEvents = reactive({})
    
    // 计算属性
    const currentTimePeriod = computed(() => {
      const time = gameState.world?.current_time
      switch(time) {
        case 'morning': return '上午'
        case 'afternoon': return '下午'
        case 'evening': return '晚上'
        default: return '上午'
      }
    })
    
    // 方法
    const handleActionSubmit = async (action) => {
      if (!gameId.value) {
        console.error('[handleActionSubmit] 游戏会话无效')
        showError('游戏会话无效，请重新开始游戏')
        return
      }

      console.log('[handleActionSubmit] 开始处理玩家行动')
      console.log('[handleActionSubmit] 游戏ID:', gameId.value)
      console.log('[handleActionSubmit] 行动内容:', action)
      console.log('[handleActionSubmit] 开始时间:', new Date().toLocaleTimeString())

      isProcessing.value = true
      showResults.value = false
      clearError()

      const startTime = Date.now()

      try {
        console.log('[handleActionSubmit] 调用API处理行动...')
        const response = await gameApi.processAction(gameId.value, action)

        const endTime = Date.now()
        const processingTime = (endTime - startTime) / 1000
        console.log('[handleActionSubmit] API调用完成')
        console.log('[handleActionSubmit] 处理耗时:', processingTime.toFixed(2), '秒')
        console.log('[handleActionSubmit] 结束时间:', new Date().toLocaleTimeString())
        console.log('[handleActionSubmit] 响应状态:', response.data?.status)

        if (response.data.status === 'success') {
          console.log('[handleActionSubmit] 行动处理成功')
          console.log('[handleActionSubmit] 结果数据:', response.data.result)

          actionResult.value = response.data.result

          // 更新游戏状态
          if (response.data.updated_game_state) {
            console.log('[handleActionSubmit] 更新游戏状态')
            console.log('[handleActionSubmit] 新状态:', response.data.updated_game_state)
            Object.assign(gameState, response.data.updated_game_state)
          }

          showResults.value = true
          console.log('[handleActionSubmit] 显示结果面板')
        } else {
          console.error('[handleActionSubmit] 行动处理失败:', response.data.message)
          showError(response.data.message || '行动处理失败')
        }
      } catch (error) {
        const endTime = Date.now()
        const processingTime = (endTime - startTime) / 1000
        console.error('[handleActionSubmit] 处理行动异常:', error)
        console.error('[handleActionSubmit] 异常发生时间:', new Date().toLocaleTimeString())
        console.error('[handleActionSubmit] 异常前耗时:', processingTime.toFixed(2), '秒')

        if (error.code === 'ECONNABORTED') {
          console.error('[handleActionSubmit] 请求超时')
          showError('请求超时，LLM处理时间较长，请稍后重试')
        } else if (error.response) {
          console.error('[handleActionSubmit] 服务器错误:', error.response.status, error.response.data)
          showError(`服务器错误: ${error.response.data?.message || '未知错误'}`)
        } else if (error.request) {
          console.error('[handleActionSubmit] 网络错误，无响应')
          showError('网络错误，请检查连接后重试')
        } else {
          console.error('[handleActionSubmit] 其他错误:', error.message)
          showError('处理失败，请重试')
        }
      } finally {
        isProcessing.value = false
        console.log('[handleActionSubmit] 处理完成，重置状态')
      }
    }
    
    const handleContinueGame = async () => {
      console.log('[handleContinueGame] 开始处理继续游戏')

      try {
        // 推进游戏天数
        if (gameState.day < 5) {
          console.log('[handleContinueGame] 推进游戏天数')
          const response = await gameApi.advanceGameDay(gameId.value)

          if (response.data.status === 'success') {
            console.log('[handleContinueGame] 天数推进成功')
            // 更新游戏状态
            if (response.data.updated_game_state) {
              Object.assign(gameState, response.data.updated_game_state)
              // 加载新一天的固定事件
              await loadTodayFixedEvents()
            }
          } else {
            console.error('[handleContinueGame] 天数推进失败:', response.data.message)
            showError(response.data.message || '天数推进失败')
            return
          }
        }

        showResults.value = false
        actionResult.value = null

        // 检查游戏是否结束
        if (gameState.day > 5) {
          console.log('[handleContinueGame] 游戏结束，跳转到结束页面')
          router.push(`/game/${gameId.value}/end`)
        }
      } catch (error) {
        console.error('[handleContinueGame] 继续游戏异常:', error)
        showError('继续游戏失败，请重试')
      }
    }
    
    const getRelationClass = (relationship) => {
      const value = relationship || 0
      if (value > 20) return 'relation-friendly'
      if (value < -20) return 'relation-hostile'
      return 'relation-neutral'
    }
    
    const getRelationText = (relationship) => {
      const value = relationship || 0
      if (value > 50) return '亲密'
      if (value > 20) return '友好'
      if (value > -20) return '中性'
      if (value > -50) return '冷淡'
      return '敌对'
    }

    const getPlayerBasicInfo = (field) => {
      if (!gameState.player) return null

      // 尝试从 player.basic_info 获取
      if (gameState.player.basic_info && gameState.player.basic_info[field] !== undefined) {
        return gameState.player.basic_info[field]
      }

      // 尝试从 player 直接获取
      if (gameState.player[field] !== undefined) {
        return gameState.player[field]
      }

      return null
    }

    const getPlayerStat = (statName) => {
      if (!gameState.player) return getDefaultStatValue(statName)

      // 尝试从 player.stats 获取
      if (gameState.player.stats && gameState.player.stats[statName] !== undefined && gameState.player.stats[statName] !== null) {
        return gameState.player.stats[statName]
      }

      // 尝试从 player 直接获取
      if (gameState.player[statName] !== undefined && gameState.player[statName] !== null) {
        return gameState.player[statName]
      }

      // 返回默认值
      return getDefaultStatValue(statName)
    }

    const getDefaultStatValue = (statName) => {
      switch(statName) {
        case 'hp':
        case 'mp':
          return 100
        case 'strength':
        case 'intelligence':
        case 'agility':
        case 'luck':
          return 50  // 使用新的默认值50
        default:
          return 0
      }
    }
    
    const showError = (message) => {
      errorMessage.value = message
    }
    
    const clearError = () => {
      errorMessage.value = ''
    }
    
    const loadGameState = async () => {
      const id = route.params.gameId
      if (!id) {
        showError('无效的游戏ID')
        isLoadingGameState.value = false
        gameStateLoaded.value = false
        return
      }

      gameId.value = id
      isLoadingGameState.value = true
      gameStateLoaded.value = false

      try {
        console.log('[loadGameState] 开始加载游戏状态，游戏ID:', id)
        const response = await gameApi.getGameState(id)
        console.log('[loadGameState] 获取游戏状态响应:', response.data)

        if (response.data && response.data.status === 'success') {
          // 正确提取游戏状态数据
          const actualGameState = response.data.game_state
          console.log('[loadGameState] 实际游戏状态:', actualGameState)

          if (actualGameState) {
            Object.assign(gameState, actualGameState)
            console.log('[loadGameState] 游戏状态已更新:', gameState)
            gameStateLoaded.value = true

            // 加载当天的固定事件
            await loadTodayFixedEvents()
          } else {
            console.error('[loadGameState] 游戏状态数据为空')
            showError('游戏状态数据为空')
            gameStateLoaded.value = false
          }
        } else {
          console.error('[loadGameState] 获取游戏状态失败:', response.data?.message)
          showError(response.data?.message || '获取游戏状态失败')
          gameStateLoaded.value = false
        }
      } catch (error) {
        console.error('[loadGameState] 加载游戏状态异常:', error)
        if (error.response?.status === 404) {
          showError('游戏会话不存在或已过期，请重新开始游戏')
        } else {
          showError('无法加载游戏状态，请检查网络连接')
        }
        gameStateLoaded.value = false
      } finally {
        isLoadingGameState.value = false
      }
    }

    const retryLoadGameState = () => {
      clearError()
      loadGameState()
    }

    // 折叠功能相关方法
    const toggleSection = (sectionName) => {
      collapsedSections[sectionName] = !collapsedSections[sectionName]
    }

    const toggleEventCard = (eventIndex) => {
      collapsedEvents[eventIndex] = !collapsedEvents[eventIndex]
    }

    // 获取时间段文本
    const getTimePeriodText = (period) => {
      switch(period) {
        case 'morning': return '上午'
        case 'afternoon': return '下午'
        case 'evening': return '晚上'
        default: return period
      }
    }

    // 加载当天的固定事件
    const loadTodayFixedEvents = async () => {
      try {
        console.log('[loadTodayFixedEvents] 加载第', gameState.day, '天的固定事件')
        const response = await gameApi.getFixedEventsForDay(gameState.day)

        if (response.data && response.data.status === 'success') {
          todayFixedEvents.value = response.data.events || []
          console.log('[loadTodayFixedEvents] 成功加载', todayFixedEvents.value.length, '个固定事件')

          // 初始化事件卡片折叠状态
          todayFixedEvents.value.forEach((_, index) => {
            collapsedEvents[index] = false
          })
        } else {
          console.warn('[loadTodayFixedEvents] 获取固定事件失败:', response.data?.message)
          todayFixedEvents.value = []
        }
      } catch (error) {
        console.error('[loadTodayFixedEvents] 加载固定事件异常:', error)
        todayFixedEvents.value = []
      }
    }

    // 地图相关方法
    const closeMapModal = () => {
      showMapModal.value = false
    }

    const getSafetyClass = (safetyLevel) => {
      const safetyMap = {
        'safe': 'safety-safe',
        'moderate': 'safety-moderate',
        'dangerous': 'safety-dangerous',
        'very_dangerous': 'safety-very-dangerous'
      }
      return safetyMap[safetyLevel] || 'safety-unknown'
    }

    const getLocationTypeText = (type) => {
      const typeMap = {
        'religious': '宗教场所',
        'residence': '居住地',
        'public': '公共场所',
        'commercial': '商业区',
        'accommodation': '住宿',
        'military': '军事',
        'wilderness': '野外'
      }
      return typeMap[type] || type
    }

    const selectLocation = (location) => {
      // 可以在这里添加选择地点的逻辑，比如显示详细信息或者设置为目标地点
      console.log('选择了地点:', location.name)
    }

    // 加载世界地点数据
    const loadWorldLocations = async () => {
      try {
        console.log('[loadWorldLocations] 开始加载世界地点数据')
        const response = await fetch('/api/world/description')
        console.log('[loadWorldLocations] API响应状态:', response.status)

        if (response.ok) {
          const result = await response.json()
          console.log('[loadWorldLocations] API响应数据:', result)

          // 根据API响应格式调整数据提取
          if (result.status === 'success' && result.data) {
            worldLocations.value = result.data.initial_locations || []
          } else {
            worldLocations.value = result.initial_locations || []
          }

          console.log('[loadWorldLocations] 加载的地点数量:', worldLocations.value.length)
        } else {
          console.error('[loadWorldLocations] API请求失败:', response.status)
        }
      } catch (error) {
        console.error('[loadWorldLocations] 加载世界地点数据异常:', error)
      }
    }
    
    // 生命周期
    onMounted(() => {
      loadGameState()
      loadWorldLocations()
    })
    
    return {
      gameState,
      isProcessing,
      showResults,
      actionResult,
      errorMessage,
      isLoadingGameState,
      gameStateLoaded,
      currentTimePeriod,
      handleActionSubmit,
      handleContinueGame,
      getRelationClass,
      getRelationText,
      getPlayerBasicInfo,
      getPlayerStat,
      clearError,
      retryLoadGameState,
      // 折叠功能
      collapsedSections,
      toggleSection,
      // 固定事件
      todayFixedEvents,
      collapsedEvents,
      toggleEventCard,
      getTimePeriodText,
      // 地图功能
      showMapModal,
      worldLocations,
      closeMapModal,
      getSafetyClass,
      getLocationTypeText,
      selectLocation
    }
  }
}
</script>

<style scoped>
.game-main-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #1a1a1a;
  color: #e0e0e0;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.game-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 25px;
  background: linear-gradient(135deg, #2c3e50, #34495e);
  border-bottom: 2px solid #3498db;
  box-shadow: 0 2px 10px rgba(0,0,0,0.3);
}

.day-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.day-counter {
  font-size: 20px;
  font-weight: bold;
  color: #3498db;
}

.time-period {
  font-size: 16px;
  color: #ecf0f1;
  background-color: rgba(52, 152, 219, 0.2);
  padding: 4px 12px;
  border-radius: 15px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 15px;
}

.weather-info {
  font-size: 16px;
  color: #f39c12;
  font-weight: 500;
}

.map-button {
  background: none;
  border: 2px solid #3498db;
  color: #3498db;
  font-size: 20px;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.map-button:hover {
  background-color: #3498db;
  color: white;
  transform: scale(1.1);
}

.game-main-content {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.game-content-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 20px;
  overflow-y: auto;
}

.game-sidebar {
  width: 300px;
  background-color: #2c3e50;
  border-left: 1px solid #34495e;
  padding: 20px;
  overflow-y: auto;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
  text-align: center;
}

.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
  text-align: center;
  padding: 40px;
}

.error-icon {
  font-size: 48px;
  margin-bottom: 20px;
}

.error-text {
  font-size: 20px;
  font-weight: 600;
  color: #e74c3c;
  margin-bottom: 10px;
}

.error-detail {
  font-size: 14px;
  color: #95a5a6;
  margin-bottom: 20px;
}

.retry-btn {
  padding: 10px 20px;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.retry-btn:hover {
  background-color: #2980b9;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #34495e;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  font-size: 18px;
  font-weight: 500;
  margin-bottom: 10px;
  color: #3498db;
}

.loading-tip {
  font-size: 14px;
  color: #95a5a6;
  margin-bottom: 8px;
}

.loading-detail {
  font-size: 12px;
  color: #7f8c8d;
  font-style: italic;
}

/* 折叠面板样式 */
.collapsible-section {
  margin-bottom: 25px;
  background-color: #34495e;
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 15px;
  background-color: #2c3e50;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.section-header:hover {
  background-color: #34495e;
}

.section-header h3 {
  margin: 0;
  color: #3498db;
  font-size: 16px;
  font-weight: 600;
}

.collapse-icon {
  color: #95a5a6;
  font-size: 12px;
  transition: transform 0.3s ease;
}

.collapse-icon.collapsed {
  transform: rotate(-90deg);
}

.section-content {
  padding: 15px;
}

.player-basic-info,
.player-stats,
.world-info,
.npc-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.player-basic-info {
  margin-bottom: 15px;
}

.stat-item,
.info-item {
  display: flex;
  justify-content: space-between;
  padding: 6px 10px;
  background-color: #34495e;
  border-radius: 4px;
  font-size: 14px;
}

.stat-label,
.info-label {
  color: #bdc3c7;
}

.stat-value,
.info-value {
  color: #ecf0f1;
  font-weight: 500;
}

.npc-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 10px;
  background-color: #34495e;
  border-radius: 4px;
  font-size: 14px;
}

.npc-name {
  color: #ecf0f1;
  font-weight: 500;
}

.npc-relation {
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 500;
}

.relation-friendly {
  background-color: #27ae60;
  color: white;
}

.relation-neutral {
  background-color: #95a5a6;
  color: white;
}

.relation-hostile {
  background-color: #e74c3c;
  color: white;
}

.no-npcs {
  color: #95a5a6;
  font-style: italic;
  text-align: center;
  padding: 15px;
}

.error-message {
  position: fixed;
  top: 20px;
  right: 20px;
  background-color: #e74c3c;
  color: white;
  padding: 15px 20px;
  border-radius: 5px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.3);
  display: flex;
  align-items: center;
  gap: 10px;
  z-index: 1000;
}

.close-error {
  background: none;
  border: none;
  color: white;
  font-size: 18px;
  cursor: pointer;
  padding: 0;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-error:hover {
  background-color: rgba(255,255,255,0.2);
  border-radius: 50%;
}

/* 固定事件样式 */
.fixed-events-container {
  margin-top: 20px;
}

.events-title {
  margin: 0 0 12px 0;
  color: #f39c12;
  font-size: 14px;
  font-weight: 600;
  border-bottom: 1px solid #34495e;
  padding-bottom: 6px;
}

.events-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.event-card {
  background-color: #2c3e50;
  border-radius: 6px;
  overflow: hidden;
  border: 1px solid #34495e;
  transition: all 0.3s ease;
}

.event-card:hover {
  border-color: #3498db;
}

.event-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  cursor: pointer;
  background-color: #34495e;
  transition: background-color 0.3s ease;
}

.event-header:hover {
  background-color: #3c5a75;
}

.event-time {
  color: #f39c12;
  font-size: 12px;
  font-weight: 600;
  background-color: rgba(243, 156, 18, 0.2);
  padding: 2px 8px;
  border-radius: 10px;
}

.event-collapse-icon {
  color: #95a5a6;
  font-size: 10px;
  transition: transform 0.3s ease;
}

.event-collapse-icon.collapsed {
  transform: rotate(-90deg);
}

.event-content {
  padding: 10px 12px;
  background-color: #2c3e50;
}

.event-description {
  margin: 0;
  color: #ecf0f1;
  font-size: 13px;
  line-height: 1.4;
}

.no-events {
  color: #95a5a6;
  font-style: italic;
  text-align: center;
  padding: 15px;
  font-size: 13px;
}

/* 地图弹窗样式 */
.map-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.map-modal {
  background-color: #2c3e50;
  border-radius: 12px;
  width: 90%;
  max-width: 1200px;
  height: 80%;
  max-height: 800px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
}

.map-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 25px;
  border-bottom: 2px solid #34495e;
  background-color: #34495e;
  border-radius: 12px 12px 0 0;
}

.map-modal-header h3 {
  margin: 0;
  color: #3498db;
  font-size: 20px;
  font-weight: 600;
}

.close-button {
  background: none;
  border: none;
  color: #95a5a6;
  font-size: 24px;
  cursor: pointer;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.3s ease;
}

.close-button:hover {
  background-color: #e74c3c;
  color: white;
}

.map-modal-content {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.map-container {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background-color: #34495e;
}

.map-image {
  max-width: 100%;
  max-height: 100%;
  border-radius: 8px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
}

.locations-panel {
  width: 350px;
  background-color: #2c3e50;
  border-left: 2px solid #34495e;
  padding: 20px;
  overflow-y: auto;
}

.locations-panel h4 {
  margin: 0 0 15px 0;
  color: #3498db;
  font-size: 16px;
  font-weight: 600;
  border-bottom: 1px solid #34495e;
  padding-bottom: 8px;
}

.locations-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.location-item {
  background-color: #34495e;
  border-radius: 8px;
  padding: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  border-left: 4px solid transparent;
}

.location-item:hover {
  background-color: #3c5a75;
  transform: translateX(4px);
}

.location-item.safety-safe {
  border-left-color: #27ae60;
}

.location-item.safety-moderate {
  border-left-color: #f39c12;
}

.location-item.safety-dangerous {
  border-left-color: #e67e22;
}

.location-item.safety-very-dangerous {
  border-left-color: #e74c3c;
}

.location-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.location-name {
  color: #ecf0f1;
  font-weight: 600;
  font-size: 14px;
}

.location-type {
  color: #95a5a6;
  font-size: 12px;
  background-color: rgba(149, 165, 166, 0.2);
  padding: 2px 8px;
  border-radius: 10px;
}

.location-description {
  color: #bdc3c7;
  font-size: 13px;
  line-height: 1.4;
  margin-bottom: 8px;
}

.location-services {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  align-items: center;
}

.services-label {
  color: #95a5a6;
  font-size: 12px;
  margin-right: 4px;
}

.services-list {
  color: #3498db;
  font-size: 12px;
  font-weight: 500;
}

.no-locations {
  color: #95a5a6;
  font-style: italic;
  text-align: center;
  padding: 20px;
  font-size: 14px;
}
</style>
