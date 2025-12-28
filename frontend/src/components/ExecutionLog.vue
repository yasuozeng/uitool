<!--
实时日志组件
展示执行过程中的实时日志流
-->
<template>
  <div class="execution-log">
    <div class="log-header">
      <div class="header-left">
        <el-icon><Document /></el-icon>
        <span>执行日志</span>
      </div>
      <div class="header-right">
        <el-tag v-if="logCount > 0" type="info" size="small">
          {{ logCount }} 条
        </el-tag>
        <el-button size="small" @click="handleClear">
          <el-icon><Delete /></el-icon>
          清空
        </el-button>
      </div>
    </div>

    <div ref="logContainer" class="log-container">
      <div
        v-for="(log, index) in logs"
        :key="index"
        class="log-item"
        :class="`log-${log.level}`"
      >
        <span class="log-time">{{ formatTime(log.timestamp) }}</span>
        <span v-if="log.case_name" class="log-case">[{{ log.case_name }}]</span>
        <span v-if="log.step_order !== undefined" class="log-step">步骤 {{ log.step_order }}:</span>
        <span class="log-message">{{ log.message }}</span>
        <el-button
          v-if="log.screenshot_path"
          type="primary"
          size="small"
          text
          @click="handleViewScreenshot(log.screenshot_path)"
        >
          <el-icon><Picture /></el-icon>
          查看截图
        </el-button>
      </div>

      <div v-if="logs.length === 0" class="log-empty">
        <el-empty description="暂无日志" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import type { ExecutionLog } from '@/store/modules/execution'

// ========== Props & Emits ==========
interface Props {
  logs: ExecutionLog[]
}

interface Emits {
  (e: 'viewScreenshot', path: string): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// ========== 数据 ==========
const logContainer = ref<HTMLElement>()

// ========== 计算属性 ==========
const logCount = computed(() => props.logs.length)

// ========== 方法 ==========

// 格式化时间
const formatTime = (timestamp: string) => {
  const date = new Date(timestamp)
  return date.toLocaleTimeString('zh-CN', { hour12: false })
}

// 清空日志
const handleClear = () => {
  emit('clear')
}

// 查看截图
const handleViewScreenshot = (path: string) => {
  emit('viewScreenshot', path)
}

// ========== 监听 ==========

// 自动滚动到底部
watch(
  () => props.logs.length,
  () => {
    nextTick(() => {
      if (logContainer.value) {
        logContainer.value.scrollTop = logContainer.value.scrollHeight
      }
    })
  }
)
</script>

<style scoped lang="scss">
.execution-log {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #1e1e1e;
  border-radius: 4px;
  overflow: hidden;

  .log-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 16px;
    background: #2d2d2d;
    border-bottom: 1px solid #3e3e3e;
    color: #cccccc;

    .header-left {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 14px;
    }

    .header-right {
      display: flex;
      align-items: center;
      gap: 8px;
    }
  }

  .log-container {
    flex: 1;
    overflow-y: auto;
    padding: 8px;
    font-family: 'Consolas', 'Monaco', monospace;
    font-size: 13px;
    line-height: 1.8;

    .log-item {
      display: flex;
      align-items: center;
      flex-wrap: wrap;
      gap: 8px;
      padding: 4px 8px;
      border-radius: 2px;

      &:hover {
        background: rgba(255, 255, 255, 0.05);
      }

      .log-time {
        color: #858585;
        flex-shrink: 0;
      }

      .log-case {
        color: #4ec9b0;
        flex-shrink: 0;
      }

      .log-step {
        color: #dcdcaa;
        flex-shrink: 0;
      }

      .log-message {
        color: #cccccc;
      }

      &.log-info {
        .log-message {
          color: #cccccc;
        }
      }

      &.log-success {
        .log-message {
          color: #4ec9b0;
        }
      }

      &.log-error {
        .log-message {
          color: #f48771;
        }
      }

      &.log-warning {
        .log-message {
          color: #dcdcaa;
        }
      }

      .el-button {
        margin-left: auto;
      }
    }

    .log-empty {
      display: flex;
      align-items: center;
      justify-content: center;
      height: 200px;

      :deep(.el-empty) {
        --el-empty-description-color: #858585;
      }
    }
  }

  // 滚动条样式
  .log-container::-webkit-scrollbar {
    width: 8px;
  }

  .log-container::-webkit-scrollbar-track {
    background: #2d2d2d;
  }

  .log-container::-webkit-scrollbar-thumb {
    background: #424242;
    border-radius: 4px;

    &:hover {
      background: #4e4e4e;
    }
  }
}
</style>
