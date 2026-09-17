<template>
  <el-dialog :model-value="visible" :title="isEdit ? `编辑养护任务 · ${form.task_no}` : '登记养护任务'"
             width="720px" top="7vh" destroy-on-close @update:model-value="close">
    <el-form ref="formRef" :model="form" :rules="rules" label-width="120px">
      <el-form-item label="所属绿地" prop="green_space_id" :error="fieldErrors.green_space_id">
        <GreenSpaceSelect v-model="form.green_space_id" :preset="spacePreset" placeholder="请选择绿地" />
      </el-form-item>
      <el-form-item label="任务名称" prop="title" :error="fieldErrors.title">
        <el-input v-model="form.title" placeholder="如：行道树整形修剪" maxlength="128" />
      </el-form-item>
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="养护类型" prop="task_type" :error="fieldErrors.task_type">
            <el-select v-model="form.task_type" placeholder="请选择" style="width: 100%">
              <el-option v-for="item in typeOptions" :key="item.value" :label="item.label" :value="item.value" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="计划日期" prop="plan_date" :error="fieldErrors.plan_date">
            <el-date-picker v-model="form.plan_date" type="date" value-format="YYYY-MM-DD"
                            placeholder="选择计划养护日期" style="width: 100%" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="优先级" :error="fieldErrors.priority">
            <el-select v-model="form.priority" style="width: 100%">
              <el-option v-for="item in priorityOptions" :key="item.value" :label="item.label" :value="item.value" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="执行班组" :error="fieldErrors.executor">
            <el-input v-model="form.executor" placeholder="如：绿化一班" maxlength="64" />
          </el-form-item>
        </el-col>
        <el-col v-if="isEdit" :span="12">
          <el-form-item label="任务状态" :error="fieldErrors.status">
            <el-select v-model="form.status" style="width: 100%">
              <el-option v-for="item in statusOptions" :key="item.value" :label="item.label" :value="item.value" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>
      <el-form-item label="任务说明" :error="fieldErrors.description">
        <el-input v-model="form.description" type="textarea" :rows="3" maxlength="2000"
                  placeholder="作业范围、技术要求、注意事项等" />
      </el-form-item>
      <div class="form-hint">
        任务编号由系统按日自动生成；任务执行后可在「养护记录」中登记作业明细，任务状态会随之自动流转。
      </div>
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

import { maintenanceTaskApi } from '@/api'
import GreenSpaceSelect from '@/components/common/GreenSpaceSelect.vue'
import { useEnumOptions } from '@/composables/useEnumOptions'
import { today } from '@/utils/format'

const emit = defineEmits(['saved'])

const { options: typeOptions } = useEnumOptions('task_type')
const { options: priorityOptions } = useEnumOptions('task_priority')
const { options: statusOptions } = useEnumOptions('task_status')

const formRef = ref(null)
const visible = ref(false)
const submitting = ref(false)
const editingId = ref(null)
const fieldErrors = ref({})
const spacePreset = ref(null)
const form = reactive(emptyForm())

const isEdit = computed(() => editingId.value !== null)

const rules = {
  green_space_id: [{ required: true, message: '请选择所属绿地', trigger: 'change' }],
  title: [{ required: true, message: '请输入任务名称', trigger: 'blur' }],
  task_type: [{ required: true, message: '请选择养护类型', trigger: 'change' }],
  plan_date: [{ required: true, message: '请选择计划日期', trigger: 'change' }],
}

function emptyForm() {
  return {
    task_no: '',
    green_space_id: null,
    title: '',
    task_type: 'prune',
    plan_date: today(),
    priority: 'medium',
    executor: '',
    status: 'pending',
    description: '',
  }
}

function open(row = null) {
  Object.assign(form, emptyForm())
  fieldErrors.value = {}
  spacePreset.value = null
  editingId.value = row?.id ?? null
  if (row) {
    Object.keys(form).forEach((key) => {
      if (row[key] !== undefined && row[key] !== null) form[key] = row[key]
    })
    form.green_space_id = row.green_space_id
    spacePreset.value = row.green_space || null
  }
  visible.value = true
}

function close() {
  visible.value = false
}

async function submit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  fieldErrors.value = {}
  const payload = { ...form }
  if (!payload.task_no) delete payload.task_no
  try {
    if (isEdit.value) {
      await maintenanceTaskApi.update(editingId.value, payload)
      ElMessage.success('养护任务已更新')
    } else {
      await maintenanceTaskApi.create(payload)
      ElMessage.success('养护任务登记成功')
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
