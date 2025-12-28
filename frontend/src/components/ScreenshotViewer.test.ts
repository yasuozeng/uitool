/**
 * ScreenshotViewer 组件测试
 * 测试截图查看器组件的功能
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import ScreenshotViewer from './ScreenshotViewer.vue'

// Mock Element Plus 组件
vi.mock('element-plus', () => ({
  ElButton: { template: '<button @click="$emit(&quot;click&quot;)"><slot /></button>' },
  ElIcon: { template: '<div><slot /></div>' },
  ElEmpty: { template: '<div>{{ description }}</div>' }
}))

// Mock window.open
const mockOpen = vi.fn()
Object.defineProperty(window, 'open', {
  value: mockOpen,
  writable: true
})

describe('ScreenshotViewer 组件', () => {
  describe('基础渲染', () => {
    it('无截图时应该显示空状态', () => {
      const wrapper = mount(ScreenshotViewer, {
        props: {
          screenshotPath: ''
        }
      })

      expect(wrapper.find('.no-screenshot').exists()).toBe(true)
      expect(wrapper.find('.screenshot-container').exists()).toBe(false)
      expect(wrapper.text()).toContain('暂无截图')
    })

    it('有截图时应该显示截图容器', () => {
      const wrapper = mount(ScreenshotViewer, {
        props: {
          screenshotPath: 'screenshots/test_error.png'
        }
      })

      expect(wrapper.find('.screenshot-container').exists()).toBe(true)
      expect(wrapper.find('.no-screenshot').exists()).toBe(false)
    })

    it('应该显示文件名', () => {
      const wrapper = mount(ScreenshotViewer, {
        props: {
          screenshotPath: 'screenshots/test_error.png'
        }
      })

      expect(wrapper.find('.filename').text()).toBe('test_error.png')
    })

    it('应该正确处理路径分隔符', () => {
      // 测试 Windows 风格路径
      const wrapper1 = mount(ScreenshotViewer, {
        props: {
          screenshotPath: 'screenshots\\subfolder\\test.png'
        }
      })
      expect(wrapper1.find('.filename').text()).toBe('test.png')

      // 测试 Unix 风格路径
      const wrapper2 = mount(ScreenshotViewer, {
        props: {
          screenshotPath: 'screenshots/subfolder/test.png'
        }
      })
      expect(wrapper2.find('.filename').text()).toBe('test.png')
    })

    it('应该生成正确的截图 URL', () => {
      const wrapper = mount(ScreenshotViewer, {
        props: {
          screenshotPath: 'screenshots/test.png'
        }
      })

      const img = wrapper.find('img')
      expect(img.attributes('src')).toBe('/api/screenshots/screenshots/test.png')
    })
  })

  describe('工具栏按钮', () => {
    beforeEach(() => {
      mockOpen.mockClear()
    })

    it('应该显示下载按钮', () => {
      const wrapper = mount(ScreenshotViewer, {
        props: {
          screenshotPath: 'screenshots/test.png'
        }
      })

      const buttons = wrapper.findAll('.el-button')
      const downloadBtn = buttons.find(btn => btn.text().includes('下载'))
      expect(downloadBtn).toBeDefined()
    })

    it('应该显示新窗口打开按钮', () => {
      const wrapper = mount(ScreenshotViewer, {
        props: {
          screenshotPath: 'screenshots/test.png'
        }
      })

      const buttons = wrapper.findAll('.el-button')
      const openBtn = buttons.find(btn => btn.text().includes('新窗口打开'))
      expect(openBtn).toBeDefined()
    })

    it('应该显示关闭按钮', () => {
      const wrapper = mount(ScreenshotViewer, {
        props: {
          screenshotPath: 'screenshots/test.png'
        }
      })

      const buttons = wrapper.findAll('.el-button')
      const closeBtn = buttons.find(btn => btn.text().includes('关闭'))
      expect(closeBtn).toBeDefined()
    })
  })

  describe('用户交互', () => {
    beforeEach(() => {
      mockOpen.mockClear()
      // 清除之前创建的 link 元素
      document.body.innerHTML = ''
    })

    it('点击下载按钮应该触发下载', async () => {
      const wrapper = mount(ScreenshotViewer, {
        props: {
          screenshotPath: 'screenshots/test.png'
        }
      })

      // Mock createElement 方法
      const mockLink = {
        href: '',
        download: '',
        click: vi.fn(),
        remove: vi.fn()
      }

      const createElementSpy = vi.spyOn(document, 'createElement').mockReturnValue(mockLink as any)
      const appendChildSpy = vi.spyOn(document.body, 'appendChild').mockReturnValue(mockLink as any)
      const removeChildSpy = vi.spyOn(document.body, 'removeChild').mockReturnValue(mockLink as any)

      const downloadBtn = wrapper.findAll('.el-button').find(btn => btn.text().includes('下载'))
      await downloadBtn!.trigger('click')

      expect(mockLink.href).toBe('/api/screenshots/screenshots/test.png')
      expect(mockLink.download).toBe('test.png')
      expect(mockLink.click).toHaveBeenCalled()
      expect(appendChildSpy).toHaveBeenCalled()
      expect(removeChildSpy).toHaveBeenCalled()

      createElementSpy.mockRestore()
      appendChildSpy.mockRestore()
      removeChildSpy.mockRestore()
    })

    it('点击新窗口打开应该打开新标签页', async () => {
      const wrapper = mount(ScreenshotViewer, {
        props: {
          screenshotPath: 'screenshots/test.png'
        }
      })

      const openBtn = wrapper.findAll('.el-button').find(btn => btn.text().includes('新窗口打开'))
      await openBtn!.trigger('click')

      expect(mockOpen).toHaveBeenCalledWith(
        '/api/screenshots/screenshots/test.png',
        '_blank'
      )
    })

    it('点击关闭按钮应该触发 close 事件', async () => {
      const wrapper = mount(ScreenshotViewer, {
        props: {
          screenshotPath: 'screenshots/test.png'
        }
      })

      const closeBtn = wrapper.findAll('.el-button').find(btn => btn.text().includes('关闭'))
      await closeBtn!.trigger('click')

      expect(wrapper.emitted('close')).toBeTruthy()
      expect(wrapper.emitted('close')?.length).toBe(1)
    })
  })

  describe('图片加载状态', () => {
    it('图片加载成功应该更新状态', async () => {
      const wrapper = mount(ScreenshotViewer, {
        props: {
          screenshotPath: 'screenshots/test.png'
        }
      })

      const img = wrapper.find('img')

      // 触发 load 事件
      await img.trigger('load')

      // 组件内部状态应该更新
      expect(wrapper.vm.error).toBe(false)
    })

    it('图片加载失败应该更新状态', async () => {
      const wrapper = mount(ScreenshotViewer, {
        props: {
          screenshotPath: 'screenshots/nonexistent.png'
        }
      })

      const img = wrapper.find('img')

      // 触发 error 事件
      await img.trigger('error')

      // 组件内部状态应该更新
      expect(wrapper.vm.error).toBe(true)
    })
  })

  describe('计算属性', () => {
    it('screenshotUrl 应该正确拼接路径', () => {
      const wrapper = mount(ScreenshotViewer, {
        props: {
          screenshotPath: 'path/to/screenshot.png'
        }
      })

      expect(wrapper.vm.screenshotUrl).toBe('/api/screenshots/path/to/screenshot.png')
    })

    it('空路径应该返回空字符串', () => {
      const wrapper = mount(ScreenshotViewer, {
        props: {
          screenshotPath: ''
        }
      })

      expect(wrapper.vm.screenshotUrl).toBe('')
    })

    it('fileName 应该正确提取文件名', () => {
      const testCases = [
        { path: 'screenshots/test.png', expected: 'test.png' },
        { path: 'screenshots/subfolder/error.png', expected: 'error.png' },
        { path: 'simple.png', expected: 'simple.png' },
        { path: 'a/b/c/d/file.jpg', expected: 'file.jpg' }
      ]

      testCases.forEach(({ path, expected }) => {
        const wrapper = mount(ScreenshotViewer, {
          props: {
            screenshotPath: path
          }
        })

        expect(wrapper.vm.fileName).toBe(expected)
      })
    })
  })
})
