<template>
  <el-container class="layout">
    <el-aside :width="collapsed ? '64px' : '220px'" class="layout__aside">
      <div class="layout__brand">
        <el-icon :size="22" color="#48a17a"><Sunny /></el-icon>
        <span v-show="!collapsed" class="layout__brand-text">绿地养护记录</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        :collapse="collapsed"
        :collapse-transition="false"
        router
        class="layout__menu"
      >
        <el-menu-item v-for="item in menuItems" :key="item.path" :index="item.path">
          <el-icon><component :is="item.icon" /></el-icon>
          <template #title>{{ item.title }}</template>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="layout__header">
        <div class="layout__header-left">
          <el-button text :icon="collapsed ? 'Expand' : 'Fold'" @click="appStore.toggleSidebar()" />
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>城市绿地养护</el-breadcrumb-item>
            <el-breadcrumb-item>{{ currentTitle }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="layout__header-right">
          <el-tag :type="appStore.serviceOnline ? 'success' : 'danger'" effect="plain" size="small">
            {{ appStore.serviceOnline ? '服务正常' : '服务异常' }}
          </el-tag>
          <span class="layout__date">{{ today }}</span>
        </div>
      </el-header>

      <el-main class="layout__main">
        <router-view v-slot="{ Component }">
          <component :is="Component" />
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'

import { metaApi } from '@/api'
import { useAppStore } from '@/stores/app'
import { useMetaStore } from '@/stores/meta'
import { today as todayText } from '@/utils/format'

const route = useRoute()
const appStore = useAppStore()
const metaStore = useMetaStore()

const collapsed = computed(() => appStore.sidebarCollapsed)
const today = todayText()

const menuItems = [
  { path: '/dashboard', title: '养护总览', icon: 'DataLine' },
  { path: '/green-spaces', title: '绿地台账', icon: 'MapLocation' },
  { path: '/tasks', title: '养护任务', icon: 'Tickets' },
  { path: '/records', title: '养护记录', icon: 'Notebook' },
  { path: '/replacements', title: '绿植更换', icon: 'Cherry' },
]

const activeMenu = computed(() => route.meta?.activeMenu || route.path)
const currentTitle = computed(() => route.meta?.title || '养护总览')

onMounted(async () => {
  await metaStore.ensureLoaded().catch(() => {})
  try {
    const health = await metaApi.health()
    appStore.setServiceOnline(health?.status === 'ok')
  } catch {
    appStore.setServiceOnline(false)
  }
})
</script>

<style scoped>
.layout {
  height: 100%;
}

.layout__aside {
  background: #fff;
  border-right: 1px solid var(--gs-border);
  transition: width 0.2s ease;
}

.layout__brand {
  display: flex;
  align-items: center;
  gap: 8px;
  height: 60px;
  padding: 0 18px;
  border-bottom: 1px solid var(--gs-border);
  white-space: nowrap;
  overflow: hidden;
}

.layout__brand-text {
  font-size: 15px;
  font-weight: 600;
  color: var(--gs-primary);
}

.layout__menu {
  border-right: none;
}

.layout__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border-bottom: 1px solid var(--gs-border);
  height: 60px;
}

.layout__header-left,
.layout__header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.layout__date {
  color: #909399;
  font-size: 13px;
}

.layout__main {
  background: var(--gs-bg);
  padding: 16px;
}
</style>
