<template>
  <div class="overlay">
    <div class="prologue-container">
      <h2 class="prologue-title">五日勇者</h2>

      <div class="prologue-text" v-if="prologue">
        <p v-for="(line, index) in prologueLines" :key="index" :style="{ animationDelay: index * 0.3 + 's' }">{{ line }}</p>
      </div>
      <div class="loading" v-else>正在加载开场白<span class="loading-dots"><span>.</span><span>.</span><span>.</span></span></div>

      <div class="player-input-container" v-if="!isSubmitting">
        <div class="input-label">请描述您的勇者：</div>
        <textarea
          v-model="playerInput"
          placeholder="例如：我是一个勇敢的战士，手持长剑，身穿皮甲..."
          maxlength="200"
          :disabled="!prologue"
          @keyup.enter="canSubmit && submitResponse()"
        ></textarea>
        <div class="input-footer">
          <div class="char-counter" :class="{ 'char-limit': playerInput.length >= 180 }">
            {{ playerInput.length }}/200
          </div>
          <button
            class="submit-button"
            @click="submitResponse"
            :disabled="!canSubmit || !prologue"
          >开始冒险</button>
        </div>
      </div>

      <div class="creating-world" v-if="isSubmitting">
        <div class="loading-text">正在创建世界<span class="loading-dots"><span>.</span><span>.</span><span>.</span></span></div>
        <div class="progress-container">
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: progressWidth }"></div>
          </div>
          <div class="progress-text">{{ progressText }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import gameApi from '@/api/gameApi'
import { useHeroStore } from '@/store/heroStore'

export default {
  name: 'PrologueView',
  emits: ['completed'],
  expose: ['completeProgress'],
  setup(props, { emit }) {
    const router = useRouter()
    const heroStore = useHeroStore()
    const prologue = ref(null)
    const playerInput = ref('')
    const isSubmitting = ref(false)
    const progressWidth = ref('0%')
    const progressText = ref('正在分析勇者信息...')
    
    // 计算属性：将开场白文本分割成行
    const prologueLines = computed(() => {
      if (!prologue.value) return []
      return prologue.value.split('\n').filter(line => line.trim() !== '')
    })
    
    // 计算属性：是否可以提交玩家输入
    const canSubmit = computed(() => {
      return playerInput.value.trim().length > 0
    })
    
    // 获取开场白
    const fetchPrologue = async () => {
      console.log('开始获取开场白...')
      try {
        // 使用gameApi从后端获取开场白
        const response = await gameApi.getPrologue()
        console.log('获取开场白成功:', response.data)
        
        if (response.data && response.data.prologue) {
          prologue.value = response.data.prologue
          console.log('开场白内容已设置:', prologue.value)
        } else if (response.data && response.data.status === 'success') {
          prologue.value = response.data.prologue || '开场白内容为空'
          console.log('开场白内容为空，已设置默认值')
        } else {
          throw new Error('返回数据格式不正确')
        }
      } catch (error) {
        console.error('获取开场白失败:', error)
        console.log('使用默认开场白')
        // 使用更新后的开场白文本
        prologue.value = '魔王向国王宣告，五日之后，将抢走神圣教堂的遗宝。\n\n国王征召勇士，共同对付魔王。\n\n你是其中的一员，来到了神圣教堂所在的村庄。\n\n但你只有五天的时间来准备...\n\n你将如何面对这个挑战？'
      }
    }
    
    // 提交玩家回应
    const submitResponse = () => {
      if (!canSubmit.value) return

      // 设置提交状态为true，显示"正在创建世界"提示
      isSubmitting.value = true

      // 模拟进度条
      simulateProgress()

      // 直接通知父组件，由父组件处理世界创建
      emit('completed', playerInput.value)
    }

    // 模拟进度条
    const simulateProgress = () => {
      const steps = [
        { progress: '15%', text: '正在分析勇者信息...' },
        { progress: '30%', text: '正在生成世界背景...' },
        { progress: '50%', text: '正在创建NPC角色...' },
        { progress: '70%', text: '正在初始化游戏状态...' },
        { progress: '85%', text: '正在保存游戏数据...' },
        { progress: '95%', text: '即将完成...' }
      ]

      let currentStep = 0
      const interval = setInterval(() => {
        if (currentStep < steps.length) {
          progressWidth.value = steps[currentStep].progress
          progressText.value = steps[currentStep].text
          currentStep++
        } else {
          // 不要自动到100%，让实际API完成时再处理
          clearInterval(interval)
        }
      }, 3000) // 每3秒更新一次，总共约18秒，给API留足时间
    }

    // 完成进度条（由父组件调用）
    const completeProgress = () => {
      progressWidth.value = '100%'
      progressText.value = '世界创建完成！'
    }

    // 组件挂载时加载开场白
    onMounted(() => {
      console.log('PrologueView组件已挂载')
      fetchPrologue()
    })
    
    return {
      prologue,
      prologueLines,
      playerInput,
      canSubmit,
      isSubmitting,
      progressWidth,
      progressText,
      submitResponse,
      completeProgress,
      heroStore
    }
  }
}
</script>

<style scoped>
/* 灰色蒙版样式 */
.overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.7);
  z-index: 20;
  display: flex;
  justify-content: center;
  align-items: center;
  animation: fadeIn 0.5s ease-in-out;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* 开场白容器样式 */
.prologue-container {
  width: 80%;
  max-width: 800px;
  background-color: rgba(0, 0, 0, 0.85);
  border: 3px solid #ff6b6b;
  border-radius: 10px;
  padding: 30px;
  color: #fff;
  font-family: 'Microsoft YaHei', sans-serif;
  box-shadow: 0 0 30px rgba(255, 107, 107, 0.6);
  display: flex;
  flex-direction: column;
  gap: 20px;
  position: relative;
  overflow: hidden;
}

.prologue-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, rgba(255, 107, 107, 0.1) 0%, transparent 100%);
  pointer-events: none;
}

/* 标题样式 */
.prologue-title {
  text-align: center;
  font-size: 32px;
  margin: 0 0 20px 0;
  color: #ff6b6b;
  text-shadow: 0 0 10px rgba(255, 107, 107, 0.7);
  font-family: 'Microsoft YaHei', sans-serif;
  letter-spacing: 2px;
  animation: titleGlow 2s infinite alternate;
}

@keyframes titleGlow {
  from { text-shadow: 0 0 10px rgba(255, 107, 107, 0.7); }
  to { text-shadow: 0 0 20px rgba(255, 107, 107, 0.9); }
}

/* 开场白文本样式 */
.prologue-text {
  font-size: 18px;
  line-height: 1.8;
  letter-spacing: 1px;
  text-align: justify;
  margin-bottom: 25px;
  padding: 0 10px;
}

.prologue-text p {
  margin-bottom: 15px;
  animation: textFadeIn 1s ease-in-out both;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
}

@keyframes textFadeIn {
  from { opacity: 0; transform: translateY(15px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 加载提示样式 */
.loading, .creating-world {
  text-align: center;
  font-size: 1.2rem;
  margin: 2rem 0;
  color: #fff;
}

.loading-dots span {
  display: inline-block;
  animation: dots 1.5s infinite;
  margin: 0 2px;
}

.loading-dots span:nth-child(2) {
  animation-delay: 0.5s;
}

.loading-dots span:nth-child(3) {
  animation-delay: 1s;
}

.creating-world {
  font-size: 1.5rem;
  margin: 3rem 0;
  color: #ffcc00;
  text-shadow: 0 0 10px rgba(255, 204, 0, 0.7);
}

.progress-container {
  margin-top: 2rem;
  width: 100%;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background-color: rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 1rem;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #ffcc00, #ff6b6b);
  border-radius: 4px;
  transition: width 0.5s ease;
  box-shadow: 0 0 10px rgba(255, 204, 0, 0.5);
}

.progress-text {
  text-align: center;
  font-size: 1rem;
  color: #fff;
  opacity: 0.8;
}

@keyframes dotFade {
  0%, 100% { opacity: 0.2; transform: translateY(0); }
  50% { opacity: 1; transform: translateY(-2px); }
}

/* 玩家输入区域样式 */
.player-input-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
  width: 100%;
  background-color: rgba(0, 0, 0, 0.3);
  padding: 20px;
  border-radius: 8px;
  border-left: 3px solid #ff6b6b;
}

.input-label {
  font-size: 16px;
  color: #ff6b6b;
  font-weight: bold;
  margin-bottom: 5px;
}

.player-input-container textarea {
  width: 100%;
  height: 100px;
  padding: 15px;
  border-radius: 5px;
  border: 2px solid #555;
  background-color: rgba(0, 0, 0, 0.5);
  color: #fff;
  font-size: 16px;
  font-family: 'Microsoft YaHei', sans-serif;
  resize: none;
  transition: all 0.3s;
}

.player-input-container textarea:focus {
  outline: none;
  border-color: #ff6b6b;
  box-shadow: 0 0 15px rgba(255, 107, 107, 0.5);
}

.player-input-container textarea:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.input-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.char-counter {
  font-size: 14px;
  color: #aaa;
  transition: all 0.3s;
}

.char-limit {
  color: #ff6b6b;
  font-weight: bold;
}

.submit-button {
  padding: 12px 25px;
  font-size: 18px;
  background-color: #ff6b6b;
  color: #fff;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: all 0.3s;
  font-weight: bold;
  letter-spacing: 1px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
}

.submit-button:hover:not(:disabled) {
  background-color: #ff8c8c;
  transform: translateY(-3px);
  box-shadow: 0 6px 10px rgba(0, 0, 0, 0.4);
}

.submit-button:active:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.submit-button:disabled {
  background-color: #777;
  cursor: not-allowed;
  opacity: 0.7;
  box-shadow: none;
}
</style>
