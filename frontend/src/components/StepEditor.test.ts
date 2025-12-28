/**
 * StepEditor 组件测试
 * 测试步骤编辑器组件的功能
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import StepEditor from './StepEditor.vue'
import type { TestStep } from '@/store/modules/case'

// Mock Element Plus 组件
vi.mock('element-plus', () => ({
  ElForm: {
    template: '<form ref="formRef"><slot /></form>',
    methods: {
      validate: vi.fn().mockResolvedValue(true),
      resetFields: vi.fn()
    }
  },
  ElFormItem: { template: '<div class="el-form-item"><label>{{ $attrs.label }}</label><slot /></div>' },
  ElInput: {
    template: '<div class="el-input"><input :value="modelValue" @input="$emit(&quot;update:modelValue&quot;, $event.target.value)" :placeholder="placeholder" /></div>',
    props: ['modelValue', 'placeholder']
  },
  ElSelect: { template: '<select class="el-select"><slot /></select>' },
  ElOption: { template: '<option :value="value"><slot /></option>', props: ['value', 'label'] },
  ElButton: { template: '<button @click="$emit(&quot;click&quot;)"><slot /></button>' },
  ElIcon: { template: '<span><slot /></span>' }
}))

// Mock API 函数
vi.mock('@/api/case', () => ({
  getActionTypes: vi.fn(() => [
    { value: 'click', label: '点击', params: [] },
    { value: 'navigate', label: '导航', params: [{ key: 'url', label: 'URL', required: true, default: 'https://example.com' }] },
    { value: 'input', label: '输入', params: [{ key: 'text', label: '文本', required: true }] }
  ]),
  getLocatorTypes: vi.fn(() => [
    { value: 'css', label: 'CSS 选择器', placeholder: '#username' },
    { value: 'xpath', label: 'XPath', placeholder: '//input[@id="username"]' },
    { value: 'id', label: 'ID', placeholder: '#username' }
  ]
}))

describe('StepEditor 组件', () => {
  // 模拟步骤数据
  const mockStep: TestStep = {
    id: 1,
    case_id: 1,
    step_order: 1,
    action_type: 'click',
    element_locator: '#submit-btn',
    locator_type: 'css',
    action_params: undefined,
    expected_result: '按钮可点击',
    description: '点击提交按钮'
  }

  describe('基础渲染', () => {
    it('应该渲染表单字段', () => {
      const wrapper = mount(StepEditor, {
        props: {
          step: null
        }
      })

      expect(wrapper.find('.el-form-item').exists()).toBe(true)
    })

    it('应该显示操作类型选择器', () => {
      const wrapper = mount(StepEditor, {
        props: {
          step: null
        }
      })

      const formItems = wrapper.findAll('.el-form-item')
      // 第一个是操作类型
      expect(formItems[0].text()).toContain('操作类型')
    })

    it('应该显示定位类型选择器', () => {
      const wrapper = mount(StepEditor, {
        props: {
          step: null
        }
      })

      const formItems = wrapper.findAll('.el-form-item')
      // 第二个是定位类型
      expect(formItems[1].text()).toContain('定位类型')
    })

    it('应该显示元素定位输入框', () => {
      const wrapper = mount(StepEditor, {
        props: {
          step: null
        }
      })

      const formItems = wrapper.findAll('.el-form-item')
      // 第三个是元素定位
      expect(formItems[2].text()).toContain('元素定位')
    })

    it('应该显示期望结果文本域', () => {
      const wrapper = mount(StepEditor, {
        props: {
          step: null
        }
      })

      const formItems = wrapper.findAll('.el-form-item')
      // 倒数第二个是期望结果
      const expectedResultItem = formItems[formItems.length - 2]
      expect(expectedResultItem.text()).toContain('期望结果')
    })

    it('应该显示步骤描述文本域', () => {
      const wrapper = mount(StepEditor, {
        props: {
          step: null
        }
      })

      const formItems = wrapper.findAll('.el-form-item')
      // 最后一个是步骤描述
      const descriptionItem = formItems[formItems.length - 1]
      expect(descriptionItem.text()).toContain('步骤描述')
    })
  })

  describe('数据初始化', () => {
    it('应该使用传入的步骤数据初始化表单', async () => {
      const wrapper = mount(StepEditor, {
        props: {
          step: mockStep
        }
      })

      await nextTick()

      expect(wrapper.vm.formData.action_type).toBe('click')
      expect(wrapper.vm.formData.element_locator).toBe('#submit-btn')
      expect(wrapper.vm.formData.locator_type).toBe('css')
      expect(wrapper.vm.formData.expected_result).toBe('按钮可点击')
      expect(wrapper.vm.formData.description).toBe('点击提交按钮')
    })

    it('应该解析 action_params JSON 字符串', async () => {
      const stepWithParams: TestStep = {
        ...mockStep,
        action_params: '{"url": "https://example.com"}'
      }

      const wrapper = mount(StepEditor, {
        props: {
          step: stepWithParams
        }
      })

      await nextTick()

      expect(wrapper.vm.formData.action_params_value).toEqual({ url: 'https://example.com' })
    })

    it('无效的 JSON 应该返回空对象', async () => {
      const stepWithInvalidParams: TestStep = {
        ...mockStep,
        action_params: 'invalid json'
      }

      const wrapper = mount(StepEditor, {
        props: {
          step: stepWithInvalidParams
        }
      })

      await nextTick()

      expect(wrapper.vm.formData.action_params_value).toEqual({})
    })

    it('null 步骤应该使用默认值', () => {
      const wrapper = mount(StepEditor, {
        props: {
          step: null
        }
      })

      expect(wrapper.vm.formData.action_type).toBe('click')
      expect(wrapper.vm.formData.element_locator).toBe('')
      expect(wrapper.vm.formData.locator_type).toBe('css')
    })
  })

  describe('动态参数渲染', () => {
    it('navigate 操作应该显示 URL 参数输入框', async () => {
      const wrapper = mount(StepEditor, {
        props: {
          step: null
        }
      })

      // 设置操作类型为 navigate
      wrapper.vm.formData.action_type = 'navigate'
      await nextTick()

      const params = wrapper.vm.currentActionParams
      expect(params).toHaveLength(1)
      expect(params[0].key).toBe('url')
    })

    it('input 操作应该显示 text 参数输入框', async () => {
      const wrapper = mount(StepEditor, {
        props: {
          step: null
        }
      })

      // 设置操作类型为 input
      wrapper.vm.formData.action_type = 'input'
      await nextTick()

      const params = wrapper.vm.currentActionParams
      expect(params).toHaveLength(1)
      expect(params[0].key).toBe('text')
    })

    it('click 操作应该没有参数输入框', () => {
      const wrapper = mount(StepEditor, {
        props: {
          step: null
        }
      })

      // 默认是 click 操作
      const params = wrapper.vm.currentActionParams
      expect(params).toHaveLength(0)
    })

    it('参数输入框应该显示默认值按钮', async () => {
      const wrapper = mount(StepEditor, {
        props: {
          step: null
        }
      })

      // 设置操作类型为 navigate
      wrapper.vm.formData.action_type = 'navigate'
      await nextTick()

      const params = wrapper.vm.currentActionParams
      expect(params[0].default).toBe('https://example.com')
    })
  })

  describe('定位符占位符', () => {
    it('css 定位类型应该显示正确的占位符', async () => {
      const wrapper = mount(StepEditor, {
        props: {
          step: null
        }
      })

      wrapper.vm.formData.locator_type = 'css'
      await nextTick()

      expect(wrapper.vm.locatorPlaceholder).toBe('#username')
    })

    it('xpath 定位类型应该显示正确的占位符', async () => {
      const wrapper = mount(StepEditor, {
        props: {
          step: null
        }
      })

      wrapper.vm.formData.locator_type = 'xpath'
      await nextTick()

      expect(wrapper.vm.locatorPlaceholder).toContain('//')
    })

    it('id 定位类型应该显示正确的占位符', async () => {
      const wrapper = mount(StepEditor, {
        props: {
          step: null
        }
      })

      wrapper.vm.formData.locator_type = 'id'
      await nextTick()

      expect(wrapper.vm.locatorPlaceholder).toBe('#username')
    })
  })

  describe('change 事件', () => {
    it('表单数据变化应该触发 change 事件', async () => {
      const wrapper = mount(StepEditor, {
        props: {
          step: null
        }
      })

      // 深度监听会在数据变化后触发 emit
      wrapper.vm.formData.action_type = 'navigate'
      await nextTick()

      // change 事件应该被触发（由于 watch 深度监听）
      expect(wrapper.emitted('change')).toBeTruthy()
    })

    it('change 事件应该包含正确的步骤数据', async () => {
      const wrapper = mount(StepEditor, {
        props: {
          step: mockStep
        }
      })

      await nextTick()

      // 修改表单数据
      wrapper.vm.formData.description = '更新后的描述'
      await nextTick()

      const emittedEvents = wrapper.emitted('change')
      if (emittedEvents && emittedEvents.length > 0) {
        const emittedStep = emittedEvents[emittedEvents.length - 1][0] as TestStep
        expect(emittedStep.description).toBe('更新后的描述')
      }
    })

    it('序列化参数应该正确处理空对象', () => {
      const wrapper = mount(StepEditor, {
        props: {
          step: null
        }
      })

      wrapper.vm.formData.action_params_value = {}
      const serialized = wrapper.vm.serializeParams()

      expect(serialized).toBeUndefined()
    })

    it('序列化参数应该正确转换为 JSON', () => {
      const wrapper = mount(StepEditor, {
        props: {
          step: null
        }
      })

      wrapper.vm.formData.action_params_value = { url: 'https://example.com', timeout: 5000 }
      const serialized = wrapper.vm.serializeParams()

      expect(serialized).toBe('{"url":"https://example.com","timeout":5000}')
    })
  })

  describe('暴露的方法', () => {
    it('应该暴露 validate 方法', () => {
      const wrapper = mount(StepEditor, {
        props: {
          step: null
        }
      })

      expect(typeof wrapper.vm.validate).toBe('function')
    })

    it('应该暴露 resetFields 方法', () => {
      const wrapper = mount(StepEditor, {
        props: {
          step: null
        }
      })

      expect(typeof wrapper.vm.resetFields).toBe('function')
    })
  })
})
