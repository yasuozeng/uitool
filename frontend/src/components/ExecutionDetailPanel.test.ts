/**
 * ExecutionDetailPanel 组件测试
 * 测试执行详情面板组件的功能
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import ExecutionDetailPanel from './ExecutionDetailPanel.vue'
import type { Execution } from '@/api/execution'

// Mock Element Plus 组件
vi.mock('element-plus', () => ({
  ElTag: { template: '<span class="el-tag" :type="type"><slot /></span>', props: ['type'] },
  ElTable: { template: '<table class="el-table"><slot /></table>' },
  ElTableColumn: { template: '<th><slot /></th>' },
  ElButton: { template: '<button @click="$emit(&quot;click&quot;)"><slot /></button>' },
  ElIcon: { template: '<span><slot /></span>' },
  ElDialog: {
    template: '<div v-if="modelValue" class="el-dialog"><slot /></div>',
    props: ['modelValue']
  }
}))

// Mock window.open
const mockOpen = vi.fn()
Object.defineProperty(window, 'open', {
  value: mockOpen,
  writable: true
})

describe('ExecutionDetailPanel 组件', () => {
  // 模拟执行数据
  const mockExecution: Execution = {
    id: 1,
    status: 'completed',
    browser: 'chrome',
    headless: true,
    window_size: '1920x1080',
    total_cases: 3,
    passed_cases: 2,
    failed_cases: 1,
    started_at: '2025-12-27T10:00:00',
    completed_at: '2025-12-27T10:05:00',
    duration: 300000,
    details: [
      {
        case_id: 1,
        case_name: '登录测试',
        status: 'completed',
        passed_steps: 5,
        failed_steps: 0,
        started_at: '2025-12-27T10:00:00',
        completed_at: '2025-12-27T10:01:00'
      },
      {
        case_id: 2,
        case_name: '注册测试',
        status: 'completed',
        passed_steps: 3,
        failed_steps: 0,
        started_at: '2025-12-27T10:01:00',
        completed_at: '2025-12-27T10:02:00'
      },
      {
        case_id: 3,
        case_name: '支付测试',
        status: 'failed',
        passed_steps: 2,
        failed_steps: 1,
        started_at: '2025-12-27T10:02:00',
        completed_at: '2025-12-27T10:05:00',
        error_message: '支付超时',
        screenshot_path: 'screenshots/payment_error.png'
      }
    ]
  }

  describe('执行概要信息', () => {
    it('应该显示执行 ID', () => {
      const wrapper = mount(ExecutionDetailPanel, {
        props: {
          execution: mockExecution
        }
      })

      const summaryItems = wrapper.findAll('.summary-item')
      expect(summaryItems[0].text()).toContain('执行 ID:')
      expect(summaryItems[0].text()).toContain('1')
    })

    it('应该显示浏览器类型', () => {
      const wrapper = mount(ExecutionDetailPanel, {
        props: {
          execution: mockExecution
        }
      })

      const summaryItems = wrapper.findAll('.summary-item')
      expect(summaryItems[1].text()).toContain('浏览器:')
      expect(summaryItems[1].text()).toContain('Chrome')
    })

    it('应该显示执行状态', () => {
      const wrapper = mount(ExecutionDetailPanel, {
        props: {
          execution: mockExecution
        }
      })

      const summaryItems = wrapper.findAll('.summary-item')
      expect(summaryItems[2].text()).toContain('状态:')
      expect(summaryItems[2].text()).toContain('已完成')
    })

    it('应该显示总用例数', () => {
      const wrapper = mount(ExecutionDetailPanel, {
        props: {
          execution: mockExecution
        }
      })

      const summaryItems = wrapper.findAll('.summary-item')
      expect(summaryItems[3].text()).toContain('总用例:')
      expect(summaryItems[3].text()).toContain('3')
    })

    it('应该显示通过用例数', () => {
      const wrapper = mount(ExecutionDetailPanel, {
        props: {
          execution: mockExecution
        }
      })

      const summaryItems = wrapper.findAll('.summary-item')
      expect(summaryItems[4].text()).toContain('通过:')
      expect(wrapper.find('.value.success').text()).toBe('2')
    })

    it('应该显示失败用例数', () => {
      const wrapper = mount(ExecutionDetailPanel, {
        props: {
          execution: mockExecution
        }
      })

      const summaryItems = wrapper.findAll('.summary-item')
      expect(summaryItems[5].text()).toContain('失败:')
      expect(wrapper.find('.value.failed').text()).toBe('1')
    })

    it('应该显示通过率', () => {
      const wrapper = mount(ExecutionDetailPanel, {
        props: {
          execution: mockExecution
        }
      })

      const summaryItems = wrapper.findAll('.summary-item')
      expect(summaryItems[6].text()).toContain('通过率:')
      expect(summaryItems[6].text()).toContain('67%') // 2/3 * 100 = 66.67 -> 67
    })
  })

  describe('通过率计算', () => {
    it('应该正确计算通过率', () => {
      const wrapper = mount(ExecutionDetailPanel, {
        props: {
          execution: mockExecution
        }
      })

      expect(wrapper.vm.passRate).toBe(67) // Math.round(2/3 * 100) = 67
    })

    it('全部通过应该返回 100', () => {
      const execution: Execution = {
        ...mockExecution,
        passed_cases: 3,
        failed_cases: 0
      }

      const wrapper = mount(ExecutionDetailPanel, {
        props: {
          execution
        }
      })

      expect(wrapper.vm.passRate).toBe(100)
    })

    it('全部失败应该返回 0', () => {
      const execution: Execution = {
        ...mockExecution,
        passed_cases: 0,
        failed_cases: 3
      }

      const wrapper = mount(ExecutionDetailPanel, {
        props: {
          execution
        }
      })

      expect(wrapper.vm.passRate).toBe(0)
    })

    it('总用例为 0 应该返回 0', () => {
      const execution: Execution = {
        ...mockExecution,
        total_cases: 0,
        passed_cases: 0,
        failed_cases: 0
      }

      const wrapper = mount(ExecutionDetailPanel, {
        props: {
          execution
        }
      })

      expect(wrapper.vm.passRate).toBe(0)
    })
  })

  describe('浏览器标签', () => {
    it('Chrome 应该显示为 Chrome', () => {
      const wrapper = mount(ExecutionDetailPanel, {
        props: {
          execution: { ...mockExecution, browser: 'chrome' }
        }
      })

      expect(wrapper.vm.getBrowserLabel('chrome')).toBe('Chrome')
    })

    it('Firefox 应该显示为 Firefox', () => {
      const wrapper = mount(ExecutionDetailPanel, {
        props: {
          execution: { ...mockExecution, browser: 'firefox' }
        }
      })

      expect(wrapper.vm.getBrowserLabel('firefox')).toBe('Firefox')
    })

    it('Edge 应该显示为 Edge', () => {
      const wrapper = mount(ExecutionDetailPanel, {
        props: {
          execution: { ...mockExecution, browser: 'edge' }
        }
      })

      expect(wrapper.vm.getBrowserLabel('edge')).toBe('Edge')
    })

    it('未知浏览器应该返回原值', () => {
      const wrapper = mount(ExecutionDetailPanel, {
        props: {
          execution: { ...mockExecution, browser: 'safari' }
        }
      })

      expect(wrapper.vm.getBrowserLabel('safari')).toBe('safari')
    })
  })

  describe('状态标签', () => {
    it('pending 状态应该返回 info 类型', () => {
      const wrapper = mount(ExecutionDetailPanel, {
        props: {
          execution: mockExecution
        }
      })

      expect(wrapper.vm.getStatusType('pending')).toBe('info')
    })

    it('running 状态应该返回 warning 类型', () => {
      const wrapper = mount(ExecutionDetailPanel, {
        props: {
          execution: mockExecution
        }
      })

      expect(wrapper.vm.getStatusType('running')).toBe('warning')
    })

    it('completed 状态应该返回 success 类型', () => {
      const wrapper = mount(ExecutionDetailPanel, {
        props: {
          execution: mockExecution
        }
      })

      expect(wrapper.vm.getStatusType('completed')).toBe('success')
    })

    it('failed 状态应该返回 danger 类型', () => {
      const wrapper = mount(ExecutionDetailPanel, {
        props: {
          execution: mockExecution
        }
      })

      expect(wrapper.vm.getStatusType('failed')).toBe('danger')
    })

    it('cancelled 状态应该返回空字符串类型', () => {
      const wrapper = mount(ExecutionDetailPanel, {
        props: {
          execution: mockExecution
        }
      })

      expect(wrapper.vm.getStatusType('cancelled')).toBe('')
    })

    it('pending 状态应该显示"待执行"', () => {
      const wrapper = mount(ExecutionDetailPanel, {
        props: {
          execution: mockExecution
        }
      })

      expect(wrapper.vm.getStatusLabel('pending')).toBe('待执行')
    })

    it('running 状态应该显示"执行中"', () => {
      const wrapper = mount(ExecutionDetailPanel, {
        props: {
          execution: mockExecution
        }
      })

      expect(wrapper.vm.getStatusLabel('running')).toBe('执行中')
    })

    it('completed 状态应该显示"已完成"', () => {
      const wrapper = mount(ExecutionDetailPanel, {
        props: {
          execution: mockExecution
        }
      })

      expect(wrapper.vm.getStatusLabel('completed')).toBe('已完成')
    })

    it('failed 状态应该显示"失败"', () => {
      const wrapper = mount(ExecutionDetailPanel, {
        props: {
          execution: mockExecution
        }
      })

      expect(wrapper.vm.getStatusLabel('failed')).toBe('失败')
    })

    it('cancelled 状态应该显示"已取消"', () => {
      const wrapper = mount(ExecutionDetailPanel, {
        props: {
          execution: mockExecution
        }
      })

      expect(wrapper.vm.getStatusLabel('cancelled')).toBe('已取消')
    })
  })

  describe('用例执行结果表格', () => {
    it('应该渲染表格', () => {
      const wrapper = mount(ExecutionDetailPanel, {
        props: {
          execution: mockExecution
        }
      })

      expect(wrapper.find('.el-table').exists()).toBe(true)
    })

    it('应该显示所有用例详情', () => {
      const wrapper = mount(ExecutionDetailPanel, {
        props: {
          execution: mockExecution
        }
      })

      expect(wrapper.text()).toContain('登录测试')
      expect(wrapper.text()).toContain('注册测试')
      expect(wrapper.text()).toContain('支付测试')
    })

    it('失败的用例应该显示截图按钮', () => {
      const wrapper = mount(ExecutionDetailPanel, {
        props: {
          execution: mockExecution
        }
      })

      const buttons = wrapper.findAll('.el-button')
      const screenshotButtons = buttons.filter(btn => btn.text().includes('查看截图'))
      expect(screenshotButtons.length).toBe(1)
    })

    it('有错误信息的用例应该显示查看错误按钮', () => {
      const wrapper = mount(ExecutionDetailPanel, {
        props: {
          execution: mockExecution
        }
      })

      const buttons = wrapper.findAll('.el-button')
      const errorButtons = buttons.filter(btn => btn.text().includes('查看错误'))
      expect(errorButtons.length).toBe(1)
    })
  })

  describe('时间格式化', () => {
    it('应该正确格式化时间字符串', () => {
      const wrapper = mount(ExecutionDetailPanel, {
        props: {
          execution: mockExecution
        }
      })

      const formatted = wrapper.vm.formatDate('2025-12-27T10:30:45')
      expect(formatted).toMatch(/2025/)
      expect(formatted).toMatch(/12\/27/)
    })

    it('空时间应该返回 "-"', () => {
      const wrapper = mount(ExecutionDetailPanel, {
        props: {
          execution: mockExecution
        }
      })

      expect(wrapper.vm.formatDate('')).toBe('-')
      expect(wrapper.vm.formatDate(undefined as any)).toBe('-')
    })
  })

  describe('用户交互', () => {
    beforeEach(() => {
      mockOpen.mockClear()
    })

    it('点击查看截图应该显示对话框', async () => {
      const wrapper = mount(ExecutionDetailPanel, {
        props: {
          execution: mockExecution
        }
      })

      wrapper.vm.handleViewScreenshot('screenshots/test.png')

      expect(wrapper.vm.screenshotDialogVisible).toBe(true)
      expect(wrapper.vm.currentScreenshotPath).toBe('screenshots/test.png')
    })

    it('截图 URL 应该正确拼接', () => {
      const wrapper = mount(ExecutionDetailPanel, {
        props: {
          execution: mockExecution
        }
      })

      wrapper.vm.handleViewScreenshot('screenshots/test.png')

      expect(wrapper.vm.screenshotUrl).toBe('/api/screenshots/screenshots/test.png')
    })

    it('点击查看错误应该显示对话框', async () => {
      const wrapper = mount(ExecutionDetailPanel, {
        props: {
          execution: mockExecution
        }
      })

      wrapper.vm.handleViewError('Error message')

      expect(wrapper.vm.errorDialogVisible).toBe(true)
      expect(wrapper.vm.currentErrorMessage).toBe('Error message')
    })
  })

  describe('对话框显示', () => {
    it('screenshotDialogVisible 为 true 应该显示对话框', () => {
      const wrapper = mount(ExecutionDetailPanel, {
        props: {
          execution: mockExecution
        }
      })

      wrapper.vm.screenshotDialogVisible = true

      expect(wrapper.find('.el-dialog').exists()).toBe(true)
    })

    it('screenshotDialogVisible 为 false 不应该显示对话框', () => {
      const wrapper = mount(ExecutionDetailPanel, {
        props: {
          execution: mockExecution
        }
      })

      wrapper.vm.screenshotDialogVisible = false

      expect(wrapper.find('.el-dialog').exists()).toBe(false)
    })
  })
})
