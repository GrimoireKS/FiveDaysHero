# 前端时间推演数据使用指南

## 概述

游戏行动处理API返回的时间推演数据专门为前端背景切换和视觉效果设计，提供了丰富的环境信息来支持动态背景展示。

## 数据结构

### API响应格式

```json
{
  "status": "success",
  "result": {
    "time_progression": {
      "morning": {
        "narrative": "上午时段的详细叙述",
        "location": "村庄",
        "weather": "晴天",
        "atmosphere": "宁静",
        "events": [
          {
            "type": "dialogue",
            "description": "与村长交谈",
            "location": "村长家"
          }
        ],
        "state_changes": { ... }
      },
      "afternoon": { ... },
      "evening": { ... }
    }
  }
}
```

### 关键字段说明

#### 时段级别信息

- **location**: 主要地点
  - 用途：选择主背景图片
  - 可能值：村庄、森林、洞穴、遗迹、山脉等

- **weather**: 天气状况
  - 用途：添加天气效果
  - 可能值：晴天、雨天、阴天、雪天

- **atmosphere**: 氛围描述
  - 用途：应用滤镜或特效
  - 可能值：宁静、紧张、神秘、危险、温馨等

#### 事件级别信息

- **events[].type**: 事件类型
  - 用途：触发特殊背景或动画
  - 可能值：
    - `exploration`: 探索类事件
    - `combat`: 战斗类事件
    - `dialogue`: 对话交流类事件
    - `fixed_event`: 固定事件
    - `discovery`: 发现类事件
    - `rest`: 休息恢复类事件
    - `trade`: 交易类事件

- **events[].location**: 具体地点
  - 用途：精确背景选择
  - 示例：村长家、铁匠铺、森林深处、古老遗迹等

## 前端实现建议

### 1. 背景图片管理

```javascript
// 背景图片映射
const backgroundImages = {
  // 主要地点
  '村庄': {
    default: '/images/backgrounds/village_default.jpg',
    morning: '/images/backgrounds/village_morning.jpg',
    afternoon: '/images/backgrounds/village_afternoon.jpg',
    evening: '/images/backgrounds/village_evening.jpg'
  },
  '森林': {
    default: '/images/backgrounds/forest_default.jpg',
    morning: '/images/backgrounds/forest_morning.jpg',
    afternoon: '/images/backgrounds/forest_afternoon.jpg',
    evening: '/images/backgrounds/forest_evening.jpg'
  },
  // 具体地点
  '村长家': '/images/backgrounds/chief_house.jpg',
  '铁匠铺': '/images/backgrounds/blacksmith.jpg',
  '森林深处': '/images/backgrounds/deep_forest.jpg'
};

// 选择背景图片
function selectBackground(location, period, events) {
  // 优先使用具体地点
  for (const event of events) {
    if (event.location && backgroundImages[event.location]) {
      return backgroundImages[event.location];
    }
  }
  
  // 使用主要地点 + 时段
  const locationBg = backgroundImages[location];
  if (locationBg && locationBg[period]) {
    return locationBg[period];
  }
  
  // 回退到默认背景
  return locationBg?.default || '/images/backgrounds/default.jpg';
}
```

### 2. 天气效果

```javascript
// 天气效果映射
const weatherEffects = {
  '晴天': {
    filter: 'brightness(1.1) contrast(1.05)',
    particles: null
  },
  '雨天': {
    filter: 'brightness(0.8) contrast(0.9)',
    particles: 'rain'
  },
  '阴天': {
    filter: 'brightness(0.9) contrast(0.95) saturate(0.8)',
    particles: null
  },
  '雪天': {
    filter: 'brightness(1.2) contrast(1.1) hue-rotate(10deg)',
    particles: 'snow'
  }
};

// 应用天气效果
function applyWeatherEffect(weather) {
  const effect = weatherEffects[weather];
  if (effect) {
    // 应用滤镜
    document.querySelector('.game-background').style.filter = effect.filter;
    
    // 添加粒子效果
    if (effect.particles) {
      showParticleEffect(effect.particles);
    }
  }
}
```

### 3. 氛围效果

```javascript
// 氛围效果映射
const atmosphereEffects = {
  '宁静': {
    overlay: 'rgba(255, 255, 255, 0.1)',
    animation: 'gentle-fade'
  },
  '紧张': {
    overlay: 'rgba(255, 0, 0, 0.1)',
    animation: 'pulse'
  },
  '神秘': {
    overlay: 'rgba(128, 0, 128, 0.15)',
    animation: 'mysterious-glow'
  },
  '危险': {
    overlay: 'rgba(255, 0, 0, 0.2)',
    animation: 'danger-flash'
  },
  '温馨': {
    overlay: 'rgba(255, 200, 100, 0.1)',
    animation: 'warm-glow'
  }
};

// 应用氛围效果
function applyAtmosphereEffect(atmosphere) {
  const effect = atmosphereEffects[atmosphere];
  if (effect) {
    const overlay = document.querySelector('.atmosphere-overlay');
    overlay.style.backgroundColor = effect.overlay;
    overlay.className = `atmosphere-overlay ${effect.animation}`;
  }
}
```

### 4. 事件特效

```javascript
// 事件特效映射
const eventEffects = {
  'combat': {
    screenShake: true,
    flashColor: 'red',
    sound: 'battle'
  },
  'discovery': {
    sparkles: true,
    flashColor: 'gold',
    sound: 'discovery'
  },
  'dialogue': {
    focusEffect: true,
    sound: 'dialogue'
  },
  'fixed_event': {
    specialTransition: true,
    sound: 'event'
  }
};

// 触发事件特效
function triggerEventEffects(events) {
  events.forEach(event => {
    const effect = eventEffects[event.type];
    if (effect) {
      if (effect.screenShake) {
        triggerScreenShake();
      }
      if (effect.sparkles) {
        showSparkleEffect();
      }
      if (effect.flashColor) {
        flashScreen(effect.flashColor);
      }
      if (effect.sound) {
        playSound(effect.sound);
      }
    }
  });
}
```

### 5. 完整的时段切换实现

```javascript
// 处理时段切换
function processTimePeriod(periodData, period) {
  const { location, weather, atmosphere, events, narrative } = periodData;
  
  // 1. 切换背景
  const backgroundUrl = selectBackground(location, period, events);
  changeBackground(backgroundUrl);
  
  // 2. 应用天气效果
  applyWeatherEffect(weather);
  
  // 3. 应用氛围效果
  applyAtmosphereEffect(atmosphere);
  
  // 4. 触发事件特效
  triggerEventEffects(events);
  
  // 5. 显示叙述文本
  displayNarrative(narrative);
  
  // 6. 更新UI指示器
  updateTimeIndicator(period);
  updateLocationIndicator(location);
  updateWeatherIndicator(weather);
}

// 处理完整的游戏行动结果
function processGameActionResult(result) {
  const timePeriods = ['morning', 'afternoon', 'evening'];
  
  timePeriods.forEach((period, index) => {
    if (result.time_progression[period]) {
      setTimeout(() => {
        processTimePeriod(result.time_progression[period], period);
      }, index * 2000); // 每个时段间隔2秒
    }
  });
}
```

## CSS动画示例

```css
/* 氛围动画 */
.gentle-fade {
  animation: gentleFade 3s ease-in-out infinite alternate;
}

@keyframes gentleFade {
  0% { opacity: 0.8; }
  100% { opacity: 1; }
}

.pulse {
  animation: pulse 1s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 0.8; }
  50% { opacity: 1; }
}

.mysterious-glow {
  animation: mysteriousGlow 4s ease-in-out infinite;
}

@keyframes mysteriousGlow {
  0%, 100% { 
    opacity: 0.6;
    filter: blur(1px);
  }
  50% { 
    opacity: 0.9;
    filter: blur(0px);
  }
}

/* 背景切换动画 */
.background-transition {
  transition: all 1s ease-in-out;
}

/* 粒子效果容器 */
.particles-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 10;
}
```

## 最佳实践

1. **预加载资源**: 提前加载可能用到的背景图片和音效
2. **平滑过渡**: 使用CSS过渡动画确保背景切换流畅
3. **性能优化**: 合理使用图片压缩和懒加载
4. **响应式设计**: 确保不同屏幕尺寸下的效果一致
5. **用户设置**: 提供选项让用户控制特效强度

## 调试工具

```javascript
// 调试时段数据
function debugTimePeriod(periodData) {
  console.log('时段数据:', {
    location: periodData.location,
    weather: periodData.weather,
    atmosphere: periodData.atmosphere,
    eventTypes: periodData.events.map(e => e.type),
    eventLocations: periodData.events.map(e => e.location)
  });
}
```

通过这套完整的数据结构和实现方案，前端可以实现丰富的动态背景切换效果，为玩家提供沉浸式的游戏体验。
