<template>
  <div class="stat-card" :class="`stat-card--${tone}`">
    <div class="stat-card__label">
      <el-icon v-if="icon"><component :is="icon" /></el-icon>
      <span>{{ label }}</span>
    </div>
    <div class="stat-card__value">
      {{ value }}
      <span v-if="unit" class="stat-card__unit">{{ unit }}</span>
    </div>
    <div v-if="hint" class="stat-card__hint">{{ hint }}</div>
  </div>
</template>

<script setup>
defineProps({
  label: { type: String, required: true },
  value: { type: [String, Number], default: '-' },
  unit: { type: String, default: '' },
  hint: { type: String, default: '' },
  icon: { type: String, default: '' },
  tone: { type: String, default: 'default' },
})
</script>

<style scoped>
.stat-card {
  background: #fff;
  border: 1px solid var(--gs-border);
  border-radius: 8px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  border-left: 3px solid var(--gs-primary-light);
}

.stat-card--warning {
  border-left-color: #e6a23c;
}

.stat-card--danger {
  border-left-color: #f56c6c;
}

.stat-card--info {
  border-left-color: #909399;
}

.stat-card__label {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #909399;
  font-size: 13px;
}

.stat-card__value {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  line-height: 1.2;
}

.stat-card__unit {
  font-size: 13px;
  color: #909399;
  margin-left: 4px;
}

.stat-card__hint {
  color: #909399;
  font-size: 12px;
}
</style>
