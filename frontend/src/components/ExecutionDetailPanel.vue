<!--
执行详情面板组件
展示单个执行的详细信息，包括每个用例的执行结果
-->
<template>
  <div class="execution-detail-panel">
    <!-- 执行概要 -->
    <div class="execution-summary">
      <div class="summary-item">
        <span class="label">执行 ID:</span>
        <span class="value">{{ execution.id }}</span>
      </div>
      <div class="summary-item">
        <span class="label">浏览器:</span>
        <span class="value">{{ getBrowserLabel(execution.browser) }}</span>
      </div>
      <div class="summary-item">
        <span class="label">状态:</span>
        <el-tag :type="getStatusType(execution.status)" size="small">
          {{ getStatusLabel(execution.status) }}
        </el-tag>
      </div>
      <div class="summary-item">
        <span class="label">总用例:</span>
        <span class="value">{{ execution.total_cases }}</span>
      </div>
      <div class="summary-item">
        <span class="label">通过:</span>
        <span class="value success">{{ execution.passed_cases }}</span>
      </div>
      <div class="summary-item">
        <span class="label">失败:</span>
        <span class="value failed">{{ execution.failed_cases }}</span>
      </div>
      <div class="summary-item">
        <span class="label">通过率:</span>
        <span class="value">{{ passRate }}%</span>
      </div>
    </div>

    <!-- 用例执行结果 -->
    <div class="case-results">
      <h3>用例执行结果</h3>
      <el-table :data="execution.details" stripe max-height="400">
        <el-table-column prop="case_id" label="用例 ID" width="80" />
        <el-table-column prop="case_name" label="用例名称" min-width="200" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'completed' ? 'success' : 'danger'" size="small">
              {{ row.status === 'completed' ? '通过' : '失败' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="步骤统计" width="150">
          <template #default="{ row }">
            通过: {{ row.passed_steps }} / 失败: {{ row.failed_steps }}
          </template>
        </el-table-column>
        <el-table-column prop="started_at" label="开始时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.started_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="completed_at" label="完成时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.completed_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button
              v-if="row.screenshot_path"
              type="primary"
              size="small"
              link
              @click="handleViewScreenshot(row.screenshot_path!)"
            >
              <el-icon><Picture /></el-icon>
              查看截图
            </el-button>
            <el-button
              v-if="row.error_message"
              type="warning"
              size="small"
              link
              @click="handleViewError(row.error_message!)"
            >
              <el-icon><Document /></el-icon>
              查看错误
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 截图对话框 -->
    <el-dialog
      v-model="screenshotDialogVisible"
      title="查看截图"
      width="70%"
      destroy-on-close
    >
      <img :src="screenshotUrl" style="width: 100%" />
    </el-dialog>

    <!-- 错误信息对话框 -->
    <el-dialog
      v-model="errorDialogVisible"
      title="错误信息"
      width="50%"
    >
      <pre class="error-content">{{ currentErrorMessage }}</pre>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { Execution } from '@/api/execution'

// ========== Props & Emits ==========
interface Props {
  execution: Execution
}

interface Emits {
  (e: 'close'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// ========== 数据 ==========
const screenshotDialogVisible = ref(false)
const errorDialogVisible = ref(false)
const currentScreenshotPath = ref('')
const currentErrorMessage = ref('')

// ========== 计算属性 ==========

const passRate = computed(() => {
  if (!props.execution.total_cases) return 0
  return Math.round((props.execution.passed_cases / props.execution.total_cases) * 100)
})

const screenshotUrl = computed(() => {
  if (!currentScreenshotPath.value) return ''
  return `/api/screenshots/${currentScreenshotPath.value}`
})

// ========== 方法 ==========

const getBrowserLabel = (browser: string) => {
  const map: Record<string, string> = {
    chrome: 'Chrome',
    firefox: 'Firefox',
    edge: 'Edge'
  }
  return map[browser] || browser
}

const getStatusType = (status: string) => {
  const map: Record<string, string> = {
    pending: 'info',
    running: 'warning',
    completed: 'success',
    failed: 'danger',
    cancelled: ''
  }
  return map[status] || ''
}

const getStatusLabel = (status: string) => {
  const map: Record<string, string> = {
    pending: '待执行',
    running: '执行中',
    completed: '已完成',
    failed: '失败',
    cancelled: '已取消'
  }
  return map[status] || status
}

const formatDate = (dateStr?: string) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

const handleViewScreenshot = (path: string) => {
  currentScreenshotPath.value = path
  screenshotDialogVisible.value = true
}

const handleViewError = (message: string) => {
  currentErrorMessage.value = message
  errorDialogVisible.value = true
}
</script>

<style scoped lang="scss">
.execution-detail-panel {
  .execution-summary {
    display: flex;
    flex-wrap: wrap;
    gap: 16px;
    padding: 16px;
    background: #f5f5f5;
    border-radius: 4px;
    margin-bottom: 20px;

    .summary-item {
      display: flex;
      align-items: center;
      gap: 8px;

      .label {
        color: #666;
        font-size: 14px;
      }

      .value {
        font-weight: 500;
        color: #333;

        &.success {
          color: #52c41a;
        }

        &.failed {
          color: #f5222d;
        }
      }
    }
  }

  .case-results {
    h3 {
      margin: 0 0 16px;
      font-size: 16px;
      font-weight: 500;
    }
  }

  .error-content {
    margin: 0;
    padding: 16px;
    background: #f5f5f5;
    border-radius: 4px;
    white-space: pre-wrap;
    word-break: break-all;
    font-family: 'Consolas', 'Monaco', monospace;
    font-size: 13px;
    line-height: 1.6;
  }
}
</style>
