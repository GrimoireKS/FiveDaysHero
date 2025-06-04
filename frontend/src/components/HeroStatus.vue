<template>
  <div class="hero-status">
    <h2 class="status-title">勇者状态</h2>
    
    <div class="status-section">
      <h3>基本信息</h3>
      <div class="status-grid">
        <div class="status-item">
          <span class="label">姓名:</span>
          <span class="value">{{ hero.name || '未知' }}</span>
        </div>
        <div class="status-item">
          <span class="label">性别:</span>
          <span class="value">{{ hero.gender || '未知' }}</span>
        </div>
        <div class="status-item">
          <span class="label">职业:</span>
          <span class="value">{{ hero.profession || '未知' }}</span>
        </div>
        <div class="status-item">
          <span class="label">年龄:</span>
          <span class="value">{{ hero.age || '未知' }}</span>
        </div>
      </div>
    </div>
    
    <div class="status-section">
      <h3>状态</h3>
      <div class="status-bars">
        <div class="status-bar">
          <span class="label">生命值:</span>
          <div class="bar-container">
            <div class="bar hp" :style="{ width: `${hero.hp}%` }"></div>
            <span class="bar-text">{{ hero.hp }}/100</span>
          </div>
        </div>
        <div class="status-bar">
          <span class="label">魔法值:</span>
          <div class="bar-container">
            <div class="bar mp" :style="{ width: `${hero.mp}%` }"></div>
            <span class="bar-text">{{ hero.mp }}/100</span>
          </div>
        </div>
      </div>
    </div>
    
    <div class="status-section" v-if="hero.isStatsSet">
      <h3>能力值</h3>
      <div class="status-grid">
        <div class="status-item">
          <span class="label">力量:</span>
          <span class="value">{{ hero.strength }}</span>
          <div class="stat-bar">
            <div class="stat-fill" :style="{ width: `${hero.strength}%` }"></div>
          </div>
        </div>
        <div class="status-item">
          <span class="label">智力:</span>
          <span class="value">{{ hero.intelligence }}</span>
          <div class="stat-bar">
            <div class="stat-fill" :style="{ width: `${hero.intelligence}%` }"></div>
          </div>
        </div>
        <div class="status-item">
          <span class="label">敏捷:</span>
          <span class="value">{{ hero.agility }}</span>
          <div class="stat-bar">
            <div class="stat-fill" :style="{ width: `${hero.agility}%` }"></div>
          </div>
        </div>
        <div class="status-item">
          <span class="label">幸运:</span>
          <span class="value">{{ hero.luck }}</span>
          <div class="stat-bar">
            <div class="stat-fill" :style="{ width: `${hero.luck}%` }"></div>
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
  setup() {
    const heroStore = useHeroStore()
    
    // 获取装备列表
    const equipmentList = computed(() => heroStore.equipmentList)
    
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
      hero: heroStore,
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
