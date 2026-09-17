<template>
  <div class="page">
    <PageHeader title="养护记录录入" description="登记每次养护作业的作业内容、工时与质量评定，可关联养护任务">
      <template #actions>
        <el-button type="primary" :icon="'Plus'" @click="formDialog.open()">录入养护记录</el-button>
      </template>
    </PageHeader>

    <div class="panel">
      <div class="filter-bar">
        <el-input v-model="filters.keyword" placeholder="记录编号 / 作业内容 / 作业人员" clearable
                  :prefix-icon="'Search'" @keyup.enter="search" @clear="search" />
        <div style="width: 220px">
          <GreenSpaceSelect v-model="filters.green_space_id" placeholder="按绿地筛选" @update:model-value="onGreenSpaceChange" />
        </div>
        <el-select v-model="filters.quality_result" placeholder="质量评定" clearable @change="search">
          <el-option v-for="item in qualityOptions" :key="item.value" :label="item.label" :value="item.value" />
        </el-select>
        <el-select v-model="filters.weather" placeholder="天气" clearable @change="search">
          <el-option v-for="item in weatherOptions" :key="item.value" :label="item.label" :value="item.value" />
        </el-select>
        <el-date-picker v-model="dateRange" type="daterange" unlink-panels value-format="YYYY-MM-DD"
                        start-placeholder="养护日期起" end-placeholder="养护日期止" @change="onDateChange" />
        <el-checkbox v-model="filters.unlinked" label="仅看未关联任务" border @change="search" />
        <el-button type="primary" :icon="'Search'" @click="search">查询</el-button>
        <el-button :icon="'RefreshLeft'" @click="reset">重置</el-button>
      </div>
    </div>

    <div class="panel">
      <div class="table-toolbar">
        <span class="summary-text">
          共 <strong>{{ meta.total }}</strong> 条记录，累计工时
          <strong>{{ formatHours(summary?.total_work_hours) }}</strong>，
          合格 <strong>{{ summary?.quality_summary?.qualified ?? 0 }}</strong>、
          待复检 <strong>{{ summary?.quality_summary?.pending ?? 0 }}</strong>、
          不合格 <strong>{{ summary?.quality_summary?.unqualified ?? 0 }}</strong>
        </span>
        <el-button :icon="'Refresh'" text @click="load">刷新</el-button>
      </div>

      <el-table :data="items" v-loading="loading" border stripe>
        <el-table-column prop="record_no" label="记录编号" width="150" />
        <el-table-column label="所属绿地" min-width="150" show-overflow-tooltip>
          <template #default="{ row }">{{ row.green_space?.name || '-' }}</template>
        </el-table-column>
        <el-table-column label="关联任务" min-width="140" show-overflow-tooltip>
          <template #default="{ row }">
            <span v-if="row.task">{{ row.task.title }}</span>
            <el-tag v-else size="small" type="info" effect="plain">日常养护</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="养护日期" width="105">
          <template #default="{ row }">
            <div>{{ row.record_date }}</div>
            <div class="cell-sub">{{ row.weather_label || '-' }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="work_content" label="作业内容" min-width="190" show-overflow-tooltip />
        <el-table-column prop="worker" label="作业人员" width="90">
          <template #default="{ row }">{{ row.worker || '-' }}</template>
        </el-table-column>
        <el-table-column label="工时" width="80" align="right">
          <template #default="{ row }">{{ formatNumber(row.work_hours) }}</template>
        </el-table-column>
        <el-table-column label="质量评定" width="95">
          <template #default="{ row }">
            <EnumTag group="quality_result" :value="row.quality_result" :label="row.quality_result_label" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="detailDialog.open(row.id)">详情</el-button>
            <el-button link type="primary" @click="formDialog.open(row)">编辑</el-button>
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

    <RecordFormDialog ref="formDialog" @saved="load" />
    <RecordDetailDialog ref="detailDialog" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'

import { maintenanceRecordApi } from '@/api'
import EnumTag from '@/components/common/EnumTag.vue'
import GreenSpaceSelect from '@/components/common/GreenSpaceSelect.vue'
import PageHeader from '@/components/common/PageHeader.vue'
import { useEnumOptions } from '@/composables/useEnumOptions'
import { useListQuery } from '@/composables/useListQuery'
import { formatHours, formatNumber } from '@/utils/format'

import RecordDetailDialog from './RecordDetailDialog.vue'
import RecordFormDialog from './RecordFormDialog.vue'

const route = useRoute()
const formDialog = ref(null)
const detailDialog = ref(null)
const dateRange = ref([])

const { options: qualityOptions } = useEnumOptions('quality_result')
const { options: weatherOptions } = useEnumOptions('weather')

const { filters, meta, items, summary, loading, load, search, resetFilters, handlePageChange, handleSizeChange } =
  useListQuery(maintenanceRecordApi.list, {
    initialFilters: {
      keyword: '',
      green_space_id: route.query.green_space_id ? Number(route.query.green_space_id) : null,
      task_id: route.query.task_id ? Number(route.query.task_id) : null,
      quality_result: '',
      weather: '',
      date_from: '',
      date_to: '',
      unlinked: false,
    },
  })

function onGreenSpaceChange() {
  filters.task_id = null
  search()
}

function onDateChange(value) {
  filters.date_from = value?.[0] || ''
  filters.date_to = value?.[1] || ''
  search()
}

function reset() {
  dateRange.value = []
  resetFilters()
}

async function remove(row) {
  try {
    await ElMessageBox.confirm(
      row.task
        ? `删除后任务「${row.task.title}」的状态会重新计算，是否继续？`
        : '确认删除该养护记录吗？',
      '删除确认',
      { type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消' },
    )
    await maintenanceRecordApi.remove(row.id)
    ElMessage.success('养护记录已删除')
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

.cell-sub {
  color: #909399;
  font-size: 12px;
}
</style>
