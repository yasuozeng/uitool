<!--
执行控制台页面
提供用例选择、浏览器配置和执行控制功能
-->
<template>
  <div class="execution-console">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1>执行控制台</h1>
    </div>

    <div class="console-content">
      <!-- 左侧：配置面板 -->
      <div class="config-panel">
        <div class="panel-section">
          <h3>浏览器配置</h3>
          <el-form label-width="90px" label-position="left">
            <el-form-item label="执行引擎">
              <el-select v-model="config.engine" style="width: 100%">
                <el-option
                  v-for="engine in engineOptions"
                  :key="engine.value"
                  :label="engine.label"
                  :value="engine.value"
                />
              </el-select>
            </el-form-item>

            <el-form-item label="浏览器">
              <el-select v-model="config.browser" style="width: 100%">
                <el-option
                  v-for="browser in browserOptions"
                  :key="browser.value"
                  :label="browser.label"
                  :value="browser.value"
                />
              </el-select>
            </el-form-item>

            <el-form-item label="无头模式">
              <el-switch v-model="config.headless" />
              <span class="hint">{{ config.headless ? '后台运行' : '显示浏览器窗口' }}</span>
            </el-form-item>

            <el-form-item label="窗口大小">
              <el-select v-model="config.window_size" style="width: 100%">
                <el-option
                  v-for="size in windowSizes"
                  :key="size.value"
                  :label="size.label"
                  :value="size.value"
                />
              </el-select>
            </el-form-item>
          </el-form>
        </div>

        <div class="panel-section">
          <h3>用例选择</h3>
          <el-input
            v-model="caseSearch"
            placeholder="搜索用例"
            clearable
            class="search-input"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>

          <div class="case-list">
            <div
              v-for="c in filteredCases"
              :key="c.id"
              class="case-item"
              :class="{ selected: selectedCaseIds.includes(c.id) }"
              @click="toggleCaseSelection(c.id)"
            >
              <div class="case-info">
                <div class="case-name">{{ c.name }}</div>
                <div class="case-meta">
                  <el-tag :type="getPriorityType(c.priority)" size="small">
                    {{ c.priority }}
                  </el-tag>
                  <span class="step-count">{{ c.step_count }} 步</span>
                </div>
              </div>
              <el-checkbox :model-value="selectedCaseIds.includes(c.id)" />
            </div>

            <div v-if="filteredCases.length === 0" class="empty-cases">
              <el-empty description="暂无可用用例" />
            </div>
          </div>

          <div class="selection-summary">
            已选择 {{ selectedCaseIds.length }} 个用例
          </div>
        </div>

        <div class="panel-section action-section">
          <el-button
            type="primary"
            size="large"
            :disabled="selectedCaseIds.length === 0 || isExecuting"
            :loading="isExecuting"
            @click="handleStartExecution"
          >
            <el-icon><VideoPlay /></el-icon>
            {{ isExecuting ? '执行中...' : '开始执行' }}
          </el-button>
          <el-button
            v-if="isExecuting"
            type="danger"
            size="large"
            @click="handleStopExecution"
          >
            <el-icon><VideoPause /></el-icon>
            停止执行
          </el-button>
        </div>
      </div>

      <!-- 右侧：执行结果 -->
      <div class="result-panel">
        <!-- 执行进度 -->
        <div v-if="currentExecution" class="progress-section">
          <div class="progress-info">
            <div class="progress-stats">
              <el-statistic title="进度" :value="progress">
                <template #suffix>%</template>
              </el-statistic>
              <el-statistic title="通过" :value="currentExecution.passed_cases">
                <template #suffix>/ {{ currentExecution.total_cases }}</template>
              </el-statistic>
              <el-statistic title="失败" :value="currentExecution.failed_cases" />
              <el-statistic title="通过率" :value="passRate">
                <template #suffix>%</template>
              </el-statistic>
            </div>
          </div>
          <el-progress
            :percentage="progress"
            :status="progressStatus"
            :stroke-width="12"
          />
        </div>

        <!-- 执行结果列表 -->
        <div class="results-section">
          <h3>执行结果</h3>
          <div class="results-list">
            <div
              v-for="detail in executionDetails"
              :key="detail.id"
              class="result-item"
              :class="`result-${detail.status}`"
            >
              <div class="result-header">
                <el-icon v-if="detail.status === 'success' || detail.status === 'completed'" class="success-icon"><CircleCheck /></el-icon>
                <el-icon v-else class="error-icon"><CircleClose /></el-icon>
                <span class="case-name">{{ detail.case_name }}</span>
                <el-tag :type="detail.status === 'success' || detail.status === 'completed' ? 'success' : 'danger'" size="small">
                  {{ detail.status === 'success' || detail.status === 'completed' ? '通过' : '失败' }}
                </el-tag>
              </div>
              <div v-if="detail.error_message" class="error-message">
                {{ detail.error_message }}
              </div>
              <div v-if="detail.screenshot_path" class="screenshot-action">
                <el-button type="primary" size="small" @click="handleViewScreenshot(detail.screenshot_path!)">
                  <el-icon><Picture /></el-icon>
                  查看截图
                </el-button>
              </div>
            </div>

            <div v-if="executionDetails.length === 0 && !isExecuting" class="empty-results">
              <el-empty description="暂无执行结果" />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 截图查看对话框 -->
    <el-dialog
      v-model="screenshotDialogVisible"
      title="查看截图"
      width="80%"
      top="5vh"
      destroy-on-close
    >
      <ScreenshotViewer
        :screenshot-path="currentScreenshotPath"
        @close="screenshotDialogVisible = false"
      />
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useCaseStore } from '@/store/modules/case'
import { getCases, getPriorities } from '@/api/case'
import { createExecution, startExecution, getExecution, getExecutionDetails, getBrowserOptions, getWindowSizeOptions } from '@/api/execution'
import type { Execution } from '@/api/execution'
import ScreenshotViewer from '@/components/ScreenshotViewer.vue'

const route = useRoute()
const caseStore = useCaseStore()

// ========== 数据 ==========
const caseSearch = ref('')
const selectedCaseIds = ref<number[]>([])
const screenshotDialogVisible = ref(false)
const currentScreenshotPath = ref('')

// 浏览器配置
const config = ref({
  engine: 'playwright',  // 执行引擎
  browser: 'chrome',
  headless: false,
  window_size: '1920x1080'
})

// 选项
const engineOptions = [
  { value: 'playwright', label: 'Playwright' }
]
const browserOptions = getBrowserOptions()
const windowSizes = getWindowSizeOptions()
const priorities = getPriorities()

// ========== 计算属性 ==========

// 可用用例列表
const availableCases = computed(() => caseStore.cases)

// 过滤后的用例
const filteredCases = computed(() => {
  if (!caseSearch.value) return availableCases.value
  const search = caseSearch.value.toLowerCase()
  return availableCases.value.filter(c =>
    c.name.toLowerCase().includes(search) ||
    (c.tags && c.tags.toLowerCase().includes(search))
  )
})

// 当前执行
const currentExecution = ref<Execution | null>(null)
const executionDetails = computed(() => currentExecution.value?.details || [])
const isExecuting = computed(() => currentExecution.value?.status === 'running')

// 进度
const progress = computed(() => {
  if (!currentExecution.value) return 0
  const { total_count = 0, success_count = 0, fail_count = 0 } = currentExecution.value
  if (total_count === 0) return 0
  return Math.round(((success_count + fail_count) / total_count) * 100)
})

const passRate = computed(() => {
  if (!currentExecution.value) return 0
  const { total_count = 0, success_count = 0 } = currentExecution.value
  if (total_count === 0) return 0
  return Math.round((success_count / total_count) * 100)
})

const progressStatus = computed(() => {
  const p = progress.value
  if (p === 100) return 'success'
  if (currentExecution.value?.fail_count! > 0) return 'exception'
  return undefined
})

// ========== 方法 ==========

// 获取优先级类型
const getPriorityType = (priority: string) => {
  const p = priorities.find(item => item.value === priority)
  return p?.type || ''
}

// 切换用例选择
const toggleCaseSelection = (id: number) => {
  const index = selectedCaseIds.value.indexOf(id)
  if (index === -1) {
    selectedCaseIds.value.push(id)
  } else {
    selectedCaseIds.value.splice(index, 1)
  }
}

// 开始执行
const handleStartExecution = async () => {
  if (selectedCaseIds.value.length === 0) {
    ElMessage.warning('请先选择要执行的用例')
    return
  }

  try {
    // 根据选中的用例数量决定执行类型
    const executionType = selectedCaseIds.value.length === 1 ? 'single' : 'batch'

    // 创建执行任务
    const createResponse = await createExecution({
      execution_type: executionType,
      case_ids: selectedCaseIds.value,
      browser: config.value.browser as any,
      headless: config.value.headless,
      window_size: config.value.window_size
    })

    const execution = createResponse.data
    currentExecution.value = execution

    // 启动执行任务
    await startExecution(execution.id)

    // 轮询获取执行状态
    startPolling(execution.id)

    ElMessage.success('执行任务已启动')
  } catch (error) {
    console.error('启动执行任务失败:', error)
    ElMessage.error('启动执行任务失败')
  }
}

// 停止执行
const handleStopExecution = async () => {
  try {
    await ElMessageBox.confirm('确定要停止当前执行吗？', '确认停止', {
      type: 'warning'
    })
    currentExecution.value = null
    ElMessage.info('执行已停止')
  } catch {
    // 用户取消
  }
}

// 轮询获取执行状态
let pollTimer: ReturnType<typeof setInterval> | null = null
const startPolling = (executionId: number) => {
  pollTimer = setInterval(async () => {
    try {
      const response = await getExecution(executionId)
      currentExecution.value = response.data

      // 如果执行完成，停止轮询并加载详情
      if (['completed', 'failed', 'cancelled'].includes(response.data.status)) {
        stopPolling()
        await loadExecutionDetails(executionId)
      }
    } catch (error) {
      console.error('获取执行状态失败:', error)
    }
  }, 2000)
}

const stopPolling = () => {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

// 加载执行详情
const loadExecutionDetails = async (executionId: number) => {
  try {
    const response = await getExecutionDetails(executionId)
    if (currentExecution.value) {
      currentExecution.value.details = response.data
    }
  } catch (error) {
    console.error('获取执行详情失败:', error)
  }
}

// 查看截图
const handleViewScreenshot = (path: string) => {
  currentScreenshotPath.value = path
  screenshotDialogVisible.value = true
}

// 加载用例列表
const loadCases = async () => {
  try {
    const response = await getCases({ page: 1, page_size: 100 })
    caseStore.setCases(response.data)
    caseStore.setPagination({
      total: response.total,
      pages: response.pages
    })
  } catch (error) {
    ElMessage.error('加载用例列表失败')
  }
}

// ========== 生命周期 ==========
onMounted(() => {
  loadCases()

  // 从 query 参数获取预选的用例
  const caseIds = route.query.case_ids as string
  if (caseIds) {
    selectedCaseIds.value = caseIds.split(',').map(id => parseInt(id))
  }
})

onUnmounted(() => {
  stopPolling()
})</script>

<style scoped lang="scss">
.execution-console {
  padding: 20px;
  background: #f5f5f5;
  min-height: 100vh;

  .page-header {
    margin-bottom: 20px;

    h1 {
      margin: 0;
      font-size: 24px;
      font-weight: 500;
    }
  }

  .console-content {
    display: flex;
    gap: 20px;
    height: calc(100vh - 120px);

    .config-panel {
      width: 350px;
      display: flex;
      flex-direction: column;
      gap: 16px;

      .panel-section {
        background: white;
        padding: 16px;
        border-radius: 4px;

        h3 {
          margin: 0 0 16px;
          font-size: 16px;
          font-weight: 500;
        }

        &.action-section {
          display: flex;
          flex-direction: column;
          gap: 12px;

          .el-button {
            width: 100%;
          }
        }
      }

      .hint {
        margin-left: 12px;
        font-size: 12px;
        color: #999;
      }

      .search-input {
        margin-bottom: 12px;
      }

      .case-list {
        max-height: 300px;
        overflow-y: auto;
        border: 1px solid #e8e8e8;
        border-radius: 4px;

        .case-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 10px 12px;
          border-bottom: 1px solid #e8e8e8;
          cursor: pointer;
          transition: background 0.2s;

          &:hover {
            background: #f5f5f5;
          }

          &.selected {
            background: #e6f7ff;
          }

          .case-info {
            flex: 1;
            min-width: 0;

            .case-name {
              font-size: 14px;
              margin-bottom: 4px;
              overflow: hidden;
              text-overflow: ellipsis;
              white-space: nowrap;
            }

            .case-meta {
              display: flex;
              align-items: center;
              gap: 8px;
              font-size: 12px;

              .step-count {
                color: #999;
              }
            }
          }
        }

        .empty-cases {
          padding: 20px;
        }
      }

      .selection-summary {
        margin-top: 12px;
        text-align: center;
        font-size: 14px;
        color: #1890ff;
      }
    }

    .result-panel {
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 16px;
      min-width: 0;

      .progress-section {
        background: white;
        padding: 20px;
        border-radius: 4px;

        .progress-info {
          margin-bottom: 16px;

          .progress-stats {
            display: flex;
            justify-content: space-around;

            :deep(.el-statistic) {
              .el-statistic__head {
                font-size: 13px;
                color: #666;
              }

              .el-statistic__content {
                font-size: 24px;
                font-weight: 500;
              }
            }
          }
        }
      }

      .results-section {
        flex: 1;
        background: white;
        border-radius: 4px;
        padding: 16px;
        display: flex;
        flex-direction: column;
        overflow: hidden;

        h3 {
          margin: 0 0 16px;
          font-size: 16px;
          font-weight: 500;
        }

        .results-list {
          flex: 1;
          overflow-y: auto;

          .result-item {
            padding: 12px;
            margin-bottom: 12px;
            border: 1px solid #e8e8e8;
            border-radius: 4px;
            background: #fafafa;

            &.result-completed {
              border-left: 4px solid #67c23a;
            }

            &.result-failed {
              border-left: 4px solid #f56c6c;
            }

            .result-header {
              display: flex;
              align-items: center;
              gap: 8px;

              .success-icon {
                color: #67c23a;
              }

              .error-icon {
                color: #f56c6c;
              }

              .case-name {
                flex: 1;
                font-weight: 500;
              }
            }

            .error-message {
              margin-top: 8px;
              padding: 8px;
              background: #fef0f0;
              border-radius: 4px;
              color: #f56c6c;
              font-size: 13px;
            }

            .screenshot-action {
              margin-top: 8px;
            }
          }

          .empty-results {
            display: flex;
            align-items: center;
            justify-content: center;
            height: 200px;
          }
        }
      }
    }
  }
}
</style>
