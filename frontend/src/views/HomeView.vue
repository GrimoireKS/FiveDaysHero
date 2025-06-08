<template>
  <div class="game-start-screen">
    <div ref="pixiContainer" class="pixi-container"></div>
    
    <div class="start-button-container" v-if="!gameStarted">
      <button class="start-button" @click="startGame">开始游戏</button>
    </div>
    
    <!-- 勇者状态组件 -->
    <div class="hero-status-container" v-if="gameStarted && heroStore.day > 0">
      <hero-status />
    </div>
    
    <!-- 开场白组件 -->
    <prologue-view
      ref="prologueRef"
      v-if="showPrologue"
      @completed="onPrologueCompleted"
    />
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import * as PIXI from 'pixi.js'
import PrologueView from './prologue/PrologueView.vue'
import gameApi from '@/api/gameApi'
import HeroStatus from '@/components/HeroStatus.vue'
import { useHeroStore } from '@/store/heroStore'

export default {
  name: 'HomeView',
  components: {
    PrologueView,
    HeroStatus
  },
  setup() {
    const router = useRouter()
    const heroStore = useHeroStore()
    const pixiContainer = ref(null)
    const prologueRef = ref(null)
    const gameStarted = ref(false)
    const showPrologue = ref(false)
    const currentDay = ref(0)
    
    // 开始游戏
    const startGame = () => {
      console.log('点击开始游戏按钮')
      gameStarted.value = true
      showPrologue.value = true
      console.log('游戏状态已更新，gameStarted:', gameStarted.value, 'showPrologue:', showPrologue.value)
      
      // 测试API连接
      gameApi.getPrologue()
        .then(response => {
          console.log('在HomeView中测试开场白API成功:', response.data)
        })
        .catch(error => {
          console.error('在HomeView中测试开场白API失败:', error)
        })
    }
    
    // 开场白完成后的回调
    const onPrologueCompleted = async (playerResponse) => {
      console.log('开场白完成，玩家回应:', playerResponse)
      // 不要立即隐藏开场白组件，让它显示"正在创建世界"的提示

      try {
        // 调用后端创建世界接口
        const response = await gameApi.createWorld(playerResponse)

        if (response.data.status === 'success') {
          const gameId = response.data.game_id
          console.log('游戏创建成功，游戏ID:', gameId)

          // 完成进度条
          if (prologueRef.value && prologueRef.value.completeProgress) {
            prologueRef.value.completeProgress()
          }

          // 等待一下让用户看到完成状态，然后隐藏开场白组件
          setTimeout(() => {
            showPrologue.value = false
            // 跳转到主游戏界面
            router.push(`/game/${gameId}`)
          }, 1000)
        } else {
          console.error('游戏创建失败:', response.data.message)
          // 隐藏开场白组件
          showPrologue.value = false
          alert('游戏创建失败，请重试')
        }
      } catch (error) {
        console.error('创建游戏世界失败:', error)
        // 隐藏开场白组件
        showPrologue.value = false
        alert('网络错误，请检查连接后重试')
      }
    }
    

    
    onMounted(() => {
      if (pixiContainer.value) {
        // 创建PIXI应用
        const app = new PIXI.Application({
          width: window.innerWidth,
          height: window.innerHeight,
          backgroundColor: 0x000000,
          resolution: window.devicePixelRatio || 1,
          autoDensity: true,
          antialias: true
        })
        
        // 将PIXI应用添加到DOM
        pixiContainer.value.appendChild(app.view)
        
        // 加载背景图片
        const backgroundTexture = PIXI.Texture.from('/images/scene_sunny.png')
        const background = new PIXI.Sprite(backgroundTexture)
        
        // 计算保持原始比例的尺寸，确保图片完整显示
        const setupBackgroundScale = () => {
          // 获取屏幕和图片的宽高比
          const screenRatio = app.screen.width / app.screen.height
          const imageRatio = background.width / background.height
          
          // 计算缩放比例，始终选择较小的缩放比例，确保图片完整显示
          const scaleX = app.screen.width / background.width
          const scaleY = app.screen.height / background.height
          const scale = Math.min(scaleX, scaleY)
          
          // 设置图片尺寸
          background.width = background.width * scale
          background.height = background.height * scale
          
          // 居中背景图片
          background.x = (app.screen.width - background.width) / 2
          background.y = (app.screen.height - background.height) / 2
          
          // 将按钮容器定位在图片内部的底部
          const startButtonContainer = document.querySelector('.start-button-container')
          if (startButtonContainer) {
            startButtonContainer.style.bottom = `${(app.screen.height - background.height) / 2 + 50}px`
            startButtonContainer.style.width = `${background.width}px`
            startButtonContainer.style.left = `${background.x}px`
          }
        }
        
        // 当纹理加载完成后设置比例
        backgroundTexture.baseTexture.on('loaded', setupBackgroundScale)
        
        // 如果纹理已经加载完成，直接设置
        if (backgroundTexture.baseTexture.valid) {
          setupBackgroundScale()
        }
        
        // 添加背景到舞台
        app.stage.addChild(background)
        
        // 添加窗口大小调整事件
        window.addEventListener('resize', () => {
          app.renderer.resize(window.innerWidth, window.innerHeight)
          
          // 重新计算背景图片的尺寸和位置，确保图片完整显示
          const originalWidth = backgroundTexture.width
          const originalHeight = backgroundTexture.height
          
          // 计算缩放比例，始终选择较小的缩放比例，确保图片完整显示
          const scaleX = app.screen.width / originalWidth
          const scaleY = app.screen.height / originalHeight
          const scale = Math.min(scaleX, scaleY)
          
          // 设置图片尺寸
          background.width = originalWidth * scale
          background.height = originalHeight * scale
          
          // 居中背景图片
          background.x = (app.screen.width - background.width) / 2
          background.y = (app.screen.height - background.height) / 2
          
          // 将按钮容器定位在图片内部的底部
          const startButtonContainer = document.querySelector('.start-button-container')
          if (startButtonContainer) {
            startButtonContainer.style.bottom = `${(app.screen.height - background.height) / 2 + 50}px`
            startButtonContainer.style.width = `${background.width}px`
            startButtonContainer.style.left = `${background.x}px`
          }
        })
      }
    })
    
    return {
      pixiContainer,
      prologueRef,
      startGame,
      gameStarted,
      showPrologue,
      currentDay,
      onPrologueCompleted,
      heroStore
    }
  }
}
</script>

<style scoped>
.game-start-screen {
  position: relative;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
}

.pixi-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.start-button-container {
  position: absolute;
  bottom: 100px;
  left: 0;
  right: 0;
  display: flex;
  justify-content: center;
  z-index: 10;
}

.start-button {
  padding: 15px 40px;
  font-size: 24px;
  font-family: 'Press Start 2P', cursive, sans-serif;
  background-color: rgba(0, 0, 0, 0.7);
  color: #fff;
  border: 3px solid #ff6b6b;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  text-shadow: 2px 2px 0px #000;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
}

.start-button:hover {
  background-color: rgba(255, 107, 107, 0.8);
  transform: scale(1.05);
}

.start-button:active {
  transform: scale(0.98);
}

.hero-status-container {
  position: absolute;
  top: 20px;
  right: 20px;
  z-index: 15;
  transition: all 0.3s ease;
}
</style>
