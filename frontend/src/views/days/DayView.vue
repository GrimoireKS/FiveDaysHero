<template>
  <div class="day-view" v-if="visible">
    <div class="day-container">
      <h2 class="day-title">第{{ dayNumber }}天</h2>
      
      <div class="day-content">
        <!-- 这里将根据每天的具体内容进行定制 -->
        <slot></slot>
      </div>
      
      <div class="day-actions">
        <button class="action-button" @click="completeDay">继续</button>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'DayView',
  props: {
    dayNumber: {
      type: Number,
      required: true
    },
    visible: {
      type: Boolean,
      default: false
    }
  },
  emits: ['completed'],
  setup(props, { emit }) {
    const completeDay = () => {
      emit('completed', props.dayNumber)
    }
    
    return {
      completeDay
    }
  }
})
</script>

<style scoped>
.day-view {
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

.day-container {
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

.day-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, rgba(255, 107, 107, 0.1) 0%, transparent 100%);
  pointer-events: none;
}

.day-title {
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

.day-content {
  font-size: 18px;
  line-height: 1.8;
  letter-spacing: 1px;
  text-align: justify;
  margin-bottom: 25px;
  padding: 0 10px;
}

.day-actions {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.action-button {
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

.action-button:hover {
  background-color: #ff8c8c;
  transform: translateY(-3px);
  box-shadow: 0 6px 10px rgba(0, 0, 0, 0.4);
}

.action-button:active {
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}
</style>
