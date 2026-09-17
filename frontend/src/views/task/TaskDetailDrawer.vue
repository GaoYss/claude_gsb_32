<template>
  <el-drawer :model-value="visible" size="640px" :title="detail.task_no ? `养护任务 · ${detail.task_no}` : '养护任务详情'"
             @update:model-value="close">
    <div v-loading="loading" class="drawer-body">
      <el-descriptions :column="2" border size="small">
        <el-descriptions-item label="任务名称" :span="2">{{ detail.title }}</el-descriptions-item>
        <el-descriptions-item label="所属绿地" :span="2">
          {{ detail.green_space ? `${detail.green_space.code} ${detail.green_space.name}` : '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="养护类型">
          <EnumTag group="task_type" :value="detail.task_type" :label="detail.task_type_label" />
        </el-descriptions-item>
        <el-descriptions-item label="优先级">
          <EnumTag group="task_priority" :value="detail.priority" :label="detail.priority_label" />
        </el-descriptions-item>
        <el-descriptions-item label="计划日期">
          {{ formatDate(detail.plan_date) }}
          <el-tag v-if="detail.is_overdue" type="danger" size="small" effect="plain">逾期</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="执行班组">{{ detail.executor || '-' }}</el-descriptions-item>
        <el-descriptions-item label="任务状态">
          <EnumTag group="task_status" :value="detail.status" :label="detail.status_label" />
        </el-descriptions-item>
        <el-descriptions-item label="完成时间">{{ formatDateTime(detail.completed_at) }}</el-descriptions-item>
        <el-descriptions-item label="任务说明" :span="2">{{ detail.description || '-' }}</el-descriptions-item>
      </el-descriptions>

      <div class="stat-grid drawer-stats">
        <StatCard label="养护记录" :value="progress.record_count ?? 0" unit="条"
                  :hint="`合格 ${progress.qualified_count ?? 0} 条，不合格 ${progress.unqualified_count ?? 0} 条`" />
        <StatCard label="累计工时" :value="formatHours(progress.total_work_hours)" />
        <StatCard label="关联更换" :value="formatNumber(progress.replacement_quantity)"
                  :hint="`金额 ${formatCurrency(progress.replacement_amount)}`" />
      </div>

      <div class="table-toolbar">
        <span class="panel-title">养护记录</span>
        <el-button v-if="detail.green_space" link type="primary"
                   @click="goRecords">去登记养护记录</el-button>
      </div>
      <el-table :data="detail.records || []" size="small" border empty-text="该任务还没有养护记录">
        <el-table-column prop="record_no" label="记录编号" width="150" />
        <el-table-column prop="record_date" label="养护日期" width="105" />
        <el-table-column prop="work_content" label="作业内容" min-width="180" show-overflow-tooltip />
        <el-table-column label="工时" width="80">
          <template #default="{ row }">{{ formatNumber(row.work_hours) }}</template>
        </el-table-column>
        <el-table-column label="质量评定" width="95">
          <template #default="{ row }">
            <EnumTag group="quality_result" :value="row.quality_result" :label="row.quality_result_label" />
          </template>
        </el-table-column>
      </el-table>
    </div>

    <template #footer>
      <el-button @click="close">关闭</el-button>
      <el-button v-if="detail.status !== 'completed' && detail.status !== 'cancelled'" type="primary"
                 @click="complete">标记完成</el-button>
    </template>
  </el-drawer>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

import { maintenanceTaskApi } from '@/api'
import EnumTag from '@/components/common/EnumTag.vue'
import StatCard from '@/components/common/StatCard.vue'
import { formatCurrency, formatDate, formatDateTime, formatHours, formatNumber } from '@/utils/format'

const emit = defineEmits(['updated'])
const router = useRouter()

const visible = ref(false)
const loading = ref(false)
const detail = ref({})
const currentId = ref(null)
const progress = computed(() => detail.value.progress || {})

async function open(id) {
  currentId.value = id
  visible.value = true
  await load()
}

async function load() {
  if (!currentId.value) return
  loading.value = true
  try {
    detail.value = await maintenanceTaskApi.detail(currentId.value)
  } finally {
    loading.value = false
  }
}

function close() {
  visible.value = false
}

function goRecords() {
  router.push({ name: 'record-list', query: { task_id: currentId.value } })
  close()
}

async function complete() {
  try {
    await maintenanceTaskApi.changeStatus(currentId.value, { status: 'completed' })
    ElMessage.success('任务已标记完成')
    await load()
    emit('updated')
  } catch {
    // 存在不合格记录时后端会拒绝，提示由请求层统一处理
  }
}

defineExpose({ open })
</script>

<style scoped>
.drawer-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.drawer-stats {
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
}

.panel-title {
  font-weight: 600;
}
</style>
