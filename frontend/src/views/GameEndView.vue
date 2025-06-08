<template>
  <div class="game-end-container">
    <div class="end-background">
      <div class="end-content">
        <div class="end-header">
          <h1 class="end-title">🎉 五日冒险结束 🎉</h1>
          <p class="end-subtitle">您的传奇故事已经完成</p>
        </div>

        <div class="game-summary">
          <div class="summary-section">
            <h2>📊 冒险统计</h2>
            <div class="stats-grid">
              <div class="stat-card">
                <div class="stat-icon">📅</div>
                <div class="stat-info">
                  <div class="stat-label">冒险天数</div>
                  <div class="stat-value">5 天</div>
                </div>
              </div>
              
              <div class="stat-card">
                <div class="stat-icon">⚔️</div>
                <div class="stat-info">
                  <div class="stat-label">最终力量</div>
                  <div class="stat-value">{{ finalStats.strength || 'N/A' }}</div>
                </div>
              </div>
              
              <div class="stat-card">
                <div class="stat-icon">🧠</div>
                <div class="stat-info">
                  <div class="stat-label">最终智力</div>
                  <div class="stat-value">{{ finalStats.intelligence || 'N/A' }}</div>
                </div>
              </div>
              
              <div class="stat-card">
                <div class="stat-icon">💨</div>
                <div class="stat-info">
                  <div class="stat-label">最终敏捷</div>
                  <div class="stat-value">{{ finalStats.agility || 'N/A' }}</div>
                </div>
              </div>
              
              <div class="stat-card">
                <div class="stat-icon">🍀</div>
                <div class="stat-info">
                  <div class="stat-label">最终幸运</div>
                  <div class="stat-value">{{ finalStats.luck || 'N/A' }}</div>
                </div>
              </div>
              
              <div class="stat-card">
                <div class="stat-icon">❤️</div>
                <div class="stat-info">
                  <div class="stat-label">最终生命</div>
                  <div class="stat-value">{{ finalStats.hp || 'N/A' }}</div>
                </div>
              </div>
            </div>
          </div>

          <div class="summary-section">
            <h2>🏆 获得成就</h2>
            <div class="achievements-list">
              <div 
                v-for="achievement in achievements" 
                :key="achievement"
                class="achievement-item"
              >
                🎖️ {{ achievement }}
              </div>
              <div v-if="achievements.length === 0" class="no-achievements">
                暂无特殊成就
              </div>
            </div>
          </div>

          <div class="summary-section">
            <h2>👥 人物关系</h2>
            <div class="relationships-list">
              <div 
                v-for="(npc, npcId) in finalRelationships" 
                :key="npcId"
                class="relationship-item"
              >
                <span class="npc-name">{{ npc.name }}</span>
                <span class="relationship-value" :class="getRelationshipClass(npc.relationship)">
                  {{ getRelationshipText(npc.relationship) }}
                </span>
              </div>
              <div v-if="Object.keys(finalRelationships).length === 0" class="no-relationships">
                未建立特殊关系
              </div>
            </div>
          </div>

          <div class="summary-section">
            <h2>📖 冒险回顾</h2>
            <div class="adventure-review">
              <p class="review-text">
                在这五天的冒险中，您经历了许多挑战和机遇。
                每一个选择都塑造了您独特的冒险故事。
                无论结果如何，这都是一段值得铭记的传奇经历。
              </p>
            </div>
          </div>
        </div>

        <div class="end-actions">
          <button @click="restartGame" class="action-btn restart-btn">
            🔄 重新开始
          </button>
          <button @click="goHome" class="action-btn home-btn">
            🏠 返回主页
          </button>
        </div>

        <div class="credits">
          <p>感谢您游玩《五日勇者》</p>
          <p class="credits-small">一个由AI驱动的文本冒险游戏</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import gameApi from '@/api/gameApi'

export default {
  name: 'GameEndView',
  setup() {
    const route = useRoute()
    const router = useRouter()
    
    const finalStats = ref({})
    const finalRelationships = ref({})
    const achievements = ref([])
    const gameId = ref('')
    
    // 方法
    const getRelationshipClass = (value) => {
      if (value > 20) return 'positive'
      if (value < -20) return 'negative'
      return 'neutral'
    }
    
    const getRelationshipText = (value) => {
      if (value > 50) return '亲密'
      if (value > 20) return '友好'
      if (value > -20) return '中性'
      if (value > -50) return '冷淡'
      return '敌对'
    }
    
    const restartGame = () => {
      router.push('/')
    }
    
    const goHome = () => {
      router.push('/')
    }
    
    const loadGameEndData = async () => {
      gameId.value = route.params.gameId
      
      if (!gameId.value) {
        console.error('无效的游戏ID')
        router.push('/')
        return
      }
      
      try {
        // 获取最终游戏状态
        const response = await gameApi.getGameState(gameId.value)
        
        if (response.data) {
          const gameState = response.data
          
          // 设置最终统计数据
          finalStats.value = gameState.player || {}
          finalRelationships.value = gameState.npc || {}
          
          // 从游戏历史中提取成就（如果有的话）
          if (gameState.history && gameState.history.length > 0) {
            const allAchievements = []
            gameState.history.forEach(day => {
              if (day.achievements) {
                allAchievements.push(...day.achievements)
              }
            })
            achievements.value = [...new Set(allAchievements)] // 去重
          }
        }
      } catch (error) {
        console.error('加载游戏结束数据失败:', error)
        // 即使加载失败也显示基本的结束页面
      }
    }
    
    onMounted(() => {
      loadGameEndData()
    })
    
    return {
      finalStats,
      finalRelationships,
      achievements,
      getRelationshipClass,
      getRelationshipText,
      restartGame,
      goHome
    }
  }
}
</script>

<style scoped>
.game-end-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.end-background {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
  max-width: 800px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
}

.end-content {
  padding: 40px;
  color: white;
}

.end-header {
  text-align: center;
  margin-bottom: 40px;
}

.end-title {
  font-size: 2.5rem;
  margin: 0 0 10px 0;
  background: linear-gradient(45deg, #ffd700, #ffed4e);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-weight: bold;
}

.end-subtitle {
  font-size: 1.2rem;
  margin: 0;
  opacity: 0.9;
}

.game-summary {
  margin-bottom: 40px;
}

.summary-section {
  margin-bottom: 30px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 20px;
}

.summary-section h2 {
  margin: 0 0 20px 0;
  font-size: 1.4rem;
  color: #ffd700;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.stat-card {
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 15px;
  gap: 15px;
}

.stat-icon {
  font-size: 2rem;
}

.stat-info {
  flex: 1;
}

.stat-label {
  font-size: 0.9rem;
  opacity: 0.8;
  margin-bottom: 5px;
}

.stat-value {
  font-size: 1.2rem;
  font-weight: bold;
  color: #ffd700;
}

.achievements-list,
.relationships-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.achievement-item,
.relationship-item {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  padding: 12px 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.npc-name {
  font-weight: 500;
}

.relationship-value {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.9rem;
  font-weight: 500;
}

.relationship-value.positive {
  background-color: #27ae60;
}

.relationship-value.neutral {
  background-color: #95a5a6;
}

.relationship-value.negative {
  background-color: #e74c3c;
}

.no-achievements,
.no-relationships {
  text-align: center;
  opacity: 0.7;
  font-style: italic;
  padding: 20px;
}

.adventure-review {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 20px;
}

.review-text {
  line-height: 1.6;
  margin: 0;
  font-size: 1.1rem;
}

.end-actions {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-bottom: 30px;
}

.action-btn {
  padding: 15px 30px;
  border: none;
  border-radius: 8px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  color: white;
}

.restart-btn {
  background: linear-gradient(45deg, #3498db, #2980b9);
}

.home-btn {
  background: linear-gradient(45deg, #2ecc71, #27ae60);
}

.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
}

.credits {
  text-align: center;
  opacity: 0.8;
  border-top: 1px solid rgba(255, 255, 255, 0.2);
  padding-top: 20px;
}

.credits p {
  margin: 5px 0;
}

.credits-small {
  font-size: 0.9rem;
  opacity: 0.7;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .end-content {
    padding: 20px;
  }
  
  .end-title {
    font-size: 2rem;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .end-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .action-btn {
    width: 200px;
  }
}
</style>
