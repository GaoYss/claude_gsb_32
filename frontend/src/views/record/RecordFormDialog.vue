<template>
  <el-dialog :model-value="visible" :title="isEdit ? `编辑养护记录 · ${form.record_no}` : '录入养护记录'"
             width="760px" top="6vh" destroy-on-close @update:model-value="close">
    <el-form ref="formRef" :model="form" :rules="rules" label-width="120px">
      <el-form-item label="所属绿地" prop="green_space_id" :error="fieldErrors.green_space_id">
        <GreenSpaceSelect v-model="form.green_space_id" :preset="spacePreset"
                          placeholder="选择绿地（可与右侧任务二选一）"
                          @update:model-value="onGreenSpaceChange" />
      </el-form-item>
      <el-form-item label="关联养护任务" :error="fieldErrors.task_id">
        <TaskSelect v-model="form.task_id" :green-space-id="form.green_space_id" :preset="taskPreset"
                    @update:model-value="onTaskChange" />
        <div class="form-hint">关联任务后，绿地自动跟随任务；任务状态会随本记录的评定结果自动流转。</div>
      </el-form-item>
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="养护日期" prop="record_date" :error="fieldErrors.record_date">
            <el-date-picker v-model="form.record_date" type="date" value-format="YYYY-MM-DD"
                            placeholder="选择养护日期" style="width: 100%" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="天气" :error="fieldErrors.weather">
            <el-select v-model="form.weather" clearable placeholder="选择天气" style="width: 100%">
              <el-option v-for="item in weatherOptions" :key="item.value" :label="item.label" :value="item.value" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="作业人员" :error="fieldErrors.worker">
            <el-input v-model="form.worker" placeholder="如：王海涛" maxlength="64" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="工时" :error="fieldErrors.work_hours">
            <el-input-number v-model="form.work_hours" :min="0" :max="1000" :precision="1"
                             :controls="false" placeholder="单位：小时" style="width: 100%" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-form-item label="作业内容" prop="work_content" :error="fieldErrors.work_content">
        <el-input v-model="form.work_content" type="textarea" :rows="3" maxlength="4000"
                  placeholder="如：修剪香樟下垂枝 32 株，清运枝条 2 车" />
      </el-form-item>
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="质量评定" :error="fieldErrors.quality_result">
            <el-select v-model="form.quality_result" style="width: 100%">
              <el-option v-for="item in qualityOptions" :key="item.value" :label="item.label" :value="item.value" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="使用材料/药剂" :error="fieldErrors.materials">
            <el-input v-model="form.materials" placeholder="如：复合肥 180kg" maxlength="1000" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-form-item label="发现问题" :error="fieldErrors.issue_found">
        <el-input v-model="form.issue_found" type="textarea" :rows="2" maxlength="2000"
                  placeholder="巡查或作业中发现的问题及处理情况" />
      </el-form-item>
      <el-form-item label="备注" :error="fieldErrors.remark">
        <el-input v-model="form.remark" type="textarea" :rows="2" maxlength="2000" />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="close">取消</el-button>
      <el-button type="primary" :loading="submitting" @click="submit">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'

import { maintenanceRecordApi, maintenanceTaskApi } from '@/api'
import GreenSpaceSelect from '@/components/common/GreenSpaceSelect.vue'
import TaskSelect from '@/components/common/TaskSelect.vue'
import { useEnumOptions } from '@/composables/useEnumOptions'
import { today } from '@/utils/format'

const emit = defineEmits(['saved'])

const { options: qualityOptions } = useEnumOptions('quality_result')
const { options: weatherOptions } = useEnumOptions('weather')

const formRef = ref(null)
const visible = ref(false)
const submitting = ref(false)
const editingId = ref(null)
const fieldErrors = ref({})
const spacePreset = ref(null)
const taskPreset = ref(null)
const form = reactive(emptyForm())

const isEdit = computed(() => editingId.value !== null)

const rules = {
  record_date: [{ required: true, message: '请选择养护日期', trigger: 'change' }],
  work_content: [{ required: true, message: '请输入作业内容', trigger: 'blur' }],
}

function emptyForm() {
  return {
    record_no: '',
    green_space_id: null,
    task_id: null,
    record_date: today(),
    work_content: '',
    worker: '',
    work_hours: null,
    weather: '',
    materials: '',
    quality_result: 'qualified',
    issue_found: '',
    remark: '',
  }
}

function open(row = null) {
  Object.assign(form, emptyForm())
  fieldErrors.value = {}
  spacePreset.value = null
  taskPreset.value = null
  editingId.value = row?.id ?? null
  if (row) {
    Object.keys(form).forEach((key) => {
      if (row[key] !== undefined && row[key] !== null) form[key] = row[key]
    })
    spacePreset.value = row.green_space || null
    taskPreset.value = row.task ? { ...row.task, id: row.task_id } : null
  }
  visible.value = true
}

function close() {
  visible.value = false
}

function onGreenSpaceChange() {
  form.task_id = null
  taskPreset.value = null
}

async function onTaskChange(taskId) {
  if (!taskId) return
  const task = await maintenanceTaskApi.detail(taskId).catch(() => null)
  if (task?.green_space) {
    form.green_space_id = task.green_space_id
    spacePreset.value = task.green_space
    taskPreset.value = { id: task.id, task_no: task.task_no, title: task.title, status: task.status }
  }
}

async function submit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  if (!form.green_space_id && !form.task_id) {
    fieldErrors.value = { green_space_id: '请选择所属绿地或关联养护任务' }
    return
  }
  submitting.value = true
  fieldErrors.value = {}
  const payload = { ...form }
  delete payload.task_no
  if (!payload.record_no) delete payload.record_no
  if (!payload.task_id) payload.task_id = null
  try {
    if (isEdit.value) {
      await maintenanceRecordApi.update(editingId.value, payload)
      ElMessage.success('养护记录已更新')
    } else {
      await maintenanceRecordApi.create(payload)
      ElMessage.success('养护记录录入成功')
    }
    emit('saved')
    close()
  } catch (error) {
    fieldErrors.value = error?.details || {}
  } finally {
    submitting.value = false
  }
}

defineExpose({ open })
</script>
