/**
 * Vitest 测试全局设置文件
 * 用于配置全局 mock 和测试环境
 */
import { vi } from 'vitest'

// Mock 所有 CSS 文件导入（测试时不需要实际样式）
vi.mock('*.css', () => ({}))
vi.mock('*.scss', () => ({}))

// Mock Element Plus 样式
vi.mock('element-plus/dist/index.css', () => ({}))
vi.mock('element-plus/theme-chalk/base.css', () => ({}))
vi.mock('element-plus/theme-chalk/el-button.css', () => ({}))
vi.mock('element-plus/theme-chalk/el-input.css', () => ({}))
vi.mock('element-plus/theme-chalk/el-form.css', () => ({}))
vi.mock('element-plus/theme-chalk/el-select.css', () => ({}))
vi.mock('element-plus/theme-chalk/el-tag.css', () => ({}))
vi.mock('element-plus/theme-chalk/el-table.css', () => ({}))
vi.mock('element-plus/theme-chalk/el-dialog.css', () => ({}))
vi.mock('element-plus/theme-chalk/el-empty.css', () => ({}))

// Mock Element Plus 图标
vi.mock('@element-plus/icons-vue', () => ({
  Position: { template: '<span />' },
  Delete: { template: '<span />' },
  Document: { template: '<span />' },
  Picture: { template: '<span />' },
  Download: { template: '<span />' },
  View: { template: '<span />' },
  Close: { template: '<span />' },
  Plus: { template: '<span />' },
  CopyDocument: { template: '<span />' },
  Check: { template: '<span />' },
  Edit: { template: '<span />' },
  Search: { template: '<span />' },
  Refresh: { template: '<span />' },
  More: { template: '<span />' }
}))
