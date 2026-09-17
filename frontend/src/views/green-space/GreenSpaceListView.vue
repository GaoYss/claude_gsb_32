<template>
  <div class="page">
    <PageHeader title="绿地台账" description="城市绿地基础档案，养护任务与记录均以此台账为归属">
      <template #actions>
        <el-button type="primary" :icon="'Plus'" @click="formDialog.open()">新增绿地</el-button>
      </template>
    </PageHeader>

    <div class="panel">
      <div class="filter-bar">
        <el-input
          v-model="filters.keyword"
          placeholder="编号 / 名称 / 地址 / 负责人"
          clearable
          :prefix-icon="'Search'"
          @keyup.enter="search"
          @clear="search"
        />
        <el-select v-model="filters.district" placeholder="所属行政区" clearable @change="search">
          <el-option v-for="item in districts" :key="item.district" :label="item.district" :value="item.district" />
        </el-select>
        <el-select v-model="filters.green_type" placeholder="绿地类型" clearable @change="search">
          <el-option v-for="item in typeOptions" :key="item.value" :label="item.label" :value="item.value" />
        </el-select>
        <el-select v-model="filters.maintenance_grade" placeholder="养护等级" clearable @change="search">
          <el-option v-for="item in gradeOptions" :key="item.value" :label="item.label" :value="item.value" />
        </el-select>
        <el-select v-model="filters.status" placeholder="养护状态" clearable @change="search">
          <el-option v-for="item in statusOptions" :key="item.value" :label="item.label" :value="item.value" />
        </el-select>
        <el-button type="primary" :icon="'Search'" @click="search">查询</el-button>
        <el-button :icon="'RefreshLeft'" @click="resetFilters">重置</el-button>
      </div>
    </div>

    <div class="panel">
      <div class="table-toolbar">
        <span class="summary-text">
          共 <strong>{{ meta.total }}</strong> 处绿地，合计面积
          <strong>{{ formatArea(summary?.total_area) }}</strong>
        </span>
        <el-button :icon="'Refresh'" text @click="load">刷新</el-button>
      </div>

      <el-table :data="items" v-loading="loading" border stripe>
        <el-table-column prop="code" label="绿地编号" width="135" />
        <el-table-column label="绿地名称" min-width="170" show-overflow-tooltip>
          <template #default="{ row }">
            <div class="cell-main">{{ row.name }}</div>
            <div class="cell-sub">负责人：{{ row.manager || '未指定' }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="district" label="行政区" width="90" />
        <el-table-column label="绿地类型" width="110">
          <template #default="{ row }">
            <EnumTag group="green_space_type" :value="row.green_type" :label="row.green_type_label" />
          </template>
        </el-table-column>
        <el-table-column label="养护等级" width="100">
          <template #default="{ row }">
            <EnumTag group="maintenance_grade" :value="row.maintenance_grade" :label="row.maintenance_grade_label" />
          </template>
        </el-table-column>
        <el-table-column label="面积" width="105" align="right">
          <template #default="{ row }">{{ formatArea(row.area_sqm) }}</template>
        </el-table-column>
        <el-table-column label="养护状态" width="105">
          <template #default="{ row }">
            <EnumTag group="green_space_status" :value="row.status" :label="row.status_label" />
          </template>
        </el-table-column>
        <el-table-column label="养护概况" min-width="170">
          <template #default="{ row }">
            <span class="summary-text">
              任务 {{ row.statistics.task_count }} 项（未完成 {{ row.statistics.open_task_count }}）、
              记录 {{ row.statistics.record_count }} 条
            </span>
            <div class="summary-text">
              最近养护：{{ formatDate(row.statistics.last_maintenance_date) }}
            </div>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="190" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="goDetail(row)">档案</el-button>
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

    <GreenSpaceFormDialog ref="formDialog" @saved="onSaved" />
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'

import { greenSpaceApi } from '@/api'
import EnumTag from '@/components/common/EnumTag.vue'
import PageHeader from '@/components/common/PageHeader.vue'
import { useEnumOptions } from '@/composables/useEnumOptions'
import { useListQuery } from '@/composables/useListQuery'
import { formatArea, formatDate } from '@/utils/format'

import GreenSpaceFormDialog from './GreenSpaceFormDialog.vue'

const router = useRouter()
const formDialog = ref(null)
const districts = ref([])

const { options: typeOptions } = useEnumOptions('green_space_type')
const { options: gradeOptions } = useEnumOptions('maintenance_grade')
const { options: statusOptions } = useEnumOptions('green_space_status')

const { filters, meta, items, summary, loading, load, search, resetFilters, handlePageChange, handleSizeChange } =
  useListQuery(greenSpaceApi.list, {
    initialFilters: { keyword: '', district: '', green_type: '', maintenance_grade: '', status: '' },
  })

async function loadDistricts() {
  const data = await greenSpaceApi.districts()
  districts.value = data?.items || []
}

function goDetail(row) {
  router.push({ name: 'green-space-detail', params: { id: row.id } })
}

async function onSaved() {
  await Promise.all([load(), loadDistricts()])
}

async function remove(row) {
  const hasChildren = row.statistics.task_count + row.statistics.record_count + row.statistics.replacement_count > 0
  try {
    if (hasChildren) {
      await ElMessageBox.confirm(
        `该绿地已关联 ${row.statistics.task_count} 项养护任务、${row.statistics.record_count} 条养护记录、` +
          `${row.statistics.replacement_count} 条更换记录，删除将一并清除，是否继续？`,
        '存在关联数据',
        { type: 'warning', confirmButtonText: '确认删除', cancelButtonText: '取消' },
      )
    } else {
      await ElMessageBox.confirm(`确认删除绿地「${row.name}」吗？`, '删除确认', {
        type: 'warning',
        confirmButtonText: '删除',
        cancelButtonText: '取消',
      })
    }
    await greenSpaceApi.remove(row.id, hasChildren ? { force: true } : undefined)
    ElMessage.success('绿地台账已删除')
    await onSaved()
  } catch (error) {
    if (error !== 'cancel' && error !== 'close' && error?.message) {
      // 错误提示已由请求层统一处理
    }
  }
}

onMounted(loadDistricts)
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
