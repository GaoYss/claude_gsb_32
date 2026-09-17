<template>
  <el-tag :type="tagType" :effect="effect" size="small" disable-transitions>{{ text }}</el-tag>
</template>

<script setup>
import { computed } from 'vue'

import { useMetaStore } from '@/stores/meta'

const props = defineProps({
  group: { type: String, required: true },
  value: { type: String, default: '' },
  label: { type: String, default: '' },
  effect: { type: String, default: 'light' },
})

const TAG_TYPES = {
  green_space_status: { normal: 'success', repairing: 'warning', suspended: 'info', archived: 'info' },
  task_status: { pending: 'info', in_progress: 'primary', completed: 'success', cancelled: 'danger' },
  task_priority: { low: 'info', medium: 'primary', high: 'warning', urgent: 'danger' },
  quality_result: { qualified: 'success', pending: 'warning', unqualified: 'danger' },
  maintenance_grade: { level1: 'success', level2: 'primary', level3: 'info' },
  replacement_reason: { dead: 'danger', disease: 'warning', aging: 'info', upgrade: 'primary' },
}

const meta = useMetaStore()
const text = computed(() => props.label || meta.label(props.group, props.value))
const tagType = computed(() => TAG_TYPES[props.group]?.[props.value] ?? 'info')
</script>
