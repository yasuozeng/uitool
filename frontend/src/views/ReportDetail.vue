<!--
报告详情页面
展示单个执行任务的HTML测试报告
-->
<template>
  <div class="report-detail">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <el-button @click="handleBack" circle>
          <el-icon><ArrowLeft /></el-icon>
        </el-button>
        <h1>测试报告 #{{ executionId }}</h1>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="handleDownload">
          <el-icon><Download /></el-icon>
          下载报告
        </el-button>
        <el-button @click="handleRefresh">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>

    <!-- 报告内容区域 -->
    <div v-loading="loading" class="report-content">
      <!-- 报告头部信息卡片 -->
      <el-card v-if="execution" class="info-card" shadow="never">
        <div class="report-header">
          <div class="header-item">
            <span class="label">执行状态</span>
            <el-tag :type="getStatusType(execution.status)" size="large">
              {{ getStatusLabel(execution.status) }}
            </el-tag>
          </div>
          <div class="header-item">
            <span class="label">执行结果</span>
            <span class="result-text">
              通过: {{ execution.passed_cases }} / 失败: {{ execution.failed_cases }}
            </span>
          </div>
          <div class="header-item">
            <span class="label">通过率</span>
            <span class="rate-text" :class="getRateClass(execution.pass_rate)">
              {{ execution.pass_rate }}%
            </span>
          </div>
          <div class="header-item">
            <span class="label">浏览器</span>
            <span>{{ getBrowserLabel(execution.browser) }}</span>
          </div>
          <div class="header-item">
            <span class="label">执行时间</span>
            <span>{{ formatDate(execution.started_at) }}</span>
          </div>
          <div class="header-item">
            <span class="label">耗时</span>
            <span>{{ formatDuration(execution.duration) }}</span>
          </div>
        </div>
      </el-card>

      <!-- HTML报告容器 -->
      <el-card v-if="htmlReport" class="html-report-card" shadow="never">
        <template #header>
          <div class="card-header">
            <span>执行详情</span>
          </div>
        </template>
        <!-- 使用iframe渲染HTML报告 -->
        <div class="html-container" v-html="htmlReport"></div>
      </el-card>

      <!-- 无报告时的提示 -->
      <el-card v-else-if="!loading" class="empty-card" shadow="never">
        <el-empty description="暂无报告数据" />
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getExecution, getExecutionDetails, generateHtmlReport } from '@/api/execution'
import type { Execution } from '@/api/execution'

const route = useRoute()
const router = useRouter()

// 从路由参数获取执行ID
const executionId = computed(() => Number(route.params.id))

// 响应式数据
const loading = ref(false)
const execution = ref<Execution | null>(null)
const htmlReport = ref('')

// ========== 方法 ==========

// 获取状态对应的标签类型
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

// 获取状态标签
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

// 获取浏览器标签
const getBrowserLabel = (browser: string) => {
  const map: Record<string, string> = {
    chrome: 'Chrome',
    firefox: 'Firefox',
    edge: 'Edge'
  }
  return map[browser] || browser
}

// 获取通过率对应的样式类
const getRateClass = (rate: number) => {
  if (rate >= 80) return 'rate-high'
  if (rate >= 50) return 'rate-medium'
  return 'rate-low'
}

// 格式化日期
const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

// 格式化耗时
const formatDuration = (seconds?: number) => {
  if (!seconds) return '-'
  if (seconds < 60) return `${seconds}秒`
  const minutes = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${minutes}分${secs}秒`
}

// 加载执行详情和生成报告
const loadReport = async () => {
  loading.value = true
  try {
    // 并行获取执行信息和详情
    const [execResponse, detailsResponse] = await Promise.all([
      getExecution(executionId.value),
      getExecutionDetails(executionId.value)
    ])

    execution.value = {
      ...execResponse.data,
      details: detailsResponse.data
    }

    // 生成HTML报告
    await generateReport()
  } catch (error) {
    ElMessage.error('获取报告数据失败')
    console.error('加载报告失败:', error)
  } finally {
    loading.value = false
  }
}

// 生成HTML报告
const generateReport = async () => {
  try {
    const response = await generateHtmlReport(executionId.value)
    htmlReport.value = response.data || ''
  } catch (error) {
    console.error('生成HTML报告失败:', error)
    // 如果生成失败，使用内置模板生成简单报告
    htmlReport.value = generateSimpleReport()
  }
}

// 生成简单的HTML报告（备用方案）
const generateSimpleReport = () => {
  if (!execution.value) return ''

  const exec = execution.value
  const details = exec.details || []

  let html = `
    <div class="simple-report">
      <h2>执行详情</h2>
      <table class="report-table">
        <thead>
          <tr>
            <th>用例名称</th>
            <th>状态</th>
            <th>开始时间</th>
            <th>结束时间</th>
            <th>耗时</th>
          </tr>
        </thead>
        <tbody>
  `

  details.forEach((detail: any) => {
    const statusClass = detail.status === 'success' ? 'success' : 'failed'
    const statusLabel = detail.status === 'success' ? '成功' : '失败'

    html += `
      <tr class="${statusClass}">
        <td>${detail.case_name || '-'}</td>
        <td><span class="status-badge ${statusClass}">${statusLabel}</span></td>
        <td>${formatDate(detail.start_time)}</td>
        <td>${formatDate(detail.end_time || '-')}</td>
        <td>${detail.duration ? detail.duration + 'ms' : '-'}</td>
      </tr>
    `

    // 如果有步骤日志，显示步骤信息
    if (detail.step_logs && detail.step_logs.length > 0) {
      html += `
        <tr class="step-logs">
          <td colspan="5">
            <div class="steps-container">
              <h4>执行步骤</h4>
      `

      detail.step_logs.forEach((step: any, index: number) => {
        const stepStatusClass = step.success ? 'success' : 'failed'
        html += `
          <div class="step-item ${stepStatusClass}">
            <strong>步骤${index + 1}:</strong> ${step.action_type || '-'}
            ${step.element_locator ? `- ${step.element_locator}` : ''}
            <span class="step-status">${step.success ? '✓' : '✗'}</span>
          </div>
        `
      })

      html += `
            </div>
          </td>
        </tr>
      `
    }
  })

  html += `
        </tbody>
      </table>
    </div>
  `

  return html
}

// 下载报告
const handleDownload = () => {
  if (!htmlReport.value) {
    ElMessage.warning('暂无报告可下载')
    return
  }

  // 创建完整的HTML文档
  const fullHtml = `
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>测试报告 #${executionId.value}</title>
      <style>
        body {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
          margin: 0;
          padding: 20px;
          background: #f5f5f5;
        }
        .simple-report {
          background: white;
          padding: 20px;
          border-radius: 8px;
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .simple-report h2 {
          margin-top: 0;
          color: #333;
          border-bottom: 2px solid #1890ff;
          padding-bottom: 10px;
        }
        .report-table {
          width: 100%;
          border-collapse: collapse;
          margin-top: 20px;
        }
        .report-table th,
        .report-table td {
          padding: 12px;
          text-align: left;
          border-bottom: 1px solid #e8e8e8;
        }
        .report-table th {
          background: #fafafa;
          font-weight: 600;
          color: #333;
        }
        .report-table tr.success {
          background: #f6ffed;
        }
        .report-table tr.failed {
          background: #fff1f0;
        }
        .status-badge {
          display: inline-block;
          padding: 4px 12px;
          border-radius: 4px;
          font-size: 12px;
          font-weight: 500;
        }
        .status-badge.success {
          background: #52c41a;
          color: white;
        }
        .status-badge.failed {
          background: #f5222d;
          color: white;
        }
        .steps-container {
          margin: 10px 0;
          padding: 10px;
          background: #fafafa;
          border-radius: 4px;
        }
        .steps-container h4 {
          margin: 0 0 10px 0;
          color: #666;
        }
        .step-item {
          padding: 8px;
          margin: 4px 0;
          border-radius: 4px;
          background: white;
        }
        .step-item.success {
          border-left: 3px solid #52c41a;
        }
        .step-item.failed {
          border-left: 3px solid #f5222d;
        }
        .step-status {
          float: right;
          font-weight: bold;
        }
      </style>
    </head>
    <body>
      ${htmlReport.value}
    </body>
    </html>
  `

  // 创建下载链接
  const blob = new Blob([fullHtml], { type: 'text/html;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `test-report-${executionId.value}-${Date.now()}.html`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)

  ElMessage.success('报告下载成功')
}

// 刷新报告
const handleRefresh = () => {
  loadReport()
}

// 返回上一页
const handleBack = () => {
  router.back()
}

// ========== 生命周期 ==========
onMounted(() => {
  loadReport()
})
</script>

<style scoped lang="scss">
.report-detail {
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

    .header-actions {
      display: flex;
      gap: 12px;
    }
  }

  .info-card {
    margin-bottom: 20px;

    .report-header {
      display: flex;
      flex-wrap: wrap;
      gap: 32px;

      .header-item {
        display: flex;
        flex-direction: column;
        gap: 8px;

        .label {
          font-size: 12px;
          color: #999;
        }

        .result-text {
          font-size: 14px;
          color: #333;
          font-weight: 500;
        }

        .rate-text {
          font-size: 18px;
          font-weight: 600;

          &.rate-high {
            color: #52c41a;
          }

          &.rate-medium {
            color: #fa8c16;
          }

          &.rate-low {
            color: #f5222d;
          }
        }
      }
    }
  }

  .html-report-card {
    .card-header {
      font-weight: 600;
    }

    .html-container {
      // HTML报告的样式由报告内容本身提供
      // 这里只做基本的容器样式
      min-height: 400px;

      :deep(table) {
        width: 100%;
        border-collapse: collapse;

        th, td {
          padding: 8px 12px;
          text-align: left;
          border-bottom: 1px solid #e8e8e8;
        }

        th {
          background: #fafafa;
          font-weight: 600;
        }
      }
    }
  }

  .empty-card {
    text-align: center;
    padding: 60px 20px;
  }
}
</style>
