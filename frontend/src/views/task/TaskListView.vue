<template>
  <div class="page">
    <PageHeader title="养护任务登记" description="按绿地登记养护作业计划，任务状态随养护记录自动流转">
      <template #actions>
        <el-button type="primary" :icon="'Plus'" @click="formDialog.open()">登记养护任务</el-button>
      </template>
    </PageHeader>

    <div class="panel">
      <div class="filter-bar">
        <el-input v-model="filters.keyword" placeholder="任务编号 / 名称 / 执行班组" clearable
                  :prefix-icon="'Search'" @keyup.enter="search" @clear="search" />
        <div style="width: 220px">
          <GreenSpaceSelect v-model="filters.green_space_id" placeholder="按绿地筛选" @update:model-value="search" />
        </div>
        <el-select v-model="filters.status" placeholder="任务状态" clearable @change="search">
          <el-option v-for="item in statusOptions" :key="item.value" :label="item.label" :value="item.value" />
        </el-select>
        <el-select v-model="filters.task_type" placeholder="养护类型" clearable @change="search">
          <el-option v-for="item in typeOptions" :key="item.value" :label="item.label" :value="item.value" />
        </el-select>
        <el-select v-model="filters.priority" placeholder="优先级" clearable @change="search">
          <el-option v-for="item in priorityOptions" :key="item.value" :label="item.label" :value="item.value" />
        </el-select>
        <el-date-picker v-model="dateRange" type="daterange" unlink-panels value-format="YYYY-MM-DD"
                        start-placeholder="计划开始" end-placeholder="计划结束" @change="onDateChange" />
        <el-checkbox v-model="filters.overdue" label="仅看逾期" border @change="search" />
        <el-button type="primary" :icon="'Search'" @click="search">查询</el-button>
        <el-button :icon="'RefreshLeft'" @click="resetFilters">重置</el-button>
      </div>
    </div>

    <div class="panel">
      <div class="table-toolbar">
        <span class="summary-text">
          共 <strong>{{ meta.total }}</strong> 项任务，
          待执行 <strong>{{ summary?.pending ?? 0 }}</strong>、
          进行中 <strong>{{ summary?.in_progress ?? 0 }}</strong>、
          已完成 <strong>{{ summary?.completed ?? 0 }}</strong>、
          已取消 <strong>{{ summary?.cancelled ?? 0 }}</strong>
        </span>
        <el-button :icon="'Refresh'" text @click="load">刷新</el-button>
      </div>

      <el-table :data="items" v-loading="loading" border stripe>
        <el-table-column label="任务编号 / 名称" min-width="240" show-overflow-tooltip>
          <template #default="{ row }">
            <div class="cell-main">{{ row.title }}</div>
            <div class="cell-sub">{{ row.task_no }}</div>
          </template>
        </el-table-column>
        <el-table-column label="所属绿地" min-width="160" show-overflow-tooltip>
          <template #default="{ row }">{{ row.green_space?.name || '-' }}</template>
        </el-table-column>
        <el-table-column label="养护类型" width="110">
          <template #default="{ row }">
            <EnumTag group="task_type" :value="row.task_type" :label="row.task_type_label" />
          </template>
        </el-table-column>
        <el-table-column label="计划日期" width="130">
          <template #default="{ row }">
            {{ row.plan_date }}
            <el-tag v-if="row.is_overdue" type="danger" size="small" effect="plain">逾期</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="优先级" width="84">
          <template #default="{ row }">
            <EnumTag group="task_priority" :value="row.priority" :label="row.priority_label" />
          </template>
        </el-table-column>
        <el-table-column prop="executor" label="执行班组" width="100">
          <template #default="{ row }">{{ row.executor || '-' }}</template>
        </el-table-column>
        <el-table-column label="执行进度" width="112">
          <template #default="{ row }">
            <div>{{ row.progress.record_count }} 条记录</div>
            <div class="cell-sub">合格 {{ row.progress.qualified_count }} 条</div>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="92">
          <template #default="{ row }">
            <EnumTag group="task_status" :value="row.status" :label="row.status_label" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="drawer.open(row.id)">详情</el-button>
            <el-button link type="primary" @click="formDialog.open(row)">编辑</el-button>
            <el-dropdown trigger="click" @command="(status) => changeStatus(row, status)">
              <el-button link type="primary">状态<el-icon><ArrowDown /></el-icon></el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item v-for="item in statusOptions" :key="item.value" :command="item.value"
                                    :disabled="item.value === row.status">
                    {{ item.label }}
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
            <el-button link type="danger" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        class="pager"
        background
        layout="total, sizes, prev, pager, next, jumper"
        :total="meta.total"
        :current-page="meta.page"
        :page-size="meta.page_size"
        :page-sizes="[10, 20, 50]"
        @current-change="handlePageChange"
        @size-change="handleSizeChange"
      />
    </div>

    <TaskFormDialog ref="formDialog" @saved="load" />
    <TaskDetailDrawer ref="drawer" @updated="load" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'

import { maintenanceTaskApi } from '@/api'
import EnumTag from '@/components/common/EnumTag.vue'
import GreenSpaceSelect from '@/components/common/GreenSpaceSelect.vue'
import PageHeader from '@/components/common/PageHeader.vue'
import { useEnumOptions } from '@/composables/useEnumOptions'
import { useListQuery } from '@/composables/useListQuery'

import TaskDetailDrawer from './TaskDetailDrawer.vue'
import TaskFormDialog from './TaskFormDialog.vue'

const route = useRoute()
const formDialog = ref(null)
const drawer = ref(null)
const dateRange = ref([])

const { options: statusOptions } = useEnumOptions('task_status')
const { options: typeOptions } = useEnumOptions('task_type')
const { options: priorityOptions } = useEnumOptions('task_priority')

const { filters, meta, items, summary, loading, load, search, resetFilters, handlePageChange, handleSizeChange } =
  useListQuery(maintenanceTaskApi.list, {
    initialFilters: {
      keyword: '',
      green_space_id: route.query.green_space_id ? Number(route.query.green_space_id) : null,
      status: '',
      task_type: '',
      priority: '',
      date_from: '',
      date_to: '',
      overdue: false,
    },
  })

function onDateChange(value) {
  filters.date_from = value?.[0] || ''
  filters.date_to = value?.[1] || ''
  search()
}

async function changeStatus(row, status) {
  try {
    await maintenanceTaskApi.changeStatus(row.id, { status })
    ElMessage.success('任务状态已更新')
    await load()
  } catch {
    // 冲突提示已由请求层处理（如存在不合格记录）
  }
}

async function remove(row) {
  try {
    const hasRecords = row.progress.record_count > 0
    await ElMessageBox.confirm(
      hasRecords
        ? `该任务已登记 ${row.progress.record_count} 条养护记录，删除任务后养护记录会保留但不再关联任务，是否继续？`
        : `确认删除任务「${row.title}」吗？`,
      '删除确认',
      { type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消' },
    )
    await maintenanceTaskApi.remove(row.id, hasRecords ? { force: true } : undefined)
    ElMessage.success('养护任务已删除')
    await load()
  } catch (error) {
    if (error === 'cancel' || error === 'close') return
  }
}
</script>

<style scoped>
.pager {
  margin-top: 16px;
  justify-content: flex-end;
}

.cell-main {
  font-weight: 500;
}

.cell-sub {
  color: #909399;
  font-size: 12px;
}
</style>
