<!--
执行详情页面
展示单个执行任务的完整详情
-->
<template>
  <div class="execution-detail">
    <div class="page-header">
      <div class="header-left">
        <el-button @click="handleBack" circle>
          <el-icon><ArrowLeft /></el-icon>
        </el-button>
        <h1>执行详情 #{{ executionId }}</h1>
      </div>
    </div>

    <div v-loading="loading" class="detail-content">
      <ExecutionDetailPanel
        v-if="execution"
        :execution="execution"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getExecution, getExecutionDetails } from '@/api/execution'
import type { Execution } from '@/api/execution'
import ExecutionDetailPanel from '@/components/ExecutionDetailPanel.vue'

const route = useRoute()
const router = useRouter()

const executionId = computed(() => Number(route.params.id))
const loading = ref(false)
const execution = ref<Execution | null>(null)

const loadExecution = async () => {
  loading.value = true
  try {
    const [execResponse, detailsResponse] = await Promise.all([
      getExecution(executionId.value),
      getExecutionDetails(executionId.value)
    ])
    execution.value = {
      ...execResponse.data,
      details: detailsResponse.data
    }
  } catch (error) {
    ElMessage.error('获取执行详情失败')
    router.push('/reports')
  } finally {
    loading.value = false
  }
}

const handleBack = () => {
  router.back()
}

onMounted(() => {
  loadExecution()
})
</script>

<style scoped lang="scss">
.execution-detail {
  padding: 20px;
  background: #f5f5f5;
  min-height: 100vh;

  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;

    .header-left {
      display: flex;
      align-items: center;
      gap: 16px;

      h1 {
        margin: 0;
        font-size: 20px;
        font-weight: 500;
      }
    }
  }

  .detail-content {
    min-height: 400px;
  }
}
</style>
