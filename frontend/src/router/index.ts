
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/LoginView.vue'),
    },
    {
      path: '/',
      component: () => import('@/layouts/MainLayout.vue'),
      // 配置子路由
      children: [
        {
          path: '', // 默认访问 / 时显示任务列表
          name: 'TaskList',
          component: () => import('@/views/TaskView.vue'),
        },
        {
          path: 'profile',
          name: 'Profile',
          // 指向真实的个人中心页面
          component: () => import('@/views/ProfileView.vue'), 
        }
      ]
    },
  ],
})

router.beforeEach((to) => {
  const token = localStorage.getItem('token')
  // 如果目标页面不是 /login，且没有 token，强制跳转到 /login
  if (to.path !== '/login' && !token) {
    return '/login'
  }
})

export default router