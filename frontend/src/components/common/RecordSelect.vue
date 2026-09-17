<template>
  <el-select
    :model-value="modelValue"
    filterable
    clearable
    :placeholder="placeholder"
    :disabled="disabled || !greenSpaceId"
    :loading="loading"
    :style="{ width: '100%' }"
    @update:model-value="emit('update:modelValue', $event)"
  >
    <el-option
      v-for="item in options"
      :key="item.id"
      :label="`${item.record_no} ${item.record_date} ${item.work_content.slice(0, 16)}`"
      :value="item.id"
    />
  </el-select>
</template>

<script setup>
import { ref, watch } from 'vue'

import { maintenanceRecordApi } from '@/api'

const props = defineProps({
  modelValue: { type: [Number, String], default: null },
  greenSpaceId: { type: [Number, String], default: null },
  preset: { type: Object, default: null },
  placeholder: { type: String, default: '可关联养护记录（选填）' },
  disabled: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue'])

const options = ref([])
const loading = ref(false)

async function load() {
  if (!props.greenSpaceId) {
    options.value = props.preset ? [props.preset] : []
    return
  }
  loading.value = true
  try {
    const data = await maintenanceRecordApi.list({
      green_space_id: props.greenSpaceId,
      page_size: 50,
      sort: 'record_date',
      order: 'desc',
    })
    const map = new Map()
    ;(data?.items || []).forEach((item) => map.set(item.id, item))
    if (props.preset) map.set(props.preset.id, props.preset)
    options.value = [...map.values()]
  } finally {
    loading.value = false
  }
}

watch(() => props.greenSpaceId, load, { immediate: true })
watch(() => props.preset, () => load())
</script>
