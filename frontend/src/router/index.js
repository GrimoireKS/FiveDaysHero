import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import GameMainView from '../views/GameMainView.vue'
import PrologueView from '../views/prologue/PrologueView.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView
  },
  {
    path: '/prologue',
    name: 'prologue',
    component: PrologueView
  },
  {
    path: '/game/:gameId',
    name: 'game-main',
    component: GameMainView,
    props: true
  },
  {
    path: '/game/:gameId/end',
    name: 'game-end',
    component: () => import('../views/GameEndView.vue'),
    props: true
  },
  // 重定向旧的游戏路由
  {
    path: '/game',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router
