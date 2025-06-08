<template>
  <div class="hero-status">
    <h2 class="status-title">勇者状态</h2>

    <div class="status-section">
      <h3>基本信息</h3>
      <div class="status-grid">
        <div class="status-item">
          <span class="label">姓名:</span>
          <span class="value">{{ getBasicInfo('name') || '未知' }}</span>
        </div>
        <div class="status-item">
          <span class="label">性别:</span>
          <span class="value">{{ getBasicInfo('gender') || '未知' }}</span>
        </div>
        <div class="status-item">
          <span class="label">职业:</span>
          <span class="value">{{ getBasicInfo('profession') || '未知' }}</span>
        </div>
        <div class="status-item">
          <span class="label">年龄:</span>
          <span class="value">{{ getBasicInfo('age') || '未知' }}</span>
        </div>
      </div>
    </div>

    <div class="status-section">
      <h3>状态</h3>
      <div class="status-bars">
        <div class="status-bar">
          <span class="label">生命值:</span>
          <div class="bar-container">
            <div class="bar hp" :style="{ width: `${getStat('hp')}%` }"></div>
            <span class="bar-text">{{ getStat('hp') }}/100</span>
          </div>
        </div>
        <div class="status-bar">
          <span class="label">魔法值:</span>
          <div class="bar-container">
            <div class="bar mp" :style="{ width: `${getStat('mp')}%` }"></div>
            <span class="bar-text">{{ getStat('mp') }}/100</span>
          </div>
        </div>
      </div>
    </div>

    <div class="status-section" v-if="isStatsSet">
      <h3>能力值</h3>
      <div class="status-grid">
        <div class="status-item">
          <span class="label">力量:</span>
          <span class="value">{{ getStat('strength') }}</span>
          <div class="stat-bar">
            <div class="stat-fill" :style="{ width: `${getStat('strength')}%` }"></div>
          </div>
        </div>
        <div class="status-item">
          <span class="label">智力:</span>
          <span class="value">{{ getStat('intelligence') }}</span>
          <div class="stat-bar">
            <div class="stat-fill" :style="{ width: `${getStat('intelligence')}%` }"></div>
          </div>
        </div>
        <div class="status-item">
          <span class="label">敏捷:</span>
          <span class="value">{{ getStat('agility') }}</span>
          <div class="stat-bar">
            <div class="stat-fill" :style="{ width: `${getStat('agility')}%` }"></div>
          </div>
        </div>
        <div class="status-item">
          <span class="label">幸运:</span>
          <span class="value">{{ getStat('luck') }}</span>
          <div class="stat-bar">
            <div class="stat-fill" :style="{ width: `${getStat('luck')}%` }"></div>
          </div>
        </div>
      </div>
    </div>

    <div class="status-section" v-if="equipmentList.length > 0">
      <h3>装备</h3>
      <ul class="equipment-list">
        <li v-for="(equip, index) in equipmentList" :key="index" class="equipment-item">
          <span class="equipment-type">{{ getEquipmentTypeName(equip.type) }}:</span>
          <span class="equipment-name">{{ equip.item }}</span>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'
import { useHeroStore } from '@/store/heroStore'

export default {
  name: 'HeroStatus',
  props: {
    // 接受从父组件传递的玩家数据
    playerData: {
      type: Object,
      default: () => ({})
    }
  },
  setup(props) {
    const heroStore = useHeroStore()

    // 获取基本信息的方法，支持后端嵌套结构和前端扁平结构
    const getBasicInfo = (field) => {
      // 优先使用props传递的数据
      if (props.playerData && Object.keys(props.playerData).length > 0) {
        // 尝试从basic_info获取
        if (props.playerData.basic_info && props.playerData.basic_info[field] !== undefined) {
          return props.playerData.basic_info[field]
        }
        // 尝试直接获取
        if (props.playerData[field] !== undefined) {
          return props.playerData[field]
        }
      }

      // 回退到heroStore
      return heroStore[field]
    }

    // 获取属性值的方法，支持后端嵌套结构和前端扁平结构
    const getStat = (statName) => {
      // 优先使用props传递的数据
      if (props.playerData && Object.keys(props.playerData).length > 0) {
        // 尝试从stats获取
        if (props.playerData.stats && props.playerData.stats[statName] !== undefined) {
          return props.playerData.stats[statName]
        }
        // 尝试直接获取
        if (props.playerData[statName] !== undefined) {
          return props.playerData[statName]
        }
      }

      // 回退到heroStore
      if (heroStore[statName] !== undefined && heroStore[statName] !== null) {
        return heroStore[statName]
      }

      // 返回默认值
      return getDefaultStatValue(statName)
    }

    // 获取默认属性值
    const getDefaultStatValue = (statName) => {
      switch(statName) {
        case 'hp':
        case 'mp':
          return 100
        case 'strength':
        case 'intelligence':
        case 'agility':
        case 'luck':
          return 50
        default:
          return 0
      }
    }

    // 检查能力值是否已设置
    const isStatsSet = computed(() => {
      const strength = getStat('strength')
      const intelligence = getStat('intelligence')
      const agility = getStat('agility')
      const luck = getStat('luck')

      return strength !== null && intelligence !== null &&
             agility !== null && luck !== null &&
             strength > 0 && intelligence > 0 &&
             agility > 0 && luck > 0
    })

    // 获取装备列表
    const equipmentList = computed(() => {
      // 优先使用props传递的数据
      if (props.playerData && props.playerData.equipment) {
        const equipment = props.playerData.equipment
        const list = []

        for (const [type, item] of Object.entries(equipment)) {
          if (item) {
            if (Array.isArray(item)) {
              item.forEach(i => {
                if (i) list.push({ type, item: i })
              })
            } else {
              list.push({ type, item })
            }
          }
        }

        return list
      }

      // 回退到heroStore
      return heroStore.equipmentList || []
    })

    // 获取装备类型的中文名称
    const getEquipmentTypeName = (type) => {
      const typeMap = {
        head: '头部',
        chest: '胸部',
        legs: '腿部',
        hands: '手部',
        feet: '脚部',
        neck: '脖子',
        wrists: '手腕'
      }
      return typeMap[type] || type
    }

    return {
      getBasicInfo,
      getStat,
      isStatsSet,
      equipmentList,
      getEquipmentTypeName
    }
  }
}
</script>

<style scoped>
.hero-status {
  background-color: rgba(0, 0, 0, 0.8);
  border: 2px solid #ff6b6b;
  border-radius: 8px;
  padding: 20px;
  color: #fff;
  font-family: 'Microsoft YaHei', sans-serif;
  max-width: 400px;
  box-shadow: 0 0 15px rgba(255, 107, 107, 0.4);
}

.status-title {
  text-align: center;
  color: #ff6b6b;
  margin-top: 0;
  margin-bottom: 20px;
  font-size: 24px;
  border-bottom: 1px solid #ff6b6b;
  padding-bottom: 10px;
}

.status-section {
  margin-bottom: 20px;
}

.status-section h3 {
  color: #ff6b6b;
  margin-bottom: 10px;
  font-size: 18px;
}

.status-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.status-item {
  display: flex;
  flex-direction: column;
}

.label {
  color: #aaa;
  font-size: 14px;
  margin-bottom: 5px;
}

.value {
  font-size: 16px;
  font-weight: bold;
}

.status-bars {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.status-bar {
  display: flex;
  align-items: center;
  gap: 10px;
}

.status-bar .label {
  width: 60px;
  margin-bottom: 0;
}

.bar-container {
  flex: 1;
  height: 20px;
  background-color: rgba(0, 0, 0, 0.3);
  border-radius: 10px;
  overflow: hidden;
  position: relative;
}

.bar {
  height: 100%;
  transition: width 0.3s ease;
}

.hp {
  background: linear-gradient(to right, #ff6b6b, #ff8e8e);
}

.mp {
  background: linear-gradient(to right, #4a90e2, #6ab0ff);
}

.bar-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 12px;
  font-weight: bold;
  text-shadow: 1px 1px 1px rgba(0, 0, 0, 0.7);
}

.stat-bar {
  height: 6px;
  background-color: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
  overflow: hidden;
  margin-top: 5px;
}

.stat-fill {
  height: 100%;
  background-color: #ff6b6b;
}

.equipment-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.equipment-item {
  padding: 8px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
}

.equipment-item:last-child {
  border-bottom: none;
}

.equipment-type {
  color: #aaa;
  margin-right: 10px;
  width: 50px;
}

.equipment-name {
  font-weight: bold;
}
</style>
