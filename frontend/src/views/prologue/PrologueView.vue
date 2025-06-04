<template>
  <div class="overlay" v-if="visible">
    <div class="prologue-container">
      <h2 class="prologue-title">五日勇者</h2>
      
      <div class="prologue-text" v-if="prologue">
        <p v-for="(line, index) in prologueLines" :key="index" :style="{ animationDelay: index * 0.3 + 's' }">{{ line }}</p>
      </div>
      <div class="loading" v-else>正在加载开场白<span class="loading-dots"><span>.</span><span>.</span><span>.</span></span></div>
      
      <div class="player-input-container" v-if="!isSubmitting">
        <div class="input-label">请描述勇者：</div>
        <textarea 
          v-model="playerInput" 
          placeholder="请输入勇者信息..." 
          maxlength="100"
          :disabled="!prologue"
          @keyup.enter="canSubmit && submitResponse()"
        ></textarea>
        <div class="input-footer">
          <div class="char-counter" :class="{ 'char-limit': playerInput.length >= 90 }">
            {{ playerInput.length }}/100
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
  props: {
    visible: {
      type: Boolean,
      default: false
    }
  },
  emits: ['completed'],
  setup(props, { emit }) {
    const router = useRouter()
    const heroStore = useHeroStore()
    const prologue = ref(null)
    const playerInput = ref('')
    const isSubmitting = ref(false)
    
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
    const submitResponse = async () => {
      if (!canSubmit.value) return
      
      // 设置提交状态为true，显示"正在创建世界"提示
      isSubmitting.value = true
      
      try {
        // 使用新的createWorld接口，一次性创建世界和勇者信息
        console.log('提交玩家回应并创建世界:', playerInput.value)
        const response = await gameApi.createWorld(playerInput.value)
        console.log('世界创建成功:', response.data)
        
        if (response.data && response.data.status === 'success') {
          const heroData = response.data.hero
          const worldInfo = response.data.world
          
          // 设置勇者基本信息
          heroStore.setBasicInfo({
            name: heroData.basic_info.name,
            gender: heroData.basic_info.gender,
            profession: heroData.basic_info.profession,
            age: heroData.basic_info.age
          })
          
          // 设置勇者能力值
          heroStore.setStats({
            strength: heroData.stats.strength,
            intelligence: heroData.stats.intelligence,
            agility: heroData.stats.agility,
            luck: heroData.stats.luck
          })
          
          // 设置勇者生命值和魔法值
          heroStore.updateStatus({
            hp: heroData.stats.hp,
            mp: heroData.stats.mp
          })
          
          // 设置勇者装备
          const equipment = heroData.equipment
          
          // 添加头部装备
          if (equipment.head) {
            heroStore.addEquipment('head', equipment.head)
          }
          
          // 添加胸部装备
          if (equipment.chest) {
            heroStore.addEquipment('chest', equipment.chest)
          }
          
          // 添加腿部装备
          if (equipment.legs) {
            heroStore.addEquipment('legs', equipment.legs)
          }
          
          // 添加手部装备
          equipment.hands.forEach(item => {
            heroStore.addEquipment('hands', item)
          })
          
          // 添加脚部装备
          if (equipment.feet) {
            heroStore.addEquipment('feet', equipment.feet)
          }
          
          // 添加脖子装备
          if (equipment.neck) {
            heroStore.addEquipment('neck', equipment.neck)
          }
          
          // 添加手腕装备
          equipment.wrists.forEach(item => {
            heroStore.addEquipment('wrists', item)
          })
          
          console.log('勇者信息已保存到store:', heroStore.$state)
          console.log('世界信息已生成:', worldInfo)
          
          // 保存世界信息到游戏状态（如果有相应的store）
          // TODO: 如果需要，添加世界信息的store
        }
        
        // 提交成功后通知父组件
        emit('completed', playerInput.value)
      } catch (error) {
        console.error('提交回应失败:', error)
        
        // 如果后端接口不可用，使用前端提取的信息
        console.log('使用前端提取的勇者信息')
        const extractedInfo = heroStore.extractHeroInfo(playerInput.value)
        console.log('前端提取到的勇者信息:', extractedInfo)
        
        // 通知父组件
        emit('completed', playerInput.value)
      } finally {
        // 无论成功或失败，最终都会由父组件处理，这里不需要重置isSubmitting
        // 因为组件会被隐藏或销毁
      }
    }
    
    // 监听 visible 属性变化，当变为 true 时加载开场白
    onMounted(() => {
      console.log('PrologueView组件已挂载, visible:', props.visible)
      fetchPrologue()
    })
    
    // 监听visible属性变化
    watch(() => props.visible, (newValue) => {
      console.log('visible属性变化:', newValue)
      if (newValue && !prologue.value) {
        console.log('visible变为true且prologue为空，重新获取开场白')
        fetchPrologue()
      }
    })
    
    return {
      prologue,
      prologueLines,
      playerInput,
      canSubmit,
      isSubmitting,
      submitResponse,
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
