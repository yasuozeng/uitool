<!--
截图查看器组件
用于展示执行失败时的截图
-->
<template>
  <div class="screenshot-viewer">
    <div v-if="screenshotUrl" class="screenshot-container">
      <div class="screenshot-toolbar">
        <span class="filename">{{ fileName }}</span>
        <div class="toolbar-actions">
          <el-button size="small" @click="handleDownload">
            <el-icon><Download /></el-icon>
            下载
          </el-button>
          <el-button size="small" @click="handleOpenNew">
            <el-icon><View /></el-icon>
            新窗口打开
          </el-button>
          <el-button size="small" @click="handleClose">
            <el-icon><Close /></el-icon>
            关闭
          </el-button>
        </div>
      </div>
      <div class="screenshot-content">
        <img :src="screenshotUrl" :alt="fileName" @load="handleLoad" @error="handleError" />
      </div>
    </div>
    <div v-else class="no-screenshot">
      <el-empty description="暂无截图" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

// ========== Props & Emits ==========
interface Props {
  screenshotPath?: string
}

interface Emits {
  (e: 'close'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// ========== 数据 ==========
const loading = ref(true)
const error = ref(false)

// ========== 计算属性 ==========

// 截图 URL
const screenshotUrl = computed(() => {
  if (!props.screenshotPath) return ''
  // 将文件路径转换为 URL（需要根据实际后端配置调整）
  return `/api/screenshots/${props.screenshotPath}`
})

// 文件名
const fileName = computed(() => {
  if (!props.screenshotPath) return ''
  const parts = props.screenshotPath.split(/[/\\]/)
  return parts[parts.length - 1] || props.screenshotPath
})

// ========== 方法 ==========

// 图片加载完成
const handleLoad = () => {
  loading.value = false
  error.value = false
}

// 图片加载失败
const handleError = () => {
  loading.value = false
  error.value = true
}

// 下载截图
const handleDownload = () => {
  const link = document.createElement('a')
  link.href = screenshotUrl.value
  link.download = fileName.value
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

// 新窗口打开
const handleOpenNew = () => {
  window.open(screenshotUrl.value, '_blank')
}

// 关闭
const handleClose = () => {
  emit('close')
}
</script>

<style scoped lang="scss">
.screenshot-viewer {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #f5f5f5;
  border-radius: 4px;
  overflow: hidden;

  .screenshot-container {
    display: flex;
    flex-direction: column;
    height: 100%;

    .screenshot-toolbar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 10px 16px;
      background: white;
      border-bottom: 1px solid #e8e8e8;

      .filename {
        font-weight: 500;
        color: #333;
      }

      .toolbar-actions {
        display: flex;
        gap: 8px;
      }
    }

    .screenshot-content {
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 20px;
      overflow: auto;

      img {
        max-width: 100%;
        max-height: 100%;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        border-radius: 4px;
      }
    }
  }

  .no-screenshot {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    background: white;
  }
}
</style>
