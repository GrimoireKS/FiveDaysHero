import { defineStore } from 'pinia'

// 定义勇者状态的 store
export const useHeroStore = defineStore('hero', {
  // 状态
  state: () => ({
    // 基本信息
    name: '', // 勇者姓名
    gender: '', // 勇者性别
    profession: '', // 勇者职业
    age: '', // 勇者年龄
    
    // 属性值
    hp: 100, // 生命值，初始值100
    mp: 100, // 魔法值，初始值100
    strength: null, // 力量，0-100
    intelligence: null, // 智力，0-100
    agility: null, // 敏捷，0-100
    luck: null, // 幸运，0-100
    
    // 装备
    equipment: {
      head: null, // 头部装备，最多1件
      chest: null, // 胸部装备，最多1件
      legs: null, // 腿部装备，最多1件
      hands: [], // 手部装备，最多2件
      feet: null, // 脚部装备，最多1件
      neck: null, // 脖子装备，最多1件
      wrists: [], // 手腕装备，最多2件
    },
    
    // 游戏进度
    day: 0, // 当前天数
    choices: [], // 每天的选择记录
  }),
  
  // 计算属性
  getters: {
    // 获取勇者全名
    fullName: (state) => {
      return state.name || '无名勇者'
    },
    
    // 检查基本属性是否已设置
    isBasicInfoSet: (state) => {
      return !!state.name || !!state.gender || !!state.profession || !!state.age
    },
    
    // 检查能力值是否已设置
    isStatsSet: (state) => {
      return state.strength !== null && 
             state.intelligence !== null && 
             state.agility !== null && 
             state.luck !== null
    },
    
    // 获取装备列表
    equipmentList: (state) => {
      const list = []
      
      if (state.equipment.head) list.push({ type: 'head', item: state.equipment.head })
      if (state.equipment.chest) list.push({ type: 'chest', item: state.equipment.chest })
      if (state.equipment.legs) list.push({ type: 'legs', item: state.equipment.legs })
      state.equipment.hands.forEach(item => list.push({ type: 'hands', item }))
      if (state.equipment.feet) list.push({ type: 'feet', item: state.equipment.feet })
      if (state.equipment.neck) list.push({ type: 'neck', item: state.equipment.neck })
      state.equipment.wrists.forEach(item => list.push({ type: 'wrists', item }))
      
      return list
    }
  },
  
  // 方法
  actions: {
    // 设置勇者基本信息
    setBasicInfo({ name, gender, profession, age }) {
      if (name && !this.name) this.name = name
      if (gender && !this.gender) this.gender = gender
      if (profession && !this.profession) this.profession = profession
      if (age && !this.age) this.age = age
    },
    
    // 设置勇者能力值
    setStats({ strength, intelligence, agility, luck }) {
      if (strength !== undefined && this.strength === null) this.strength = strength
      if (intelligence !== undefined && this.intelligence === null) this.intelligence = intelligence
      if (agility !== undefined && this.agility === null) this.agility = agility
      if (luck !== undefined && this.luck === null) this.luck = luck
    },
    
    // 更新生命值和魔法值
    updateStatus({ hp, mp }) {
      if (hp !== undefined) this.hp = hp
      if (mp !== undefined) this.mp = mp
    },
    
    // 添加装备
    addEquipment(type, item) {
      if (!item) return false
      
      switch (type) {
        case 'head':
        case 'chest':
        case 'legs':
        case 'feet':
        case 'neck':
          this.equipment[type] = item
          return true
        case 'hands':
          if (this.equipment.hands.length < 2) {
            this.equipment.hands.push(item)
            return true
          }
          return false
        case 'wrists':
          if (this.equipment.wrists.length < 2) {
            this.equipment.wrists.push(item)
            return true
          }
          return false
        default:
          return false
      }
    },
    
    // 移除装备
    removeEquipment(type, index = 0) {
      switch (type) {
        case 'head':
        case 'chest':
        case 'legs':
        case 'feet':
        case 'neck':
          this.equipment[type] = null
          return true
        case 'hands':
        case 'wrists':
          if (index >= 0 && index < this.equipment[type].length) {
            this.equipment[type].splice(index, 1)
            return true
          }
          return false
        default:
          return false
      }
    },
    
    // 记录每天的选择
    recordChoice(day, choice) {
      this.choices.push({ day, choice })
      this.day = day
    },
    
    // 从玩家输入中提取勇者信息
    extractHeroInfo(playerInput) {
      // 这里可以添加更复杂的逻辑来从玩家输入中提取信息
      // 简单示例：
      const nameMatch = playerInput.match(/我叫([\u4e00-\u9fa5a-zA-Z]+)/);
      const genderMatch = playerInput.match(/(男|女)勇者/);
      const professionMatch = playerInput.match(/我是([\u4e00-\u9fa5a-zA-Z]+)(勇者|战士|法师|盗贼|弓箭手|骑士)/);
      const ageMatch = playerInput.match(/(\d+)岁/);
      
      const info = {}
      if (nameMatch) info.name = nameMatch[1]
      if (genderMatch) info.gender = genderMatch[1]
      if (professionMatch) info.profession = professionMatch[1]
      if (ageMatch) info.age = parseInt(ageMatch[1])
      
      if (Object.keys(info).length > 0) {
        this.setBasicInfo(info)
      }
      
      return info
    },
    
    // 重置状态
    reset() {
      this.$reset()
    }
  },
  
  // 持久化
  persist: true
})
