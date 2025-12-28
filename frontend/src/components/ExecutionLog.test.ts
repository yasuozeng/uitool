/**
 * ExecutionLog 组件测试
 * 测试实时日志展示组件的功能
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import ExecutionLog from './ExecutionLog.vue'
import type { ExecutionLog as ExecutionLogType } from '@/store/modules/execution'

// Mock Element Plus 组件
vi.mock('element-plus', () => ({
  ElIcon: { template: '<div><slot /></div>' },
  ElTag: { template: '<div><slot /></div>' },
  ElButton: { template: '<button @click="$emit(&quot;click&quot;)"><slot /></button>' },
  ElEmpty: { template: '<div>{{ description }}</div>' }
}))

describe('ExecutionLog 组件', () => {
  // 模拟日志数据
  const mockLogs: ExecutionLogType[] = [
    {
      id: '1',
      timestamp: '2025-12-27T10:00:00',
      level: 'info',
      message: '开始执行',
      case_name: '测试用例1',
      step_order: 1
    },
    {
      id: '2',
      timestamp: '2025-12-27T10:00:01',
      level: 'success',
      message: '步骤执行成功',
      case_name: '测试用例1',
      step_order: 1
    },
    {
      id: '3',
      timestamp: '2025-12-27T10:00:02',
      level: 'error',
      message: '步骤执行失败',
      case_name: '测试用例2',
      step_order: 2,
      screenshot_path: 'screenshots/error1.png'
    }
  ]

  describe('基础渲染', () => {
    it('应该正确渲染日志列表', () => {
      const wrapper = mount(ExecutionLog, {
        props: {
          logs: mockLogs
        }
      })

      // 验证日志数量
      const logItems = wrapper.findAll('.log-item')
      expect(logItems).toHaveLength(3)
    })

    it('应该显示空状态', () => {
      const wrapper = mount(ExecutionLog, {
        props: {
          logs: []
        }
      })

      expect(wrapper.find('.log-empty').exists()).toBe(true)
      expect(wrapper.text()).toContain('暂无日志')
    })

    it('应该显示日志数量', () => {
      const wrapper = mount(ExecutionLog, {
        props: {
          logs: mockLogs
        }
      })

      expect(wrapper.find('.el-tag').text()).toContain('3 条')
    })

    it('无日志时不显示数量标签', () => {
      const wrapper = mount(ExecutionLog, {
        props: {
          logs: []
        }
      })

      expect(wrapper.find('.el-tag').exists()).toBe(false)
    })
  })

  describe('日志内容渲染', () => {
    it('应该显示日志时间', () => {
      const wrapper = mount(ExecutionLog, {
        props: {
          logs: mockLogs
        }
      })

      const timeElements = wrapper.findAll('.log-time')
      expect(timeElements).toHaveLength(3)
      expect(timeElements[0].text()).toMatch(/\d{2}:\d{2}:\d{2}/)
    })

    it('应该显示用例名称', () => {
      const wrapper = mount(ExecutionLog, {
        props: {
          logs: mockLogs
        }
      })

      const caseElements = wrapper.findAll('.log-case')
      expect(caseElements).toHaveLength(3)
      expect(caseElements[0].text()).toContain('[测试用例1]')
    })

    it('应该显示步骤序号', () => {
      const wrapper = mount(ExecutionLog, {
        props: {
          logs: mockLogs
        }
      })

      const stepElements = wrapper.findAll('.log-step')
      expect(stepElements).toHaveLength(3)
      expect(stepElements[0].text()).toContain('步骤 1:')
    })

    it('应该显示日志消息', () => {
      const wrapper = mount(ExecutionLog, {
        props: {
          logs: mockLogs
        }
      })

      const messages = wrapper.findAll('.log-message')
      expect(messages[0].text()).toBe('开始执行')
      expect(messages[1].text()).toBe('步骤执行成功')
      expect(messages[2].text()).toBe('步骤执行失败')
    })

    it('应该为错误日志显示截图按钮', () => {
      const wrapper = mount(ExecutionLog, {
        props: {
          logs: mockLogs
        }
      })

      const screenshotButtons = wrapper.findAll('.el-button')
      // 最后一个日志有截图，应该显示"查看截图"按钮
      expect(screenshotButtons[screenshotButtons.length - 1].text()).toContain('查看截图')
    })
  })

  describe('日志级别样式', () => {
    it('应该为 info 日志应用正确的样式', () => {
      const wrapper = mount(ExecutionLog, {
        props: {
          logs: [
            {
              id: '1',
              timestamp: '2025-12-27T10:00:00',
              level: 'info',
              message: 'Info message'
            }
          ]
        }
      })

      expect(wrapper.find('.log-info').exists()).toBe(true)
    })

    it('应该为 success 日志应用正确的样式', () => {
      const wrapper = mount(ExecutionLog, {
        props: {
          logs: [
            {
              id: '1',
              timestamp: '2025-12-27T10:00:00',
              level: 'success',
              message: 'Success message'
            }
          ]
        }
      })

      expect(wrapper.find('.log-success').exists()).toBe(true)
    })

    it('应该为 error 日志应用正确的样式', () => {
      const wrapper = mount(ExecutionLog, {
        props: {
          logs: [
            {
              id: '1',
              timestamp: '2025-12-27T10:00:00',
              level: 'error',
              message: 'Error message'
            }
          ]
        }
      })

      expect(wrapper.find('.log-error').exists()).toBe(true)
    })

    it('应该为 warning 日志应用正确的样式', () => {
      const wrapper = mount(ExecutionLog, {
        props: {
          logs: [
            {
              id: '1',
              timestamp: '2025-12-27T10:00:00',
              level: 'warning',
              message: 'Warning message'
            }
          ]
        }
      })

      expect(wrapper.find('.log-warning').exists()).toBe(true)
    })
  })

  describe('用户交互', () => {
    it('点击清空按钮应该触发 clear 事件', async () => {
      const wrapper = mount(ExecutionLog, {
        props: {
          logs: mockLogs
        }
      })

      // 查找清空按钮（文本包含"清空"）
      const clearButton = wrapper.findAll('.el-button').find(btn => btn.text().includes('清空'))
      expect(clearButton).toBeDefined()

      await clearButton!.trigger('click')
      expect(wrapper.emitted('clear')).toBeTruthy()
    })

    it('点击查看截图按钮应该触发 viewScreenshot 事件', async () => {
      const wrapper = mount(ExecutionLog, {
        props: {
          logs: mockLogs
        }
      })

      // 查找包含"查看截图"的按钮
      const screenshotButtons = wrapper.findAll('.el-button').filter(btn => btn.text().includes('查看截图'))
      expect(screenshotButtons.length).toBeGreaterThan(0)

      await screenshotButtons[0].trigger('click')
      expect(wrapper.emitted('viewScreenshot')).toBeTruthy()
      expect(wrapper.emitted('viewScreenshot')?.[0]).toEqual(['screenshots/error1.png'])
    })
  })

  describe('自动滚动', () => {
    it('日志变化时应该自动滚动到底部', async () => {
      const wrapper = mount(ExecutionLog, {
        props: {
          logs: []
        }
      })

      // Mock scrollHeight 和 scrollTop
      const mockElement = {
        scrollHeight: 1000,
        scrollTop: 0
      }

      wrapper.vm.$refs.logContainer = mockElement

      // 添加新日志
      await wrapper.setProps({
        logs: [
          {
            id: '1',
            timestamp: '2025-12-27T10:00:00',
            level: 'info',
            message: 'New log'
          }
        ]
      })

      await nextTick()

      // 验证 scrollTop 被设置为 scrollHeight
      expect(mockElement.scrollTop).toBe(mockElement.scrollHeight)
    })
  })

  describe('时间格式化', () => {
    it('应该正确格式化时间戳', () => {
      const wrapper = mount(ExecutionLog, {
        props: {
          logs: [
            {
              id: '1',
              timestamp: '2025-12-27T10:30:45',
              level: 'info',
              message: 'Test'
            }
          ]
        }
      })

      const timeText = wrapper.find('.log-time').text()
      expect(timeText).toMatch(/10:30:45/)
    })
  })
})
