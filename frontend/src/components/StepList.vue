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
  background: #fafafa;
  border-radius: 4px;

  .list-container {
    flex: 1;
    overflow-y: auto;
    padding: 8px;

    .step-item {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 10px;
      margin-bottom: 8px;
      background: white;
      border: 1px solid #e8e8e8;
      border-radius: 4px;
      cursor: pointer;
      transition: all 0.2s;

      &:hover {
        border-color: #1890ff;
        box-shadow: 0 2px 4px rgba(24, 144, 255, 0.1);
      }

      &.active {
        border-color: #1890ff;
        background: #e6f7ff;
      }

      .step-order {
        flex-shrink: 0;
        width: 28px;
        height: 28px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: #1890ff;
        color: white;
        border-radius: 50%;
        font-size: 12px;
        font-weight: 500;
      }

      .step-content {
        flex: 1;
        min-width: 0;
        display: flex;
        align-items: center;
        gap: 8px;
        overflow: hidden;

        .step-type {
          flex-shrink: 0;
        }

        .step-locator {
          flex: 1;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
          font-size: 13px;
          color: #333;
        }

        .step-desc {
          flex-shrink: 0;
          max-width: 150px;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
          font-size: 12px;
          color: #999;
        }
      }

      .step-actions {
        flex-shrink: 0;
        display: flex;
        gap: 4px;
        opacity: 0;
        transition: opacity 0.2s;

        .el-button {
          padding: 4px;
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
      height: 200px;
    }
  }

  .list-actions {
    display: flex;
    gap: 12px;
    padding: 12px;
    border-top: 1px solid #e8e8e8;
    background: white;
  }
}
</style>
