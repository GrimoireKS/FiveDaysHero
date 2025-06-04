<template>
  <day-view :day-number="5" :visible="visible" @completed="onCompleted">
    <div class="day-specific-content">
      <p>勇者的最终日，魔王已经降临，你必须面对最终的挑战。</p>
      
      <div class="day-choices">
        <h3>你将如何面对魔王？</h3>
        <div class="choice-list">
          <div 
            v-for="(choice, index) in choices" 
            :key="index" 
            class="choice-item"
            :class="{ 'selected': selectedChoice === index }"
            @click="selectChoice(index)"
          >
            {{ choice.text }}
          </div>
        </div>
      </div>
    </div>
  </day-view>
</template>

<script>
import { ref, defineComponent } from 'vue'
import DayView from './DayView.vue'
import axios from 'axios'

export default defineComponent({
  name: 'Day5View',
  components: {
    DayView
  },
  props: {
    visible: {
      type: Boolean,
      default: false
    }
  },
  emits: ['completed'],
  setup(props, { emit }) {
    const choices = [
      { text: '正面强攻', value: 'attack' },
      { text: '寻找弱点', value: 'weakness' },
      { text: '尝试说服魔王', value: 'persuade' }
    ]
    
    const selectedChoice = ref(null)
    
    const selectChoice = (index) => {
      selectedChoice.value = index
    }
    
    const onCompleted = async () => {
      if (selectedChoice.value !== null) {
        try {
          // 将选择发送到后端
          await axios.post('/api/game/day5', {
            choice: choices[selectedChoice.value].value
          })
        } catch (error) {
          console.error('提交第五天选择失败:', error)
        }
      }
      
      // 无论API调用是否成功，都通知父组件日程已完成
      emit('completed', {
        day: 5,
        choice: selectedChoice.value !== null ? choices[selectedChoice.value].value : null
      })
    }
    
    return {
      choices,
      selectedChoice,
      selectChoice,
      onCompleted
    }
  }
})
</script>

<style scoped>
.day-specific-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.day-choices {
  margin-top: 20px;
}

.day-choices h3 {
  color: #ff6b6b;
  margin-bottom: 15px;
  font-size: 20px;
  text-align: center;
}

.choice-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.choice-item {
  padding: 15px;
  background-color: rgba(0, 0, 0, 0.5);
  border: 2px solid #555;
  border-radius: 5px;
  cursor: pointer;
  transition: all 0.3s;
}

.choice-item:hover {
  border-color: #ff6b6b;
  background-color: rgba(255, 107, 107, 0.1);
}

.choice-item.selected {
  border-color: #ff6b6b;
  background-color: rgba(255, 107, 107, 0.2);
  box-shadow: 0 0 15px rgba(255, 107, 107, 0.3);
}
</style>
