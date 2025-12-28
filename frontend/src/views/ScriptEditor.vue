<!--
脚本编辑器页面
提供用例基本信息编辑和测试步骤的可视化编辑
-->
<template>
  <div class="script-editor">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <el-button @click="handleBack" circle>
          <el-icon><ArrowLeft /></el-icon>
        </el-button>
        <h1>{{ isEdit ? '编辑用例' : '新建用例' }}</h1>
      </div>
      <div class="header-right">
        <el-button @click="handleBack">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">
          <el-icon><Check /></el-icon>
          保存
        </el-button>
      </div>
    </div>

    <!-- 内容区域 -->
    <div class="editor-content">
      <!-- 左侧：步骤列表 -->
      <div class="left-panel">
        <div class="panel-header">
          <span>测试步骤</span>
          <el-tag type="info">{{ steps.length }} 个步骤</el-tag>
        </div>
        <StepList
          :steps="steps"
          :selected-index="selectedIndex"
          @select="handleSelectStep"
          @add="handleAddStep"
          @delete="handleDeleteStep"
          @reorder="handleReorderSteps"
        />
      </div>

      <!-- 右侧：步骤详情 -->
      <div class="right-panel">
        <el-tabs v-model="activeTab" class="editor-tabs">
          <!-- 基本信息 -->
          <el-tab-pane label="基本信息" name="basic">
            <el-form
              ref="basicFormRef"
              :model="basicForm"
              :rules="basicRules"
              label-width="100px"
              class="basic-form"
            >
              <el-form-item label="用例名称" prop="name">
                <el-input v-model="basicForm.name" placeholder="请输入用例名称" />
              </el-form-item>

              <el-form-item label="优先级" prop="priority">
                <el-select v-model="basicForm.priority" placeholder="选择优先级">
                  <el-option
                    v-for="p in priorities"
                    :key="p.value"
                    :label="p.label"
                    :value="p.value"
                  />
                </el-select>
              </el-form-item>

              <el-form-item label="标签" prop="tags">
                <el-input v-model="basicForm.tags" placeholder="多个标签用逗号分隔" />
              </el-form-item>

              <el-form-item label="描述" prop="description">
                <el-input
                  v-model="basicForm.description"
                  type="textarea"
                  :rows="4"
                  placeholder="描述用例的测试目标和范围"
                />
              </el-form-item>
            </el-form>
          </el-tab-pane>

          <!-- 步骤编辑 -->
          <el-tab-pane label="步骤编辑" name="step">
            <div v-if="selectedStep" class="step-edit-area">
              <div class="step-title-bar">
                <span class="step-title">步骤 #{{ selectedStep.step_order }}</span>
                <el-tag>{{ getActionTypeName(selectedStep.action_type) }}</el-tag>
              </div>
              <StepEditor :step="selectedStep" @change="handleStepChange" />
            </div>
            <div v-else class="step-empty">
              <el-empty description="请选择一个步骤进行编辑" />
            </div>
          </el-tab-pane>

          <!-- JSON 预览 -->
          <el-tab-pane label="JSON 预览" name="json">
            <pre class="json-preview">{{ jsonPreview }}</pre>
          </el-tab-pane>
        </el-tabs>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { getCaseDetail, createCase, updateCase, saveSteps, getPriorities, getActionTypes } from '@/api/case'
import type { TestCase, TestStep, CreateCaseRequest } from '@/api/case'
import StepList from '@/components/StepList.vue'
import StepEditor from '@/components/StepEditor.vue'

const router = useRouter()
const route = useRoute()

// ========== 数据 ==========
const isEdit = computed(() => !!route.params.id)
const caseId = computed(() => route.params.id ? Number(route.params.id) : undefined)
const saving = ref(false)
const activeTab = ref('basic')
const selectedIndex = ref<number>(-1)

// 基本信息表单
const basicFormRef = ref<FormInstance>()
const basicForm = ref({
  name: '',
  description: '',
  priority: 'P1',
  tags: ''
})

const basicRules: FormRules = {
  name: [{ required: true, message: '请输入用例名称', trigger: 'blur' }],
  priority: [{ required: true, message: '请选择优先级', trigger: 'change' }]
}

// 步骤数据
const steps = ref<TestStep[]>([])
const selectedStep = computed(() => {
  if (selectedIndex.value === -1) return null
  return steps.value[selectedIndex.value]
})

// 选项
const priorities = getPriorities()
const actionTypes = getActionTypes()

// ========== 计算属性 ==========

// 安全解析 action_params（支持对象和 JSON 字符串）
const parseActionParams = (params?: string | Record<string, any>) => {
  if (!params) return undefined
  // 如果已经是对象，直接返回
  if (typeof params === 'object') {
    return params
  }
  // 如果是字符串，尝试解析
  try {
    return JSON.parse(params)
  } catch {
    return undefined
  }
}

// JSON 预览
const jsonPreview = computed(() => {
  const preview = {
    name: basicForm.value.name,
    description: basicForm.value.description,
    priority: basicForm.value.priority,
    tags: basicForm.value.tags,
    steps: steps.value.map((s, i) => ({
      step_order: i + 1,
      action_type: s.action_type,
      locator_type: s.locator_type,
      element_locator: s.element_locator,
      params: parseActionParams(s.action_params),
      description: s.description
    }))
  }
  return JSON.stringify(preview, null, 2)
})

// ========== 方法 ==========

// 获取操作类型名称
const getActionTypeName = (type: string) => {
  const action = actionTypes.find(a => a.value === type)
  return action?.label || type
}

// 加载用例详情
const loadCase = async () => {
  if (!caseId.value) return

  try {
    const response = await getCaseDetail(caseId.value)
    const data = response.data

    basicForm.value = {
      name: data.name,
      description: data.description || '',
      priority: data.priority || 'P1',
      tags: data.tags || ''
    }

    if (data.steps && data.steps.length > 0) {
      steps.value = [...data.steps]
    }
  } catch (error) {
    ElMessage.error('加载用例失败')
    router.back()
  }
}

// 选择步骤
const handleSelectStep = (index: number) => {
  selectedIndex.value = index
  activeTab.value = 'step'
}

// 添加步骤
const handleAddStep = (step: TestStep) => {
  step.step_order = steps.value.length + 1
  steps.value.push(step)
  selectedIndex.value = steps.value.length - 1
  activeTab.value = 'step'
}

// 删除步骤
const handleDeleteStep = (index: number) => {
  steps.value.splice(index, 1)
  // 重新编号
  steps.value.forEach((s, i) => {
    s.step_order = i + 1
  })
  if (selectedIndex.value >= steps.value.length) {
    selectedIndex.value = steps.value.length - 1
  }
}

// 重新排序步骤
const handleReorderSteps = (fromIndex: number, toIndex: number) => {
  const [removed] = steps.value.splice(fromIndex, 1)
  steps.value.splice(toIndex, 0, removed)
  // 重新编号
  steps.value.forEach((s, i) => {
    s.step_order = i + 1
  })
  selectedIndex.value = toIndex
}

// 步骤变化
const handleStepChange = (step: TestStep) => {
  if (selectedIndex.value !== -1) {
    steps.value[selectedIndex.value] = step
  }
}

// 保存
const handleSave = async () => {
  // 验证基本信息
  const valid = await basicFormRef.value?.validate().catch(() => false)
  if (!valid) return

  saving.value = true

  try {
    // 构建步骤数据（移除临时字段，action_params 转换为 dict）
    const stepsData = steps.value.map(s => {
      return {
        step_order: s.step_order,
        action_type: s.action_type,
        element_locator: s.element_locator || '',
        locator_type: s.locator_type,
        // 后端期望 dict 类型，使用 parseActionParams 处理
        action_params: parseActionParams(s.action_params),
        expected_result: s.expected_result,
        description: s.description
      }
    })

    if (isEdit.value && caseId.value) {
      // 更新基本信息
      await updateCase(caseId.value, {
        name: basicForm.value.name,
        description: basicForm.value.description,
        priority: basicForm.value.priority,
        tags: basicForm.value.tags
      })
      // 保存步骤
      await saveSteps(caseId.value, stepsData)
      ElMessage.success('保存成功')
    } else {
      // 创建新用例
      const data: CreateCaseRequest = {
        name: basicForm.value.name,
        description: basicForm.value.description,
        priority: basicForm.value.priority,
        tags: basicForm.value.tags,
        steps: stepsData
      }
      await createCase(data)
      ElMessage.success('创建成功')
      router.push('/')
    }
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

// 返回
const handleBack = () => {
  router.back()
}

// ========== 生命周期 ==========
onMounted(() => {
  if (isEdit.value) {
    loadCase()
  }
})
</script>

<style scoped lang="scss">
.script-editor {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f0f2f5; // 更新为新的背景色

  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 24px; // 保持不变
    background: white;
    border-bottom: 1px solid #f0f0f0; // 更新边框色
    box-shadow: 0 1px 6px rgba(0, 0, 0, 0.04); // 添加阴影

    .header-left {
      display: flex;
      align-items: center;
      gap: 16px; // 保持不变

      h1 {
        margin: 0;
        font-size: 20px;
        font-weight: 600; // 从 500 增加到 600
        color: #262626; // 添加文本色
      }
    }

    .header-right {
      display: flex;
      gap: 12px; // 保持不变
    }
  }

  .editor-content {
    flex: 1;
    display: flex;
    overflow: hidden;
    padding: 20px; // 从 16px 增加到 20px
    gap: 20px; // 从 16px 增加到 20px

    .left-panel {
      width: 360px; // 从 350px 增加到 360px
      display: flex;
      flex-direction: column;
      background: white;
      border-radius: 8px; // 从 4px 增加到 8px
      overflow: hidden;
      border: 1px solid #f0f0f0; // 添加边框
      box-shadow: 0 1px 6px rgba(0, 0, 0, 0.04); // 添加阴影

      .panel-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 14px 18px; // 增加内边距
        border-bottom: 1px solid #f0f0f0; // 更新边框色
        font-weight: 600; // 从 500 增加到 600
        color: #262626; // 添加文本色
        background: #fafafa; // 添加背景色
      }
    }

    .right-panel {
      flex: 1;
      background: white;
      border-radius: 8px; // 从 4px 增加到 8px
      overflow: hidden;
      border: 1px solid #f0f0f0; // 添加边框
      box-shadow: 0 1px 6px rgba(0, 0, 0, 0.04); // 添加阴影

      .editor-tabs {
        height: 100%;

        :deep(.el-tabs__header) {
          margin: 0;
          padding: 0 20px; // 添加水平内边距
          background: #fafafa; // 添加背景色
          border-bottom: 1px solid #f0f0f0; // 更新边框色

          .el-tabs__nav-wrap {
            &::after {
              display: none; // 移除默认底部边框
            }
          }

          .el-tabs__item {
            font-weight: 500; // 添加字重
            font-size: 15px; // 增加字体大小
            color: #595959; // 更新文本色
            height: 56px; // 增加高度
            line-height: 56px; // 调整行高
            transition: all 0.2s; // 添加过渡效果

            &:hover {
              color: #1677ff; // 悬停时使用主色
            }

            &.is-active {
              color: #1677ff; // 更新为新的主色
              font-weight: 600; // 激活状态加粗
            }
          }

          .el-tabs__active-bar {
            background: #1677ff; // 更新为新的主色
            height: 3px; // 增加高度
            border-radius: 3px 3px 0 0; // 添加圆角
          }
        }

        :deep(.el-tabs__content) {
          height: calc(100% - 56px); // 调整高度计算
          overflow-y: auto;
        }

        .basic-form {
          max-width: 640px; // 从 600px 增加到 640px
          padding: 32px; // 从 20px 增加到 32px
        }

        .step-edit-area {
          padding: 0;
        }

        .step-empty {
          display: flex;
          align-items: center;
          justify-content: center;
          height: 320px; // 从 300px 增加到 320px
        }

        .step-title-bar {
          display: flex;
          align-items: center;
          gap: 12px; // 保持不变
          padding: 16px 24px; // 增加内边距
          border-bottom: 1px solid #f0f0f0; // 更新边框色
          background: #fafafa; // 保持不变

          .step-title {
            font-weight: 600; // 从 500 增加到 600
            font-size: 16px;
            color: #262626; // 添加文本色
          }
        }

        .json-preview {
          margin: 0;
          padding: 24px; // 从 20px 增加到 24px
          background: #fafafa; // 从 #f5f5f5 更新为 #fafafa
          font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
          font-size: 13px;
          line-height: 1.6;
          overflow: auto;
          color: #262626; // 添加文本色
          border-radius: 6px; // 添加圆角
        }
      }
    }
  }
}
</style>
