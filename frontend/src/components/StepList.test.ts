/**
 * StepList 组件测试
 * 测试步骤列表组件的功能（包括拖拽）
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import StepList from './StepList.vue'
import type { TestStep } from '@/store/modules/case'

// Mock Element Plus 组件
vi.mock('element-plus', () => ({
  ElTag: { template: '<span class="el-tag" :type="type"><slot /></span>', props: ['type'] },
  ElButton: { template: '<button @click="$emit(&quot;click&quot;)"><slot /></button>' },
  ElIcon: { template: '<span><slot /></span>' },
  ElEmpty: { template: '<div>{{ description }}</div>' }
}))

// Mock API 函数
vi.mock('@/api/case', () => ({
  getActionTypes: vi.fn(() => [
    { value: 'click', label: '点击' },
    { value: 'navigate', label: '导航' },
    { value: 'input', label: '输入' },
    { value: 'clear', label: '清除' },
    { value: 'wait', label: '等待' },
    { value: 'verify_text', label: '验证文本' },
    { value: 'verify_element', label: '验证元素' },
    { value: 'select', label: '选择' },
    { value: 'hover', label: '悬停' },
    { value: 'scroll', label: '滚动' },
    { value: 'screenshot', label: '截图' }
  ])
}))

describe('StepList 组件', () => {
  // 模拟步骤数据
  const mockSteps: TestStep[] = [
    {
      id: 1,
      case_id: 1,
      step_order: 1,
      action_type: 'navigate',
      element_locator: '',
      locator_type: '',
      description: '打开首页'
    },
    {
      id: 2,
      case_id: 1,
      step_order: 2,
      action_type: 'input',
      element_locator: '#username',
      locator_type: 'css',
      description: '输入用户名'
    },
    {
      id: 3,
      case_id: 1,
      step_order: 3,
      action_type: 'click',
      element_locator: '#submit',
      locator_type: 'css',
      description: '点击提交'
    }
  ]

  describe('基础渲染', () => {
    it('应该渲染所有步骤', () => {
      const wrapper = mount(StepList, {
        props: {
          steps: mockSteps
        }
      })

      const stepItems = wrapper.findAll('.step-item')
      expect(stepItems).toHaveLength(3)
    })

    it('空列表应该显示空状态', () => {
      const wrapper = mount(StepList, {
        props: {
          steps: []
        }
      })

      expect(wrapper.find('.empty-state').exists()).toBe(true)
      expect(wrapper.text()).toContain('暂无测试步骤')
    })

    it('应该显示步骤序号', () => {
      const wrapper = mount(StepList, {
        props: {
          steps: mockSteps
        }
      })

      const orderElements = wrapper.findAll('.step-order')
      expect(orderElements[0].text()).toBe('1')
      expect(orderElements[1].text()).toBe('2')
      expect(orderElements[2].text()).toBe('3')
    })

    it('应该显示操作类型标签', () => {
      const wrapper = mount(StepList, {
        props: {
          steps: mockSteps
        }
      })

      const typeElements = wrapper.findAll('.step-type .el-tag')
      expect(typeElements[0].text()).toBe('导航')
      expect(typeElements[1].text()).toBe('输入')
      expect(typeElements[2].text()).toBe('点击')
    })

    it('应该显示元素定位符', () => {
      const wrapper = mount(StepList, {
        props: {
          steps: mockSteps
        }
      })

      const locatorElements = wrapper.findAll('.step-locator')
      expect(locatorElements[1].text()).toBe('#username')
      expect(locatorElements[2].text()).toBe('#submit')
    })

    it('空定位符应该显示 "-"', () => {
      const wrapper = mount(StepList, {
        props: {
          steps: mockSteps
        }
      })

      const locatorElements = wrapper.findAll('.step-locator')
      expect(locatorElements[0].text()).toBe('-')
    })

    it('应该显示步骤描述', () => {
      const wrapper = mount(StepList, {
        props: {
          steps: mockSteps
        }
      })

      const descElements = wrapper.findAll('.step-desc')
      expect(descElements[0].text()).toBe('打开首页')
      expect(descElements[1].text()).toBe('输入用户名')
      expect(descElements[2].text()).toBe('点击提交')
    })
  })

  describe('操作类型颜色', () => {
    it('navigate 应该是 primary 类型', () => {
      const wrapper = mount(StepList, {
        props: {
          steps: [{ ...mockSteps[0], action_type: 'navigate' }]
        }
      })

      const color = wrapper.vm.getActionTypeColor('navigate')
      expect(color).toBe('primary')
    })

    it('click 应该是 success 类型', () => {
      const wrapper = mount(StepList, {
        props: {
          steps: [{ ...mockSteps[0], action_type: 'click' }]
        }
      })

      const color = wrapper.vm.getActionTypeColor('click')
      expect(color).toBe('success')
    })

    it('input 应该是 warning 类型', () => {
      const wrapper = mount(StepList, {
        props: {
          steps: [{ ...mockSteps[0], action_type: 'input' }]
        }
      })

      const color = wrapper.vm.getActionTypeColor('input')
      expect(color).toBe('warning')
    })

    it('wait 应该是 info 类型', () => {
      const wrapper = mount(StepList, {
        props: {
          steps: [{ ...mockSteps[0], action_type: 'wait' }]
        }
      })

      const color = wrapper.vm.getActionTypeColor('wait')
      expect(color).toBe('info')
    })

    it('screenshot 应该是 danger 类型', () => {
      const wrapper = mount(StepList, {
        props: {
          steps: [{ ...mockSteps[0], action_type: 'screenshot' }]
        }
      })

      const color = wrapper.vm.getActionTypeColor('screenshot')
      expect(color).toBe('danger')
    })

    it('未知类型应该返回空字符串', () => {
      const wrapper = mount(StepList, {
        props: {
          steps: mockSteps
        }
      })

      const color = wrapper.vm.getActionTypeColor('unknown_type')
      expect(color).toBe('')
    })
  })

  describe('选中状态', () => {
    it('应该根据 selectedIndex 应用 active 样式', () => {
      const wrapper = mount(StepList, {
        props: {
          steps: mockSteps,
          selectedIndex: 1
        }
      })

      const stepItems = wrapper.findAll('.step-item')
      expect(stepItems[0].classes()).not.toContain('active')
      expect(stepItems[1].classes()).toContain('active')
      expect(stepItems[2].classes()).not.toContain('active')
    })

    it('点击步骤应该触发 select 事件', async () => {
      const wrapper = mount(StepList, {
        props: {
          steps: mockSteps
        }
      })

      const stepItems = wrapper.findAll('.step-item')
      await stepItems[1].trigger('click')

      expect(wrapper.emitted('select')).toBeTruthy()
      expect(wrapper.emitted('select')?.[0]).toEqual([1])
    })
  })

  describe('操作按钮', () => {
    it('每个步骤应该有复制和删除按钮', () => {
      const wrapper = mount(StepList, {
        props: {
          steps: mockSteps
        }
      })

      const stepItems = wrapper.findAll('.step-item')
      stepItems.forEach(item => {
        const buttons = item.findAll('.step-actions .el-button')
        expect(buttons).toHaveLength(2)
      })
    })

    it('点击复制按钮应该触发 add 事件', async () => {
      const wrapper = mount(StepList, {
        props: {
          steps: mockSteps
        }
      })

      const copyButtons = wrapper.findAll('.step-item').map(item =>
        item.findAll('.step-actions .el-button')[0]
      )

      await copyButtons[0].trigger('click')

      expect(wrapper.emitted('add')).toBeTruthy()
      const addedStep = wrapper.emitted('add')?.[0][0] as TestStep
      expect(addedStep.step_order).toBe(4) // 原有3个步骤，新步骤序号是4
    })

    it('点击删除按钮应该触发 delete 事件', async () => {
      const wrapper = mount(StepList, {
        props: {
          steps: mockSteps
        }
      })

      const deleteButtons = wrapper.findAll('.step-item').map(item =>
        item.findAll('.step-actions .el-button')[1]
      )

      await deleteButtons[1].trigger('click')

      expect(wrapper.emitted('delete')).toBeTruthy()
      expect(wrapper.emitted('delete')?.[0]).toEqual([1])
    })

    it('删除事件应该使用 stopPropagation', async () => {
      const wrapper = mount(StepList, {
        props: {
          steps: mockSteps
        }
      })

      const deleteButton = wrapper.findAll('.step-item')[1].findAll('.step-actions .el-button')[1]

      await deleteButton.trigger('click')

      // 应该只触发 delete，不触发 select
      expect(wrapper.emitted('delete')).toBeTruthy()
      expect(wrapper.emitted('select')).toBeFalsy()
    })
  })

  describe('底部操作栏', () => {
    it('应该显示添加步骤按钮', () => {
      const wrapper = mount(StepList, {
        props: {
          steps: mockSteps
        }
      })

      const buttons = wrapper.findAll('.list-actions .el-button')
      const addButton = buttons.find(btn => btn.text().includes('添加步骤'))
      expect(addButton).toBeDefined()
    })

    it('点击添加按钮应该触发 add 事件', async () => {
      const wrapper = mount(StepList, {
        props: {
          steps: mockSteps
        }
      })

      const buttons = wrapper.findAll('.list-actions .el-button')
      const addButton = buttons.find(btn => btn.text().includes('添加步骤'))!

      await addButton.trigger('click')

      expect(wrapper.emitted('add')).toBeTruthy()
      const newStep = wrapper.emitted('add')?.[0][0] as TestStep
      expect(newStep.step_order).toBe(4) // 原有3个步骤
      expect(newStep.action_type).toBe('click')
    })

    it('应该显示清空全部按钮', () => {
      const wrapper = mount(StepList, {
        props: {
          steps: mockSteps
        }
      })

      const buttons = wrapper.findAll('.list-actions .el-button')
      const clearButton = buttons.find(btn => btn.text().includes('清空全部'))
      expect(clearButton).toBeDefined()
    })

    it('空列表时清空按钮应该禁用', () => {
      const wrapper = mount(StepList, {
        props: {
          steps: []
        }
      })

      const buttons = wrapper.findAll('.list-actions .el-button')
      const clearButton = buttons.find(btn => btn.text().includes('清空全部'))!
      const buttonElement = clearButton.element as HTMLButtonElement
      expect(buttonElement.disabled).toBe(true)
    })

    it('点击清空全部应该触发多次 delete 事件', async () => {
      const wrapper = mount(StepList, {
        props: {
          steps: mockSteps
        }
      })

      const buttons = wrapper.findAll('.list-actions .el-button')
      const clearButton = buttons.find(btn => btn.text().includes('清空全部'))!

      await clearButton.trigger('click')

      const deleteEvents = wrapper.emitted('delete')
      expect(deleteEvents).toBeTruthy()
      expect(deleteEvents?.length).toBe(3) // 3个步骤
      // 应该从后往前删除：2, 1, 0
      expect(deleteEvents?.[0]).toEqual([2])
      expect(deleteEvents?.[1]).toEqual([1])
      expect(deleteEvents?.[2]).toEqual([0])
    })
  })

  describe('拖拽功能', () => {
    it('步骤应该有 draggable 属性', () => {
      const wrapper = mount(StepList, {
        props: {
          steps: mockSteps
        }
      })

      const stepItems = wrapper.findAll('.step-item')
      stepItems.forEach(item => {
        expect(item.attributes('draggable')).toBe('true')
      })
    })

    it('dragstart 事件应该设置拖拽索引', async () => {
      const wrapper = mount(StepList, {
        props: {
          steps: mockSteps
        }
      })

      const stepItems = wrapper.findAll('.step-item')
      const mockEvent = {
        preventDefault: vi.fn(),
        dataTransfer: {
          effectAllowed: '',
          dropEffect: ''
        }
      }

      await stepItems[0].trigger('dragstart', mockEvent)

      expect(mockEvent.dataTransfer.effectAllowed).toBe('move')
      expect(wrapper.vm.dragIndex).toBe(0)
    })

    it('dragover 事件应该阻止默认行为', async () => {
      const wrapper = mount(StepList, {
        props: {
          steps: mockSteps
        }
      })

      const mockEvent = {
        preventDefault: vi.fn(),
        dataTransfer: {
          effectAllowed: '',
          dropEffect: ''
        }
      }

      await wrapper.find('.step-item').trigger('dragover', mockEvent)

      expect(mockEvent.preventDefault).toHaveBeenCalled()
      expect(mockEvent.dataTransfer.dropEffect).toBe('move')
    })

    it('drop 事件应该触发 reorder 事件', async () => {
      const wrapper = mount(StepList, {
        props: {
          steps: mockSteps
        }
      })

      const stepItems = wrapper.findAll('.step-item')

      // 先触发 dragstart
      const mockDragEvent = {
        preventDefault: vi.fn(),
        dataTransfer: {
          effectAllowed: '',
          dropEffect: ''
        }
      }
      await stepItems[0].trigger('dragstart', mockDragEvent)

      // 再触发 drop
      const mockDropEvent = {
        preventDefault: vi.fn(),
        dataTransfer: {
          effectAllowed: '',
          dropEffect: ''
        }
      }
      await stepItems[2].trigger('drop', mockDropEvent)

      expect(wrapper.emitted('reorder')).toBeTruthy()
      expect(wrapper.emitted('reorder')?.[0]).toEqual([0, 2])
    })

    it('drop 到相同位置不应该触发 reorder', async () => {
      const wrapper = mount(StepList, {
        props: {
          steps: mockSteps
        }
      })

      const stepItems = wrapper.findAll('.step-item')

      // 先触发 dragstart
      const mockDragEvent = {
        preventDefault: vi.fn(),
        dataTransfer: {
          effectAllowed: '',
          dropEffect: ''
        }
      }
      await stepItems[1].trigger('dragstart', mockDragEvent)

      // 再触发 drop 到相同位置
      const mockDropEvent = {
        preventDefault: vi.fn(),
        dataTransfer: {
          effectAllowed: '',
          dropEffect: ''
        }
      }
      await stepItems[1].trigger('drop', mockDropEvent)

      expect(wrapper.emitted('reorder')).toBeFalsy()
    })

    it('drop 后应该重置拖拽索引', async () => {
      const wrapper = mount(StepList, {
        props: {
          steps: mockSteps
        }
      })

      const stepItems = wrapper.findAll('.step-item')

      // 先触发 dragstart
      const mockDragEvent = {
        preventDefault: vi.fn(),
        dataTransfer: {
          effectAllowed: '',
          dropEffect: ''
        }
      }
      await stepItems[0].trigger('dragstart', mockDragEvent)
      expect(wrapper.vm.dragIndex).toBe(0)

      // 再触发 drop
      const mockDropEvent = {
        preventDefault: vi.fn(),
        dataTransfer: {
          effectAllowed: '',
          dropEffect: ''
        }
      }
      await stepItems[2].trigger('drop', mockDropEvent)

      expect(wrapper.vm.dragIndex).toBe(-1)
    })
  })

  describe('操作类型名称获取', () => {
    it('应该返回正确的操作类型名称', () => {
      const wrapper = mount(StepList, {
        props: {
          steps: mockSteps
        }
      })

      expect(wrapper.vm.getActionTypeName('navigate')).toBe('导航')
      expect(wrapper.vm.getActionTypeName('click')).toBe('点击')
      expect(wrapper.vm.getActionTypeName('input')).toBe('输入')
    })

    it('未知类型应该返回原值', () => {
      const wrapper = mount(StepList, {
        props: {
          steps: mockSteps
        }
      })

      expect(wrapper.vm.getActionTypeName('unknown_type')).toBe('unknown_type')
    })
  })
})
