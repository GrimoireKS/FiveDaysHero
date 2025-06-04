<template>
  <div class="game-container">
    <div class="game-header">
      <div class="day-counter">第 {{ gameState.day }} 天</div>
      <div class="weather">{{ gameState.world.weather }}</div>
    </div>
    
    <div class="game-content">
      <div class="game-scene">
        <!-- 这里将使用PixiJS渲染游戏场景 -->
        <div ref="pixiContainer" class="pixi-container"></div>
      </div>
      
      <div class="game-narrative">
        <div class="narrative-text">{{ currentNarrative }}</div>
      </div>
      
      <div class="game-input">
        <textarea 
          v-model="playerAction" 
          placeholder="输入你的行动（不超过100字）..." 
          maxlength="100"
          @keyup="checkLength"
        ></textarea>
        <div class="char-counter">{{ playerAction.length }}/100</div>
        <button @click="submitAction" :disabled="!canSubmit">确认行动</button>
      </div>
    </div>
    
    <div class="game-sidebar">
      <div class="player-info">
        <h3>{{ gameState.player.name }}</h3>
        <div class="stats">
          <div class="stat">力量: {{ gameState.player.stats.strength }}</div>
          <div class="stat">智力: {{ gameState.player.stats.intelligence }}</div>
          <div class="stat">魅力: {{ gameState.player.stats.charisma }}</div>
        </div>
      </div>
      
      <div class="inventory">
        <h3>物品栏</h3>
        <div v-if="gameState.player.inventory.length === 0">空</div>
        <div v-else class="inventory-items">
          <div v-for="(item, index) in gameState.player.inventory" :key="index" class="item">
            {{ item.name }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, computed } from 'vue'
import * as PIXI from 'pixi.js'

export default {
  name: 'GameView',
  setup() {
    const pixiContainer = ref(null)
    const playerAction = ref('')
    const currentNarrative = ref('你来到了村庄，魔王将在五天后降临。你需要做好准备...')
    
    // 初始化游戏状态
    const gameState = reactive({
      day: 1,
      player: {
        name: '勇者',
        stats: {
          strength: 5,
          intelligence: 5,
          charisma: 5
        },
        inventory: []
      },
      world: {
        weather: '晴天',
        villageStatus: '平静',
        npcRelations: {}
      }
    })
    
    // 检查输入长度
    const checkLength = () => {
      if (playerAction.value.length > 100) {
        playerAction.value = playerAction.value.substring(0, 100)
      }
    }
    
    // 是否可以提交行动
    const canSubmit = computed(() => {
      return playerAction.value.trim().length > 0
    })
    
    // 提交玩家行动
    const submitAction = async () => {
      if (!canSubmit.value) return
      
      try {
        const response = await fetch('/api/game/action', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            action: playerAction.value,
            day: gameState.day,
            gameState: gameState
          })
        })
        
        const data = await response.json()
        
        if (data.status === 'success') {
          // 更新游戏状态
          currentNarrative.value = data.result.narrative
          
          // 更新玩家状态
          Object.assign(gameState.player.stats, data.result.stateChanges.playerStats)
          
          // 更新世界状态
          Object.assign(gameState.world, data.result.stateChanges.worldState)
          
          // 进入下一天
          gameState.day += 1
          
          // 清空输入
          playerAction.value = ''
        }
      } catch (error) {
        console.error('提交行动失败:', error)
        alert('提交行动失败，请重试')
      }
    }
    
    // 初始化PixiJS
    onMounted(() => {
      if (pixiContainer.value) {
        const app = new PIXI.Application({
          width: 640,
          height: 360,
          backgroundColor: 0x1099bb,
          resolution: window.devicePixelRatio || 1
        })
        
        pixiContainer.value.appendChild(app.view)
        
        // 创建简单的背景
        const background = PIXI.Sprite.from('/assets/village_bg.png')
        background.width = app.screen.width
        background.height = app.screen.height
        app.stage.addChild(background)
        
        // 这里可以添加更多的游戏元素
      }
    })
    
    return {
      pixiContainer,
      playerAction,
      currentNarrative,
      gameState,
      checkLength,
      canSubmit,
      submitAction
    }
  }
}
</script>

<style scoped>
.game-container {
  display: grid;
  grid-template-columns: 3fr 1fr;
  grid-template-rows: auto 1fr;
  height: 100vh;
  background-color: #222;
  color: #eee;
  font-family: 'Courier New', monospace;
}

.game-header {
  grid-column: 1 / -1;
  display: flex;
  justify-content: space-between;
  padding: 10px 20px;
  background-color: #333;
  border-bottom: 2px solid #ff6b6b;
}

.day-counter, .weather {
  font-size: 18px;
  font-weight: bold;
}

.game-content {
  display: flex;
  flex-direction: column;
  padding: 20px;
}

.game-scene {
  flex: 1;
  margin-bottom: 20px;
}

.pixi-container {
  width: 100%;
  height: 360px;
  background-color: #000;
}

.game-narrative {
  background-color: #333;
  padding: 15px;
  border-radius: 5px;
  margin-bottom: 20px;
  min-height: 100px;
  max-height: 200px;
  overflow-y: auto;
}

.narrative-text {
  line-height: 1.6;
}

.game-input {
  position: relative;
}

textarea {
  width: 100%;
  height: 80px;
  background-color: #444;
  color: #fff;
  border: 1px solid #666;
  border-radius: 5px;
  padding: 10px;
  resize: none;
  font-family: inherit;
}

.char-counter {
  position: absolute;
  bottom: 45px;
  right: 10px;
  font-size: 12px;
  color: #aaa;
}

button {
  margin-top: 10px;
  padding: 8px 16px;
  background-color: #ff6b6b;
  color: #fff;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: bold;
  transition: background-color 0.3s;
}

button:hover:not(:disabled) {
  background-color: #ff8c8c;
}

button:disabled {
  background-color: #666;
  cursor: not-allowed;
}

.game-sidebar {
  padding: 20px;
  background-color: #2a2a2a;
  border-left: 1px solid #444;
}

.player-info, .inventory {
  margin-bottom: 30px;
}

h3 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #ff6b6b;
  border-bottom: 1px solid #444;
  padding-bottom: 5px;
}

.stats {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stat {
  background-color: #333;
  padding: 5px 10px;
  border-radius: 3px;
}

.inventory-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.item {
  background-color: #333;
  padding: 5px 10px;
  border-radius: 3px;
}
</style>
