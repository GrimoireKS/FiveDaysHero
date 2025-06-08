<template>
  <div class="game-result-panel">
    <div class="panel-header">
      <h2>📖 今日冒险记录</h2>
      <p class="subtitle">您的行动带来了以下变化...</p>
    </div>

    <!-- 时段进度条 -->
    <div class="time-progression">
      <div class="time-periods">
        <div 
          v-for="(period, index) in timePeriods" 
          :key="period.key"
          class="time-period"
          :class="{ 'active': currentPeriodIndex >= index, 'current': currentPeriodIndex === index }"
        >
          <div class="period-icon">{{ period.icon }}</div>
          <div class="period-name">{{ period.name }}</div>
        </div>
      </div>
      <div class="progress-line">
        <div class="progress-fill" :style="{ width: progressWidth }"></div>
      </div>
    </div>

    <!-- 时段详情 -->
    <div class="time-details">
      <div 
        v-for="(period, index) in timePeriods" 
        :key="period.key"
        v-show="currentPeriodIndex >= index"
        class="period-detail"
        :class="{ 'current': currentPeriodIndex === index }"
      >
        <div class="period-header">
          <span class="period-title">{{ period.icon }} {{ period.name }}</span>
          <span class="period-time">{{ period.time }}</span>
        </div>
        
        <div class="period-content">
          <!-- 叙述内容 -->
          <div class="narrative-section">
            <h4>📜 事件叙述</h4>
            <div class="narrative-text">
              {{ getPeriodNarrative(period.key) }}
            </div>
          </div>
          
          <!-- 事件列表 -->
          <div class="events-section" v-if="getPeriodEvents(period.key).length > 0">
            <h4>⚡ 重要事件</h4>
            <div class="events-list">
              <div 
                v-for="(event, eventIndex) in getPeriodEvents(period.key)" 
                :key="eventIndex"
                class="event-item"
              >
                {{ event }}
              </div>
            </div>
          </div>
          
          <!-- 状态变化 -->
          <div class="changes-section" v-if="hasStateChanges(period.key)">
            <h4>📊 状态变化</h4>
            <div class="changes-grid">
              <div 
                v-for="change in getStateChanges(period.key)" 
                :key="change.label"
                class="change-item"
                :class="change.type"
              >
                <span class="change-label">{{ change.label }}</span>
                <span class="change-value">{{ change.value }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 一天总结 -->
    <div v-if="showDaySummary" class="day-summary">
      <h3>🌟 今日总结</h3>
      
      <div class="summary-content">
        <div class="summary-narrative">
          <h4>📖 总体叙述</h4>
          <p>{{ result.day_summary?.narrative || '今天是充实的一天。' }}</p>
        </div>
        
        <div class="summary-achievements" v-if="result.day_summary?.achievements?.length > 0">
          <h4>🏆 获得成就</h4>
          <div class="achievements-list">
            <div 
              v-for="achievement in result.day_summary.achievements" 
              :key="achievement"
              class="achievement-item"
            >
              🎉 {{ achievement }}
            </div>
          </div>
        </div>
        
        <div class="summary-consequences" v-if="result.day_summary?.consequences?.length > 0">
          <h4>⚠️ 重要后果</h4>
          <div class="consequences-list">
            <div 
              v-for="consequence in result.day_summary.consequences" 
              :key="consequence"
              class="consequence-item"
            >
              {{ consequence }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="action-buttons">
      <button
        v-if="!showDaySummary"
        @click="nextPeriod"
        class="next-btn"
        :disabled="false"
      >
        {{ currentPeriodIndex < timePeriods.length - 1 ? '下一时段' : '查看总结' }}
      </button>

      <button
        v-if="showDaySummary"
        @click="continueGame"
        class="continue-btn"
      >
        继续冒险
      </button>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'

export default {
  name: 'GameResultPanel',
  props: {
    result: {
      type: Object,
      required: true
    }
  },
  emits: ['continue-game'],
  setup(props, { emit }) {
    const currentPeriodIndex = ref(0)
    const showDaySummary = ref(false)
    
    const timePeriods = [
      { key: 'morning', name: '上午', icon: '🌅', time: '08:00 - 12:00' },
      { key: 'afternoon', name: '下午', icon: '☀️', time: '12:00 - 18:00' },
      { key: 'evening', name: '晚上', icon: '🌙', time: '18:00 - 24:00' }
    ]
    
    // 计算属性
    const progressWidth = computed(() => {
      return `${((currentPeriodIndex.value + 1) / timePeriods.length) * 100}%`
    })
    
    // 方法
    const getPeriodNarrative = (periodKey) => {
      return props.result.time_progression?.[periodKey]?.narrative || '这个时段平静地度过了。'
    }
    
    const getPeriodEvents = (periodKey) => {
      return props.result.time_progression?.[periodKey]?.events || []
    }
    
    const hasStateChanges = (periodKey) => {
      const changes = props.result.time_progression?.[periodKey]?.state_changes
      return changes && (changes.player || changes.world || changes.relationships)
    }
    
    const getStateChanges = (periodKey) => {
      const changes = props.result.time_progression?.[periodKey]?.state_changes
      if (!changes) return []
      
      const result = []
      
      // 玩家状态变化
      if (changes.player) {
        Object.entries(changes.player).forEach(([key, value]) => {
          if (value !== 0) {
            result.push({
              label: getStatLabel(key),
              value: value > 0 ? `+${value}` : `${value}`,
              type: value > 0 ? 'positive' : 'negative'
            })
          }
        })
      }
      
      // 关系变化
      if (changes.relationships) {
        Object.entries(changes.relationships).forEach(([npcId, value]) => {
          if (value !== 0) {
            result.push({
              label: `与${npcId}的关系`,
              value: value > 0 ? `+${value}` : `${value}`,
              type: value > 0 ? 'positive' : 'negative'
            })
          }
        })
      }
      
      return result
    }
    
    const getStatLabel = (statKey) => {
      const labels = {
        hp: '生命值',
        mp: '魔法值',
        strength: '力量',
        intelligence: '智力',
        agility: '敏捷',
        luck: '幸运'
      }
      return labels[statKey] || statKey
    }
    
    const nextPeriod = () => {
      if (currentPeriodIndex.value < timePeriods.length - 1) {
        currentPeriodIndex.value++
      } else {
        showDaySummary.value = true
      }
    }
    
    const continueGame = () => {
      emit('continue-game')
    }
    
    // 自动播放动画
    onMounted(() => {
      // 可以添加自动播放逻辑
    })
    
    return {
      currentPeriodIndex,
      showDaySummary,
      timePeriods,
      progressWidth,
      getPeriodNarrative,
      getPeriodEvents,
      hasStateChanges,
      getStateChanges,
      nextPeriod,
      continueGame
    }
  }
}
</script>

<style scoped>
.game-result-panel {
  background: linear-gradient(135deg, #2c3e50, #34495e);
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 8px 25px rgba(0,0,0,0.3);
  color: #ecf0f1;
  max-height: 80vh;
  overflow-y: auto;
}

.panel-header {
  text-align: center;
  margin-bottom: 25px;
}

.panel-header h2 {
  margin: 0 0 8px 0;
  color: #3498db;
  font-size: 24px;
  font-weight: 600;
}

.subtitle {
  margin: 0;
  color: #bdc3c7;
  font-size: 14px;
}

.time-progression {
  margin-bottom: 25px;
  position: relative;
}

.time-periods {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.time-period {
  display: flex;
  flex-direction: column;
  align-items: center;
  opacity: 0.5;
  transition: all 0.3s ease;
}

.time-period.active {
  opacity: 1;
}

.time-period.current {
  transform: scale(1.1);
}

.period-icon {
  font-size: 24px;
  margin-bottom: 5px;
}

.period-name {
  font-size: 12px;
  color: #bdc3c7;
  font-weight: 500;
}

.progress-line {
  height: 4px;
  background-color: #34495e;
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #3498db, #2ecc71);
  transition: width 0.5s ease;
}

.time-details {
  margin-bottom: 25px;
}

.period-detail {
  margin-bottom: 20px;
  padding: 20px;
  background-color: rgba(52, 73, 94, 0.3);
  border-radius: 8px;
  border-left: 4px solid #3498db;
  opacity: 0.7;
  transition: all 0.3s ease;
}

.period-detail.current {
  opacity: 1;
  border-left-color: #2ecc71;
  background-color: rgba(46, 204, 113, 0.1);
}

.period-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}

.period-title {
  font-size: 16px;
  font-weight: 600;
  color: #3498db;
}

.period-time {
  font-size: 12px;
  color: #95a5a6;
}

.period-content h4 {
  margin: 0 0 10px 0;
  color: #f39c12;
  font-size: 14px;
  font-weight: 600;
}

.narrative-section {
  margin-bottom: 15px;
}

.narrative-text {
  background-color: rgba(0,0,0,0.2);
  padding: 15px;
  border-radius: 6px;
  line-height: 1.6;
  font-size: 14px;
  color: #ecf0f1;
}

.events-section {
  margin-bottom: 15px;
}

.events-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.event-item {
  background-color: rgba(52, 152, 219, 0.1);
  padding: 10px 12px;
  border-radius: 4px;
  border-left: 3px solid #3498db;
  font-size: 13px;
}

.changes-section {
  margin-bottom: 15px;
}

.changes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 8px;
}

.change-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 12px;
  border-radius: 4px;
  font-size: 13px;
  font-weight: 500;
}

.change-item.positive {
  background-color: rgba(46, 204, 113, 0.2);
  border-left: 3px solid #2ecc71;
}

.change-item.negative {
  background-color: rgba(231, 76, 60, 0.2);
  border-left: 3px solid #e74c3c;
}

.change-label {
  color: #bdc3c7;
}

.change-value {
  color: #ecf0f1;
  font-weight: 600;
}

.day-summary {
  background-color: rgba(241, 196, 15, 0.1);
  border: 1px solid rgba(241, 196, 15, 0.3);
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
}

.day-summary h3 {
  margin: 0 0 15px 0;
  color: #f1c40f;
  font-size: 18px;
  text-align: center;
}

.summary-content > div {
  margin-bottom: 15px;
}

.summary-content h4 {
  margin: 0 0 8px 0;
  color: #f39c12;
  font-size: 14px;
  font-weight: 600;
}

.achievements-list,
.consequences-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.achievement-item {
  background-color: rgba(46, 204, 113, 0.2);
  padding: 8px 12px;
  border-radius: 4px;
  font-size: 13px;
}

.consequence-item {
  background-color: rgba(231, 76, 60, 0.2);
  padding: 8px 12px;
  border-radius: 4px;
  font-size: 13px;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 15px;
}

.next-btn,
.continue-btn {
  padding: 12px 24px;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.next-btn {
  background-color: #3498db;
  color: white;
}

.continue-btn {
  background-color: #2ecc71;
  color: white;
}

.next-btn:hover:not(:disabled),
.continue-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0,0,0,0.3);
}

.next-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .game-result-panel {
    padding: 20px;
  }
  
  .changes-grid {
    grid-template-columns: 1fr;
  }
  
  .period-header {
    flex-direction: column;
    gap: 5px;
    text-align: center;
  }
}
</style>
