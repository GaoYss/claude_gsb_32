import { createRouter, createWebHistory } from 'vue-router'

import DefaultLayout from '@/layouts/DefaultLayout.vue'

const routes = [
  {
    path: '/',
    component: DefaultLayout,
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'dashboard',
        component: () => import('@/views/dashboard/DashboardView.vue'),
        meta: { title: '养护总览', icon: 'DataLine' },
      },
      {
        path: 'green-spaces',
        name: 'green-space-list',
        component: () => import('@/views/green-space/GreenSpaceListView.vue'),
        meta: { title: '绿地台账', icon: 'MapLocation' },
      },
      {
        path: 'green-spaces/:id',
        name: 'green-space-detail',
        component: () => import('@/views/green-space/GreenSpaceDetailView.vue'),
        meta: { title: '绿地档案', activeMenu: '/green-spaces' },
      },
      {
        path: 'tasks',
        name: 'task-list',
        component: () => import('@/views/task/TaskListView.vue'),
        meta: { title: '养护任务', icon: 'Tickets' },
      },
      {
        path: 'records',
        name: 'record-list',
        component: () => import('@/views/record/RecordListView.vue'),
        meta: { title: '养护记录', icon: 'Notebook' },
      },
      {
        path: 'replacements',
        name: 'replacement-list',
        component: () => import('@/views/replacement/ReplacementListView.vue'),
        meta: { title: '绿植更换', icon: 'Cherry' },
      },
    ],
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('@/views/NotFoundView.vue'),
    meta: { title: '页面不存在' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 }),
})

router.afterEach((to) => {
  document.title = to.meta?.title ? `${to.meta.title} · 城市绿地养护记录系统` : '城市绿地养护记录系统'
})

export default router
