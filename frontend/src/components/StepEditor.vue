<!--
步骤编辑器组件
用于编辑单个测试步骤的详细配置
-->
<template>
  <div class="step-editor">
    <el-form
      ref="formRef"
      :model="formData"
      :rules="rules"
      label-width="100px"
      label-position="right"
    >
      <!-- 操作类型 -->
      <el-form-item label="操作类型" prop="action_type">
        <el-select v-model="formData.action_type" placeholder="选择操作类型" style="width: 100%">
          <el-option
            v-for="action in actionTypes"
            :key="action.value"
            :label="action.label"
            :value="action.value"
          />
        </el-select>
      </el-form-item>

      <!-- 定位类型 -->
      <el-form-item label="定位类型" prop="locator_type">
        <el-select v-model="formData.locator_type" placeholder="选择定位类型" style="width: 100%">
          <el-option
            v-for="locator in locatorTypes"
            :key="locator.value"
            :label="locator.label"
            :value="locator.value"
          />
        </el-select>
      </el-form-item>

      <!-- 元素定位符 -->
      <el-form-item label="元素定位" prop="element_locator">
        <el-input
          v-model="formData.element_locator"
          :placeholder="locatorPlaceholder"
          clearable
        >
          <template #prepend>
            <el-icon><Position /></el-icon>
          </template>
        </el-input>
      </el-form-item>

      <!-- 操作参数（动态） -->
      <el-form-item
        v-for="param in currentActionParams"
        :key="param.key"
        :label="param.label"
        :prop="'action_params_value.' + param.key"
      >
        <el-input
          v-model="formData.action_params_value[param.key]"
          :placeholder="param.required ? `请输入${param.label}` : `可选${param.label}`"
          clearable
        >
          <template v-if="param.default" #append>
            <el-button @click="formData.action_params_value[param.key] = param.default">
              默认
            </el-button>
          </template>
        </el-input>
      </el-form-item>

      <!-- 期望结果 -->
      <el-form-item label="期望结果" prop="expected_result">
        <el-input
          v-model="formData.expected_result"
          type="textarea"
          :rows="2"
          placeholder="描述期望的结果"
        />
      </el-form-item>

      <!-- 步骤描述 -->
      <el-form-item label="步骤描述" prop="description">
        <el-input
          v-model="formData.description"
          type="textarea"
          :rows="2"
          placeholder="描述该步骤的作用"
        />
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import type { TestStep } from '@/store/modules/case'
import { getActionTypes, getLocatorTypes } from '@/api/case'

// ========== Props & Emits ==========
interface Props {
  step?: TestStep | null
}

interface Emits {
  (e: 'change', step: TestStep): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// ========== 数据 ==========
const formRef = ref<FormInstance>()
const actionTypes = getActionTypes()
const locatorTypes = getLocatorTypes()

// 标志位：防止循环更新（从 props 更新时不触发 emit）
const isUpdatingFromProps = ref(false)

// 表单数据
const formData = ref<TestStep>({
  step_order: 1,
  action_type: 'click',
  element_locator: '',
  locator_type: 'css',
  action_params_value: {},
  expected_result: '',
  description: ''
})

// ========== 计算属性 ==========

// 当前操作类型的参数配置
const currentActionParams = computed(() => {
  const action = actionTypes.find(a => a.value === formData.value.action_type)
  return action?.params || []
})

// 定位符占位符
const locatorPlaceholder = computed(() => {
  const locator = locatorTypes.find(l => l.value === formData.value.locator_type)
  return locator?.placeholder || '请输入元素定位符'
})

// ========== 表单验证规则 ==========
const rules: FormRules = {
  action_type: [{ required: true, message: '请选择操作类型', trigger: 'change' }],
  locator_type: [{ required: true, message: '请选择定位类型', trigger: 'change' }],
  element_locator: [{ required: true, message: '请输入元素定位符', trigger: 'blur' }]
}

// ========== 方法 ==========

// 序列化参数为 JSON 字符串
const serializeParams = () => {
  const params = formData.value.action_params_value
  if (Object.keys(params).length === 0) return undefined
  return JSON.stringify(params)
}

// 触发 change 事件
const emitChange = () => {
  const step: TestStep = {
    id: props.step?.id,
    case_id: props.step?.case_id,
    step_order: formData.value.step_order,
    action_type: formData.value.action_type,
    element_locator: formData.value.element_locator,
    locator_type: formData.value.locator_type,
    action_params: serializeParams(),
    expected_result: formData.value.expected_result,
    description: formData.value.description
  }
  emit('change', step)
}

// 解析参数（支持对象和 JSON 字符串）
const parseParams = (params?: string | Record<string, any>) => {
  if (!params) return {}
  // 如果已经是对象，直接返回
  if (typeof params === 'object') {
    return params
  }
  // 如果是字符串，尝试解析
  try {
    return JSON.parse(params)
  } catch {
    return {}
  }
}

// ========== 监听 ==========

// 监听表单变化（仅在非 props 更新时触发 emit）
watch(
  () => formData.value,
  () => {
    // 如果是从 props 更新的，不触发 emit（避免循环更新）
    if (!isUpdatingFromProps.value) {
      emitChange()
    }
  },
  { deep: true }
)

// 监听外部 step 变化
watch(
  () => props.step,
  (newStep) => {
    if (newStep) {
      // 设置标志位，防止触发 emit
      isUpdatingFromProps.value = true
      formData.value = {
        step_order: newStep.step_order,
        action_type: newStep.action_type,
        element_locator: newStep.element_locator,
        locator_type: newStep.locator_type,
        action_params_value: parseParams(newStep.action_params),
        expected_result: newStep.expected_result || '',
        description: newStep.description || ''
      }
      // 重置标志位
      setTimeout(() => {
        isUpdatingFromProps.value = false
      }, 0)
    }
  },
  { immediate: true }
)

// ========== 暴露方法 ==========
defineExpose({
  validate: () => formRef.value?.validate(),
  resetFields: () => formRef.value?.resetFields()
})
</script>

<style scoped lang="scss">
.step-editor {
  padding: 20px;
  background: white;
  border-radius: 4px;

  :deep(.el-form-item__label) {
    font-weight: 500;
  }
}
</style>
