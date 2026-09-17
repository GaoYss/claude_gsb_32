<template>
  <el-dialog :model-value="visible" :title="detail.record_no ? `养护记录 · ${detail.record_no}` : '养护记录详情'"
             width="700px" @update:model-value="close">
    <div v-loading="loading">
      <el-descriptions :column="2" border size="small">
        <el-descriptions-item label="所属绿地" :span="2">
          {{ detail.green_space ? `${detail.green_space.code} ${detail.green_space.name}` : '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="关联任务" :span="2">
          <span v-if="detail.task">
            {{ detail.task.task_no }} · {{ detail.task.title }}
            <EnumTag group="task_status" :value="detail.task.status" />
          </span>
          <el-tag v-else size="small" type="info" effect="plain">日常养护（未关联任务）</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="养护日期">{{ formatDate(detail.record_date) }}</el-descriptions-item>
        <el-descriptions-item label="天气">{{ detail.weather_label || '-' }}</el-descriptions-item>
        <el-descriptions-item label="作业人员">{{ detail.worker || '-' }}</el-descriptions-item>
        <el-descriptions-item label="工时">{{ formatHours(detail.work_hours) }}</el-descriptions-item>
        <el-descriptions-item label="质量评定">
          <EnumTag group="quality_result" :value="detail.quality_result" :label="detail.quality_result_label" />
        </el-descriptions-item>
        <el-descriptions-item label="登记时间">{{ formatDateTime(detail.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="作业内容" :span="2">{{ detail.work_content || '-' }}</el-descriptions-item>
        <el-descriptions-item label="使用材料" :span="2">{{ detail.materials || '-' }}</el-descriptions-item>
        <el-descriptions-item label="发现问题" :span="2">{{ detail.issue_found || '-' }}</el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ detail.remark || '-' }}</el-descriptions-item>
      </el-descriptions>

      <div v-if="detail.replacements?.length" class="linked-replacements">
        <div class="panel-title">关联的绿植更换记录</div>
        <el-table :data="detail.replacements" size="small" border>
          <el-table-column prop="replacement_no" label="编号" width="150" />
          <el-table-column prop="plant_name" label="植株" width="120" />
          <el-table-column label="数量" width="110">
            <template #default="{ row }">{{ formatNumber(row.quantity) }} {{ row.unit_label }}</template>
          </el-table-column>
          <el-table-column label="更换原因" width="120">
            <template #default="{ row }">
              <EnumTag group="replacement_reason" :value="row.reason" :label="row.reason_label" />
            </template>
          </el-table-column>
          <el-table-column label="金额" width="120" align="right">
            <template #default="{ row }">{{ formatCurrency(row.amount) }}</template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <template #footer>
      <el-button @click="close">关闭</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref } from 'vue'

import { maintenanceRecordApi } from '@/api'
import EnumTag from '@/components/common/EnumTag.vue'
import { formatCurrency, formatDate, formatDateTime, formatHours, formatNumber } from '@/utils/format'

const visible = ref(false)
const loading = ref(false)
const detail = ref({})

async function open(id) {
  visible.value = true
  loading.value = true
  try {
    detail.value = await maintenanceRecordApi.detail(id)
  } finally {
    loading.value = false
  }
}

function close() {
  visible.value = false
}

defineExpose({ open })
</script>

<style scoped>
.linked-replacements {
  margin-top: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.panel-title {
  font-weight: 600;
}
</style>
