<template>
  <div class="action-input-panel">
    <div class="panel-header">
      <h2>制定您的行动计划</h2>
      <p class="instruction">请描述您今天想要做什么（限制100字以内）</p>
    </div>
    
    <div class="input-section">
      <div class="input-container">
        <textarea
          v-model="actionText"
          ref="textareaRef"
          placeholder="例如：我想在村庄里四处走走，了解一下这个地方的情况，和村民们聊聊天，看看有什么任务可以做..."
          maxlength="100"
          @input="handleInput"
          @keydown="handleKeydown"
          :disabled="disabled"
          class="action-textarea"
        ></textarea>
        
        <div class="input-footer">
          <div class="char-counter" :class="{ 'warning': isNearLimit, 'danger': isAtLimit }">
            {{ actionText.length }}/100
          </div>
          
          <div class="input-actions">
            <button 
              @click="clearInput" 
              class="clear-btn"
              :disabled="disabled || !actionText.trim()"
            >
              清空
            </button>
            
            <button 
              @click="submitAction" 
              class="submit-btn"
              :disabled="disabled || !canSubmit"
            >
              <span v-if="!disabled">确认行动</span>
              <span v-else>处理中...</span>
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <div class="tips-section">
      <h3>💡 行动建议</h3>
      <div class="tips-grid">
        <div class="tip-item" @click="fillSuggestion('探索村庄，与村民交流，了解当地情况和可能的任务。')">
          🏘️ 探索村庄
        </div>
        <div class="tip-item" @click="fillSuggestion('前往森林寻找有用的材料和宝物，提升自己的实力。')">
          🌲 森林探险
        </div>
        <div class="tip-item" @click="fillSuggestion('在村庄里寻找训练的机会，提升战斗技能和属性。')">
          ⚔️ 技能训练
        </div>
        <div class="tip-item" @click="fillSuggestion('寻找商人购买装备和道具，为即将到来的挑战做准备。')">
          🛒 购买装备
        </div>
        <div class="tip-item" @click="fillSuggestion('寻找其他冒险者组队，或者帮助村民解决问题。')">
          🤝 社交互动
        </div>
        <div class="tip-item" @click="fillSuggestion('收集信息，了解魔王的弱点和击败它的方法。')">
          📚 收集情报
        </div>
      </div>
    </div>
    
    <div class="warning-section" v-if="showWarnings">
      <div class="warning-item">
        ⚠️ 请注意：您的行动将影响整个游戏世界的发展
      </div>
      <div class="warning-item">
        ⏰ 每个行动将消耗一整天的时间（上午、下午、晚上）
      </div>
      <div class="warning-item">
        🎯 明确具体的行动比模糊的计划更容易获得好结果
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, nextTick } from 'vue'

export default {
  name: 'ActionInputPanel',
  props: {
    disabled: {
      type: Boolean,
      default: false
    }
  },
  emits: ['submit-action'],
  setup(props, { emit }) {
    const actionText = ref('')
    const textareaRef = ref(null)
    const showWarnings = ref(true)
    
    // 计算属性
    const isNearLimit = computed(() => actionText.value.length >= 80)
    const isAtLimit = computed(() => actionText.value.length >= 100)
    const canSubmit = computed(() => {
      const trimmed = actionText.value.trim()
      return trimmed.length > 0 && trimmed.length <= 100 && !props.disabled
    })
    
    // 方法
    const handleInput = () => {
      // 确保不超过100字符
      if (actionText.value.length > 100) {
        actionText.value = actionText.value.substring(0, 100)
      }
    }
    
    const handleKeydown = (event) => {
      // Ctrl+Enter 或 Cmd+Enter 提交
      if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
        event.preventDefault()
        if (canSubmit.value) {
          submitAction()
        }
      }
    }
    
    const clearInput = () => {
      actionText.value = ''
      nextTick(() => {
        if (textareaRef.value) {
          textareaRef.value.focus()
        }
      })
    }
    
    const submitAction = () => {
      if (!canSubmit.value) return
      
      const trimmedAction = actionText.value.trim()
      if (trimmedAction) {
        emit('submit-action', trimmedAction)
        actionText.value = ''
      }
    }
    
    const fillSuggestion = (suggestion) => {
      if (props.disabled) return
      
      actionText.value = suggestion
      nextTick(() => {
        if (textareaRef.value) {
          textareaRef.value.focus()
          // 将光标移到末尾
          textareaRef.value.setSelectionRange(suggestion.length, suggestion.length)
        }
      })
    }
    
    return {
      actionText,
      textareaRef,
      showWarnings,
      isNearLimit,
      isAtLimit,
      canSubmit,
      handleInput,
      handleKeydown,
      clearInput,
      submitAction,
      fillSuggestion
    }
  }
}
</script>

<style scoped>
.action-input-panel {
  background: linear-gradient(135deg, #2c3e50, #34495e);
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 8px 25px rgba(0,0,0,0.3);
  color: #ecf0f1;
}

.panel-header {
  margin-bottom: 20px;
  text-align: center;
}

.panel-header h2 {
  margin: 0 0 8px 0;
  color: #3498db;
  font-size: 24px;
  font-weight: 600;
}

.instruction {
  margin: 0;
  color: #bdc3c7;
  font-size: 14px;
}

.input-section {
  margin-bottom: 25px;
}

.input-container {
  position: relative;
}

.action-textarea {
  width: 100%;
  min-height: 120px;
  padding: 15px;
  border: 2px solid #34495e;
  border-radius: 8px;
  background-color: #1a1a1a;
  color: #ecf0f1;
  font-size: 16px;
  font-family: inherit;
  line-height: 1.5;
  resize: vertical;
  transition: border-color 0.3s ease;
}

.action-textarea:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.action-textarea:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.action-textarea::placeholder {
  color: #7f8c8d;
  font-style: italic;
}

.input-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
}

.char-counter {
  font-size: 14px;
  color: #95a5a6;
  font-weight: 500;
}

.char-counter.warning {
  color: #f39c12;
}

.char-counter.danger {
  color: #e74c3c;
  font-weight: 600;
}

.input-actions {
  display: flex;
  gap: 10px;
}

.clear-btn,
.submit-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.clear-btn {
  background-color: #95a5a6;
  color: white;
}

.clear-btn:hover:not(:disabled) {
  background-color: #7f8c8d;
}

.submit-btn {
  background-color: #3498db;
  color: white;
  min-width: 100px;
}

.submit-btn:hover:not(:disabled) {
  background-color: #2980b9;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
}

.clear-btn:disabled,
.submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.tips-section {
  margin-bottom: 20px;
}

.tips-section h3 {
  margin: 0 0 15px 0;
  color: #f39c12;
  font-size: 16px;
  font-weight: 600;
}

.tips-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 10px;
}

.tip-item {
  padding: 12px 15px;
  background-color: rgba(52, 152, 219, 0.1);
  border: 1px solid rgba(52, 152, 219, 0.3);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
  text-align: center;
}

.tip-item:hover {
  background-color: rgba(52, 152, 219, 0.2);
  border-color: rgba(52, 152, 219, 0.5);
  transform: translateY(-2px);
}

.warning-section {
  background-color: rgba(241, 196, 15, 0.1);
  border: 1px solid rgba(241, 196, 15, 0.3);
  border-radius: 6px;
  padding: 15px;
}

.warning-item {
  color: #f1c40f;
  font-size: 13px;
  margin-bottom: 5px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.warning-item:last-child {
  margin-bottom: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .action-input-panel {
    padding: 20px;
  }
  
  .tips-grid {
    grid-template-columns: 1fr;
  }
  
  .input-footer {
    flex-direction: column;
    gap: 10px;
    align-items: stretch;
  }
  
  .input-actions {
    justify-content: center;
  }
}
</style>
