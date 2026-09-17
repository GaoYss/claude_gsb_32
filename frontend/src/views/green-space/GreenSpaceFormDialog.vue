<template>
  <el-dialog
    :model-value="visible"
    :title="isEdit ? `编辑绿地台账 · ${form.code}` : '新增绿地台账'"
    width="760px"
    top="6vh"
    destroy-on-close
    @update:model-value="close"
    @closed="fieldErrors = {}"
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-width="110px">
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="绿地名称" prop="name" :error="fieldErrors.name">
            <el-input v-model="form.name" placeholder="如：运河文化公园" maxlength="128" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="绿地编号" :error="fieldErrors.code">
            <el-input v-model="form.code" :disabled="isEdit" placeholder="留空则自动生成，如 GS-2026-0001" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="所属行政区" prop="district" :error="fieldErrors.district">
            <el-select v-model="form.district" filterable allow-create default-first-option
                       placeholder="选择或输入行政区" style="width: 100%">
              <el-option v-for="item in districts" :key="item.district" :label="item.district" :value="item.district" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="绿地类型" prop="green_type" :error="fieldErrors.green_type">
            <el-select v-model="form.green_type" placeholder="请选择" style="width: 100%">
              <el-option v-for="item in typeOptions" :key="item.value" :label="item.label" :value="item.value" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="养护等级" prop="maintenance_grade" :error="fieldErrors.maintenance_grade">
            <el-select v-model="form.maintenance_grade" placeholder="请选择" style="width: 100%">
              <el-option v-for="item in gradeOptions" :key="item.value" :label="item.label" :value="item.value" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="养护状态" prop="status" :error="fieldErrors.status">
            <el-select v-model="form.status" placeholder="请选择" style="width: 100%">
              <el-option v-for="item in statusOptions" :key="item.value" :label="item.label" :value="item.value" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="绿地面积" prop="area_sqm" :error="fieldErrors.area_sqm">
            <el-input-number v-model="form.area_sqm" :min="0" :max="99999999" :precision="2"
                             :controls="false" placeholder="单位：平方米" style="width: 100%" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="建成日期" :error="fieldErrors.established_date">
            <el-date-picker v-model="form.established_date" type="date" value-format="YYYY-MM-DD"
                            placeholder="选择日期" style="width: 100%" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="养护负责人" :error="fieldErrors.manager">
            <el-input v-model="form.manager" placeholder="如：沈建国" maxlength="64" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="联系电话" :error="fieldErrors.contact_phone">
            <el-input v-model="form.contact_phone" placeholder="如：0571-85112233" maxlength="32" />
          </el-form-item>
        </el-col>
        <el-col :span="24">
          <el-form-item label="详细地址" :error="fieldErrors.address">
            <el-input v-model="form.address" placeholder="如：环城北路武林广场南侧" maxlength="255" />
          </el-form-item>
        </el-col>
        <el-col :span="24">
          <el-form-item label="主要植物概况" :error="fieldErrors.plant_summary">
            <el-input v-model="form.plant_summary" type="textarea" :rows="2" maxlength="2000"
                      placeholder="如：香樟 86 株、红叶石楠球 42 株、时令花坛 420 平方米" />
          </el-form-item>
        </el-col>
        <el-col :span="24">
          <el-form-item label="备注" :error="fieldErrors.remark">
            <el-input v-model="form.remark" type="textarea" :rows="2" maxlength="2000"
                      placeholder="养护注意事项、移交情况等" />
          </el-form-item>
        </el-col>
      </el-row>
    </el-form>

    <template #footer>
      <el-button @click="close">取消</el-button>
      <el-button type="primary" :loading="submitting" @click="submit">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'

import { greenSpaceApi } from '@/api'
import { useEnumOptions } from '@/composables/useEnumOptions'

const emit = defineEmits(['saved'])

const { options: typeOptions } = useEnumOptions('green_space_type')
const { options: gradeOptions } = useEnumOptions('maintenance_grade')
const { options: statusOptions } = useEnumOptions('green_space_status')

const formRef = ref(null)
const visible = ref(false)
const submitting = ref(false)
const editingId = ref(null)
const fieldErrors = ref({})
const districts = ref([])

const form = reactive(emptyForm())

const isEdit = computed(() => editingId.value !== null)

const rules = {
  name: [{ required: true, message: '请输入绿地名称', trigger: 'blur' }],
  district: [{ required: true, message: '请选择所属行政区', trigger: 'change' }],
  green_type: [{ required: true, message: '请选择绿地类型', trigger: 'change' }],
  maintenance_grade: [{ required: true, message: '请选择养护等级', trigger: 'change' }],
  area_sqm: [{ required: true, message: '请输入绿地面积', trigger: 'blur' }],
}

function emptyForm() {
  return {
    code: '',
    name: '',
    district: '',
    address: '',
    green_type: 'park',
    maintenance_grade: 'level2',
    status: 'normal',
    area_sqm: null,
    manager: '',
    contact_phone: '',
    established_date: '',
    plant_summary: '',
    remark: '',
  }
}

function open(row = null) {
  Object.assign(form, emptyForm())
  fieldErrors.value = {}
  editingId.value = row?.id ?? null
  if (row) {
    Object.keys(form).forEach((key) => {
      if (row[key] !== undefined && row[key] !== null) form[key] = row[key]
    })
  }
  visible.value = true
}

function close() {
  visible.value = false
}

function buildPayload() {
  const payload = { ...form }
  if (!payload.code) delete payload.code
  if (!payload.established_date) delete payload.established_date
  return payload
}

async function submit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  fieldErrors.value = {}
  try {
    if (isEdit.value) {
      await greenSpaceApi.update(editingId.value, buildPayload())
      ElMessage.success('绿地台账已更新')
    } else {
      await greenSpaceApi.create(buildPayload())
      ElMessage.success('绿地台账创建成功')
    }
    emit('saved')
    close()
  } catch (error) {
    fieldErrors.value = error?.details || {}
  } finally {
    submitting.value = false
  }
}

async function loadDistricts() {
  const data = await greenSpaceApi.districts()
  districts.value = data?.items || []
}

defineExpose({ open })
onMounted(loadDistricts)
</script>
