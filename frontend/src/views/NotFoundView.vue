<template>
  <el-result icon="warning" title="页面不存在" sub-title="请检查地址是否正确，或返回养护总览">
    <template #extra>
      <el-button type="primary" @click="router.push('/dashboard')">返回养护总览</el-button>
    </template>
  </el-result>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()
</script>
