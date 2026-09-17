<template>
  <div class="page-header">
    <div>
      <h2 class="page-header__title">
        {{ title }}
        <slot name="tag" />
      </h2>
      <p v-if="description" class="page-header__desc">{{ description }}</p>
    </div>
    <div class="page-header__actions">
      <slot name="actions" />
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, required: true },
  description: { type: String, default: '' },
})
</script>

<style scoped>
.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.page-header__title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.page-header__desc {
  margin: 6px 0 0;
  color: #909399;
  font-size: 13px;
}

.page-header__actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}
</style>
