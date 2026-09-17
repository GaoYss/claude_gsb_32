<template>
  <div class="panel chart-panel">
    <div class="chart-panel__head">
      <span class="chart-panel__title">{{ title }}</span>
      <span v-if="hint" class="chart-panel__hint">{{ hint }}</span>
    </div>
    <BaseChart :option="option" :height="height" />
  </div>
</template>

<script setup>
import BaseChart from './BaseChart.vue'

defineProps({
  title: { type: String, required: true },
  hint: { type: String, default: '' },
  option: { type: Object, required: true },
  height: { type: String, default: '280px' },
})
</script>

<style scoped>
.chart-panel__head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: 8px;
}

.chart-panel__title {
  font-weight: 600;
}

.chart-panel__hint {
  color: #909399;
  font-size: 12px;
}
</style>
