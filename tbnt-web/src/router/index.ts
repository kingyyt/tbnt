import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Layout from '@/layout/index.vue'
import HomeView from '@/views/dashboard/index.vue'
import LoginView from '@/views/auth/index.vue'
import WorkSettingsView from '@/views/work/SettingsView.vue'
import WorkHistoryView from '@/views/work/HistoryView.vue'
import ProfileView from '@/views/profile/index.vue'
import LobbyView from '@/views/lobby/index.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      component: Layout,
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          name: 'home',
          component: HomeView
        },
        {
          path: 'history',
          name: 'history',
          component: WorkHistoryView
        },
        {
          path: 'settings',
          name: 'settings',
          component: WorkSettingsView
        },
        {
          path: 'profile',
          name: 'profile',
          component: ProfileView
        },
        {
          path: 'lobby',
          name: 'lobby',
          component: LobbyView
        }
      ]
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: { requiresAuth: false }
    }
  ],
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.token) {
    next('/login')
  } else if (to.path === '/login' && authStore.token) {
    next('/')
  } else {
    next()
  }
})

export default router
