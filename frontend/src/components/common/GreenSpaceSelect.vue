<template>
  <el-select
    :model-value="modelValue"
    filterable
    remote
    clearable
    :remote-method="remoteSearch"
    :loading="loading"
    :placeholder="placeholder"
    :disabled="disabled"
    :style="{ width: '100%' }"
    @update:model-value="emit('update:modelValue', $event)"
  >
    <el-option
      v-for="item in options"
      :key="item.id"
      :label="`${item.code} ${item.name}`"
      :value="item.id"
    />
  </el-select>
</template>

<script setup>
import { onMounted, ref } from 'vue'

import { greenSpaceApi } from '@/api'

const props = defineProps({
  modelValue: { type: [Number, String], default: null },
  preset: { type: Object, default: null },
  placeholder: { type: String, default: '请选择绿地' },
  disabled: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue'])

const options = ref([])
const loading = ref(false)

function merge(items) {
  const map = new Map()
  items.filter(Boolean).forEach((item) => map.set(item.id, item))
  if (props.preset) map.set(props.preset.id, props.preset)
  options.value = [...map.values()]
}

async function load(keyword) {
  loading.value = true
  try {
    const data = await greenSpaceApi.options(keyword ? { keyword } : undefined)
    merge(data?.items || [])
    if (props.preset) merge([props.preset, ...(data?.items || [])])
  } finally {
    loading.value = false
  }
}

function remoteSearch(keyword) {
  return load(keyword?.trim() || undefined)
}

onMounted(() => load())
</script>
