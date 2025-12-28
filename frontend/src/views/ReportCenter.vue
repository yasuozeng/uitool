<!--
报告中心页面
展示执行历史记录，支持查看详细报告和导出
-->
<template>
  <div class="report-center">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1>报告中心</h1>
      <el-button type="primary" @click="handleRefresh">
        <el-icon><Refresh /></el-icon>
        刷新
      </el-button>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-bar">
      <el-select v-model="filterStatus" placeholder="执行状态" clearable style="width: 150px">
        <el-option label="全部" value="" />
        <el-option label="执行中" value="running" />
        <el-option label="已完成" value="completed" />
        <el-option label="失败" value="failed" />
        <el-option label="已取消" value="cancelled" />
      </el-select>

      <el-select v-model="filterBrowser" placeholder="浏览器" clearable style="width: 150px">
        <el-option label="全部" value="" />
        <el-option label="Chrome" value="chrome" />
        <el-option label="Firefox" value="firefox" />
        <el-option label="Edge" value="edge" />
      </el-select>

      <el-date-picker
        v-model="filterDate"
        type="daterange"
        range-separator="至"
        start-placeholder="开始日期"
        end-placeholder="结束日期"
        style="width: 280px"
      />

      <el-button type="primary" @click="handleFilter">
        <el-icon><Search /></el-icon>
        筛选
      </el-button>
      <el-button @click="handleReset">
        <el-icon><RefreshLeft /></el-icon>
        重置
      </el-button>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-cards">
      <div class="stat-card">
        <div class="stat-icon total">
          <el-icon><DataAnalysis /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-label">总执行数</div>
          <div class="stat-value">{{ totalExecutions }}</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon success">
          <el-icon><CircleCheck /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-label">成功执行</div>
          <div class="stat-value">{{ completedExecutions }}</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon failed">
          <el-icon><CircleClose /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-label">失败执行</div>
          <div class="stat-value">{{ failedExecutions }}</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon rate">
          <el-icon><TrendCharts /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-label">平均通过率</div>
          <div class="stat-value">{{ averagePassRate }}%</div>
        </div>
      </div>
    </div>

    <!-- 执行历史表格 -->
    <div class="execution-table">
      <el-table v-loading="loading" :data="executions" stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="browser" label="浏览器" width="100">
          <template #default="{ row }">
            {{ getBrowserLabel(row.browser) }}
          </template>
        </el-table-column>
        <el-table-column label="执行结果" width="150">
          <template #default="{ row }">
            <span class="result-summary">
              通过: {{ row.passed_cases }} / 失败: {{ row.failed_cases }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="started_at" label="开始时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.started_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="duration" label="耗时" width="100">
          <template #default="{ row }">
            {{ formatDuration(row.duration) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" link @click="handleViewDetail(row.id)">
              <el-icon><View /></el-icon>
              详情
            </el-button>
            <el-button type="success" size="small" link @click="handleViewReport(row.id)">
              <el-icon><Document /></el-icon>
              报告
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 分页 -->
    <div class="pagination">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.page_size"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @current-change="loadExecutions"
        @size-change="handleSizeChange"
      />
    </div>

    <!-- 详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="执行详情"
      width="80%"
      top="5vh"
      destroy-on-close
    >
      <ExecutionDetailPanel
        v-if="currentExecution"
        :execution="currentExecution"
        @close="detailDialogVisible = false"
      />
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getExecutionList, getExecutionDetails } from '@/api/execution'
import type { Execution } from '@/api/execution'
import ExecutionDetailPanel from '@/components/ExecutionDetailPanel.vue'

const router = useRouter()

// ========== 数据 ==========
const loading = ref(false)
const executions = ref<Execution[]>([])
const filterStatus = ref('')
const filterBrowser = ref('')
const filterDate = ref<[Date, Date] | null>(null)
const detailDialogVisible = ref(false)
const currentExecution = ref<Execution | null>(null)

const pagination = ref({
  page: 1,
  page_size: 20,
  total: 0
})

// ========== 计算属性 ==========

// 统计数据
const totalExecutions = computed(() => pagination.value.total)
const completedExecutions = computed(() =>
  executions.value.filter(e => e.status === 'completed').length
)
const failedExecutions = computed(() =>
  executions.value.filter(e => e.status === 'failed').length
)
const averagePassRate = computed(() => {
  if (executions.value.length === 0) return 0
  const total = executions.value.reduce((sum, e) => sum + (e.total_cases || 0), 0)
  const passed = executions.value.reduce((sum, e) => sum + (e.passed_cases || 0), 0)
  return total > 0 ? Math.round((passed / total) * 100) : 0
})

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

// 加载执行列表
const loadExecutions = async () => {
  loading.value = true
  try {
    const response = await getExecutionList({
      page: pagination.value.page,
      page_size: pagination.value.page_size
    })
    executions.value = response.data || []
    pagination.value.total = response.total || 0
  } catch (error) {
    ElMessage.error('加载执行列表失败')
  } finally {
    loading.value = false
  }
}

// 筛选
const handleFilter = () => {
  pagination.value.page = 1
  loadExecutions()
}

// 重置筛选
const handleReset = () => {
  filterStatus.value = ''
  filterBrowser.value = ''
  filterDate.value = null
  pagination.value.page = 1
  loadExecutions()
}

// 刷新
const handleRefresh = () => {
  loadExecutions()
}

// 每页数量变化
const handleSizeChange = () => {
  pagination.value.page = 1
  loadExecutions()
}

// 查看详情
const handleViewDetail = async (id: number) => {
  try {
    // 获取执行基本信息
    const execution = executions.value.find(e => e.id === id)
    if (!execution) return

    // 获取详细结果
    const response = await getExecutionDetails(id)
    currentExecution.value = {
      ...execution,
      details: response.data
    }
    detailDialogVisible.value = true
  } catch (error) {
    ElMessage.error('获取执行详情失败')
  }
}

// 查看报告
const handleViewReport = (id: number) => {
  router.push(`/reports/${id}`)
}

// ========== 生命周期 ==========
onMounted(() => {
  loadExecutions()
})
</script>

<style scoped lang="scss">
.report-center {
  padding: 24px; // 从 20px 增加到 24px
  background: #f0f2f5; // 更新为新的背景色
  min-height: 100vh;

  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px; // 从 20px 增加到 24px
    padding: 18px 22px; // 增加内边距
    background: white;
    border-radius: 8px; // 从 4px 增加到 8px
    box-shadow: 0 1px 6px rgba(0, 0, 0, 0.04); // 添加阴影
    border: 1px solid #f0f0f0; // 添加边框

    h1 {
      margin: 0;
      font-size: 22px; // 从 24px 调整为 22px
      font-weight: 600; // 从 500 增加到 600
      color: #262626; // 更新为新的文本色
    }
  }

  .filter-bar {
    display: flex;
    gap: 16px; // 从 12px 增加到 16px
    margin-bottom: 24px; // 保持不变
    padding: 18px 22px; // 增加内边距
    background: white;
    border-radius: 8px; // 从 4px 增加到 8px
    border: 1px solid #f0f0f0; // 添加边框
    box-shadow: 0 1px 6px rgba(0, 0, 0, 0.04); // 添加阴影
    transition: box-shadow 0.2s; // 添加过渡效果

    &:hover {
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06); // 悬停时增强阴影
    }
  }

  .stats-cards {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 20px; // 从 16px 增加到 20px
    margin-bottom: 24px; // 从 20px 增加到 24px

    .stat-card {
      display: flex;
      align-items: center;
      padding: 20px; // 保持不变
      background: white;
      border-radius: 8px; // 从 4px 增加到 8px
      border: 1px solid #f0f0f0; // 添加边框
      box-shadow: 0 1px 6px rgba(0, 0, 0, 0.04); // 添加阴影
      transition: all 0.2s; // 添加过渡效果

      &:hover {
        transform: translateY(-2px); // 轻微上移效果
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08); // 悬停时增强阴影
      }

      .stat-icon {
        width: 56px; // 从 60px 调整为 56px
        height: 56px; // 从 60px 调整为 56px
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 8px;
        font-size: 24px; // 从 28px 调整为 24px

        &.total {
          background: #e6f4ff; // 更新为新的浅蓝背景
          color: #1677ff; // 更新为新的主色
        }

        &.success {
          background: #f6ffed; // 保持不变
          color: #52c41a; // 保持不变
        }

        &.failed {
          background: #fff1f0; // 保持不变
          color: #ff4d4f; // 更新为新的危险色
        }

        &.rate {
          background: #fff7e6; // 保持不变
          color: #faad14; // 保持不变
        }
      }

      .stat-content {
        margin-left: 16px; // 保持不变

        .stat-label {
          font-size: 14px; // 保持不变
          color: #595959; // 更新为新的文本色
          margin-bottom: 6px; // 从 4px 增加到 6px
          font-weight: 500; // 添加字重
        }

        .stat-value {
          font-size: 28px; // 从 24px 增加到 28px
          font-weight: 600; // 从 500 增加到 600
          color: #262626; // 更新为新的文本色
        }
      }
    }
  }

  .execution-table {
    background: white;
    border-radius: 8px; // 从 4px 增加到 8px
    padding: 20px; // 从 16px 增加到 20px
    border: 1px solid #f0f0f0; // 添加边框
    box-shadow: 0 1px 6px rgba(0, 0, 0, 0.04); // 添加阴影

    .result-summary {
      font-size: 14px; // 从 13px 增加到 14px
      color: #595959; // 更新为新的文本色
      font-weight: 500; // 添加字重
    }
  }

  .pagination {
    display: flex;
    justify-content: center;
    margin-top: 24px; // 从 20px 增加到 24px
    padding: 18px 22px; // 增加内边距
    background: white;
    border-radius: 8px; // 从 4px 增加到 8px
    border: 1px solid #f0f0f0; // 添加边框
    box-shadow: 0 1px 6px rgba(0, 0, 0, 0.04); // 添加阴影
  }
}

// 响应式调整
@media (max-width: 1400px) {
  .report-center {
    .stats-cards {
      grid-template-columns: repeat(2, 1fr); // 从 4 列调整为 2 列
    }
  }
}

@media (max-width: 768px) {
  .report-center {
    padding: 16px; // 减小内边距

    .stats-cards {
      grid-template-columns: 1fr; // 调整为 1 列
      gap: 12px; // 减小间距
    }

    .filter-bar {
      flex-direction: column; // 垂直排列
      gap: 12px; // 减小间距

      .el-select,
      .el-date-picker {
        width: 100% !important; // 全宽
      }
    }
  }
}
</style>
