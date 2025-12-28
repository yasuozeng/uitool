<!--
步骤列表组件
支持拖拽排序、选择、删除等操作
-->
<template>
  <div class="step-list">
    <!-- 步骤列表 -->
    <div class="list-container">
      <div
        v-for="(step, index) in steps"
        :key="step.id || index"
        class="step-item"
        :class="{ active: selectedIndex === index }"
        draggable="true"
        @click="handleSelect(index)"
        @dragstart="handleDragStart(index, $event)"
        @dragover="handleDragOver($event)"
        @drop="handleDrop(index, $event)"
      >
        <div class="step-order">{{ step.step_order }}</div>
        <div class="step-content">
          <div class="step-type">
            <el-tag :type="getActionTypeColor(step.action_type)" size="small">
              {{ getActionTypeName(step.action_type) }}
            </el-tag>
          </div>
          <div class="step-locator" :title="step.element_locator">
            {{ step.element_locator || '-' }}
          </div>
          <div v-if="step.description" class="step-desc" :title="step.description">
            {{ step.description }}
          </div>
        </div>
        <div class="step-actions">
          <el-button type="primary" size="small" text @click.stop="handleCopy(index)">
            <el-icon><CopyDocument /></el-icon>
          </el-button>
          <el-button type="danger" size="small" text @click.stop="handleDelete(index)">
            <el-icon><Delete /></el-icon>
          </el-button>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="steps.length === 0" class="empty-state">
        <el-empty description="暂无测试步骤" />
      </div>
    </div>

    <!-- 底部操作栏 -->
    <div class="list-actions">
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon>
        添加步骤
      </el-button>
      <el-button @click="handleClearAll" :disabled="steps.length === 0">
        <el-icon><Delete /></el-icon>
        清空全部
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { TestStep } from '@/store/modules/case'
import { getActionTypes } from '@/api/case'

// ========== Props & Emits ==========
interface Props {
  steps: TestStep[]
  selectedIndex?: number
}

interface Emits {
  (e: 'select', index: number): void
  (e: 'add', step: TestStep): void
  (e: 'update', index: number, step: TestStep): void
  (e: 'delete', index: number): void
  (e: 'reorder', fromIndex: number, toIndex: number): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// ========== 数据 ==========
const actionTypes = getActionTypes()
let dragIndex = ref<number>(-1)

// ========== 方法 ==========

// 获取操作类型名称
const getActionTypeName = (type: string) => {
  const action = actionTypes.find(a => a.value === type)
  return action?.label || type
}

// 获取操作类型对应的标签颜色
const getActionTypeColor = (type: string) => {
  const colorMap: Record<string, string> = {
    navigate: 'primary',
    click: 'success',
    input: 'warning',
    clear: '',
    wait: 'info',
    verify_text: 'success',
    verify_element: 'success',
    select: 'warning',
    hover: '',
    scroll: '',
    screenshot: 'danger'
  }
  return colorMap[type] || ''
}

// 选择步骤
const handleSelect = (index: number) => {
  emit('select', index)
}

// 添加步骤
const handleAdd = () => {
  const newStep: TestStep = {
    step_order: props.steps.length + 1,
    action_type: 'click',
    element_locator: '',
    locator_type: 'css',
    description: ''
  }
  emit('add', newStep)
}

// 复制步骤
const handleCopy = (index: number) => {
  const step = props.steps[index]
  const newStep: TestStep = {
    ...step,
    step_order: props.steps.length + 1
  }
  emit('add', newStep)
}

// 删除步骤
const handleDelete = (index: number) => {
  emit('delete', index)
}

// 清空全部
const handleClearAll = () => {
  // 逐个删除，从后往前
  for (let i = props.steps.length - 1; i >= 0; i--) {
    emit('delete', i)
  }
}

// ========== 拖拽相关 ==========

// 开始拖拽
const handleDragStart = (index: number, event: DragEvent) => {
  dragIndex.value = index
  if (event.dataTransfer) {
    event.dataTransfer.effectAllowed = 'move'
  }
}

// 拖拽经过
const handleDragOver = (event: DragEvent) => {
  event.preventDefault()
  if (event.dataTransfer) {
    event.dataTransfer.dropEffect = 'move'
  }
}

// 放下
const handleDrop = (toIndex: number, event: DragEvent) => {
  event.preventDefault()
  const fromIndex = dragIndex.value
  if (fromIndex !== -1 && fromIndex !== toIndex) {
    emit('reorder', fromIndex, toIndex)
  }
  dragIndex.value = -1
}
</script>

<style scoped lang="scss">
.step-list {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #fafafa; // 保持不变
  border-radius: 6px; // 从 4px 增加到 6px

  .list-container {
    flex: 1;
    overflow-y: auto;
    padding: 12px; // 从 8px 增加到 12px

    .step-item {
      display: flex;
      align-items: center;
      gap: 10px; // 从 8px 增加到 10px
      padding: 12px; // 从 10px 增加到 12px
      margin-bottom: 10px; // 从 8px 增加到 10px
      background: white;
      border: 1px solid #f0f0f0; // 更新边框色
      border-radius: 6px; // 从 4px 增加到 6px
      cursor: pointer;
      transition: all 0.2s; // 保持不变

      &:hover {
        border-color: #1677ff; // 更新为新的主色
        box-shadow: 0 2px 6px rgba(22, 119, 255, 0.12); // 更新阴影颜色
        transform: translateX(2px); // 添加轻微移动效果
      }

      &.active {
        border-color: #1677ff; // 更新为新的主色
        background: #e6f4ff; // 更新为新的浅蓝背景
        box-shadow: 0 2px 6px rgba(22, 119, 255, 0.15); // 添加阴影

        // 左侧指示器
        &::before {
          content: '';
          position: absolute;
          left: 0;
          top: 50%;
          transform: translateY(-50%);
          width: 3px;
          height: 60%;
          background: #1677ff;
          border-radius: 0 2px 2px 0;
        }
      }

      .step-order {
        flex-shrink: 0;
        width: 32px; // 从 28px 增加到 32px
        height: 32px; // 从 28px 增加到 32px
        display: flex;
        align-items: center;
        justify-content: center;
        background: #1677ff; // 更新为新的主色
        color: white;
        border-radius: 6px; // 从 50% 改为 6px 圆角
        font-size: 13px; // 从 12px 增加到 13px
        font-weight: 600; // 从 500 增加到 600
        box-shadow: 0 2px 4px rgba(22, 119, 255, 0.2); // 添加阴影
      }

      .step-content {
        flex: 1;
        min-width: 0;
        display: flex;
        align-items: center;
        gap: 10px; // 从 8px 增加到 10px
        overflow: hidden;

        .step-type {
          flex-shrink: 0;
        }

        .step-locator {
          flex: 1;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
          font-size: 14px; // 从 13px 增加到 14px
          color: #262626; // 更新为新的文本色
          font-weight: 500; // 添加字重
        }

        .step-desc {
          flex-shrink: 0;
          max-width: 160px; // 从 150px 增加到 160px
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
          font-size: 12px; // 保持不变
          color: #8c8c8c; // 更新为新的文本色
        }
      }

      .step-actions {
        flex-shrink: 0;
        display: flex;
        gap: 6px; // 从 4px 增加到 6px
        opacity: 0;
        transition: opacity 0.2s; // 保持不变

        .el-button {
          padding: 6px; // 从 4px 增加到 6px
          border-radius: 4px; // 添加圆角
          transition: all 0.2s; // 添加过渡效果

          &:hover {
            transform: scale(1.1); // 添加缩放效果
          }
        }
      }

      &:hover .step-actions {
        opacity: 1;
      }
    }

    .empty-state {
      display: flex;
      align-items: center;
      justify-content: center;
      height: 240px; // 从 200px 增加到 240px
      padding: 20px; // 添加内边距

      :deep(.el-empty) {
        --el-empty-description-color: #8c8c8c; // 更新空状态文本颜色
      }
    }
  }

  .list-actions {
    display: flex;
    gap: 16px; // 从 12px 增加到 16px
    padding: 14px 16px; // 增加内边距
    border-top: 1px solid #f0f0f0; // 更新边框色
    background: white;

    .el-button {
      flex: 1; // 按钮平分宽度
      height: 40px; // 增加按钮高度
      font-weight: 500; // 添加字重
      border-radius: 6px; // 添加圆角
      transition: all 0.2s; // 添加过渡效果

      &:hover:not(:disabled) {
        transform: translateY(-1px); // 添加轻微上移效果
      }
    }
  }
}

// 滚动条美化
.list-container::-webkit-scrollbar {
  width: 6px; // 减小滚动条宽度
}

.list-container::-webkit-scrollbar-track {
  background: transparent; // 透明轨道
}

.list-container::-webkit-scrollbar-thumb {
  background: #d9d9d9; // 更新滚动条颜色
  border-radius: 3px;

  &:hover {
    background: #bfbfbf; // 悬停时颜色加深
  }
}
</style>
