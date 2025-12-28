/**
 * Vue Router 配置
 * 定义应用的所有路由
 */
import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

// 路由配置
const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'CaseManagement',
    component: () => import('@/views/CaseManagement.vue'),
    meta: { title: '用例管理' }
  },
  {
    path: '/editor/:id?',
    name: 'ScriptEditor',
    component: () => import('@/views/ScriptEditor.vue'),
    meta: { title: '脚本编辑器' }
  },
  {
    path: '/execution',
    name: 'ExecutionConsole',
    component: () => import('@/views/ExecutionConsole.vue'),
    meta: { title: '执行控制台' }
  },
  {
    path: '/execution/:id',
    name: 'ExecutionDetail',
    component: () => import('@/views/ExecutionDetail.vue'),
    meta: { title: '执行详情' }
  },
  {
    path: '/reports',
    name: 'ReportCenter',
    component: () => import('@/views/ReportCenter.vue'),
    meta: { title: '报告中心' }
  },
  {
    path: '/reports/:id',
    name: 'ReportDetail',
    component: () => import('@/views/ReportDetail.vue'),
    meta: { title: '报告详情' }
  }
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫：设置页面标题
router.beforeEach((to, _from, next) => {
  const title = to.meta.title as string
  if (title) {
    document.title = `${title} - uiTool1.0`
  }
  next()
})

export default router
