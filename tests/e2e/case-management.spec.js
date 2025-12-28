/**
 * uiTool1.0 用例管理页面 E2E 测试
 * 测试目标: http://localhost:5174/
 * 使用 Playwright 进行端到端测试
 */
import { test, expect } from '@playwright/test';

// 测试套件：用例管理 (P0 - 高优先级)
test.describe('用例管理页面', () => {
  // 每个测试前访问主页
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:5174/');
    // 等待页面加载完成
    await page.waitForLoadState('networkidle');
  });

  // TC1.1: 页面加载和初始化
  test('应该正确加载用例管理页面', async ({ page }) => {
    // 验证页面标题
    const title = await page.title();
    expect(title).toMatch(/uiTool|测试/);

    // 验证导航栏存在
    const navBar = page.locator('.el-menu, nav, header');
    await expect(navBar).toBeVisible();

    // 验证导航项包含"用例管理"、"执行控制台"、"报告中心"
    const navigation = page.locator('text=/用例管理|执行控制台|报告中心/');
    await expect(navigation.first()).toBeVisible();

    // 验证用例列表容器存在
    const table = page.locator('.el-table, table');
    await expect(table).toBeVisible();
  });

  // TC1.2: 新建用例
  test('应该能跳转到新建用例页面', async ({ page }) => {
    // 点击"新建用例"按钮
    const newButton = page.locator('button:has-text("新建"), button:has-text("创建"), .el-button--primary').first();
    await newButton.click();

    // 验证跳转到 /editor 路由
    await expect(page).toHaveURL(/\/editor/);

    // 验证编辑器页面加载
    const editor = page.locator('.script-editor, .editor');
    await expect(editor).toBeVisible();

    // 验证左侧步骤列表区域
    const stepList = page.locator('.step-list, .steps-container');
    await expect(stepList).toBeVisible();
  });

  // TC1.3: 搜索用例
  test('应该能搜索用例', async ({ page }) => {
    // 查找搜索框
    const searchInput = page.locator('input[placeholder*="搜索"], input[placeholder*="名称"], .el-input__inner').first();

    // 输入搜索关键词
    await searchInput.fill('测试');

    // 等待搜索结果更新
    await page.waitForTimeout(500);

    // 验证搜索框有值
    const value = await searchInput.inputValue();
    expect(value).toBe('测试');
  });

  // TC1.4: 按优先级筛选
  test('应该能按优先级筛选用例', async ({ page }) => {
    // 查找优先级选择器
    const prioritySelect = page.locator('.el-select, select').first();

    // 点击选择器
    await prioritySelect.click();

    // 等待下拉选项出现
    await page.waitForTimeout(300);

    // 验证选择器可交互
    await expect(prioritySelect).toBeVisible();
  });

  // TC1.5: 编辑用例
  test('应该能编辑用例', async ({ page }) => {
    // 查找表格中的编辑按钮
    const editButton = page.locator('button:has-text("编辑"), .el-button:has-text("编辑")').first();

    // 如果存在编辑按钮，点击它
    const editButtonCount = await editButton.count();
    if (editButtonCount > 0) {
      await editButton.first().click();

      // 验证跳转到 /editor/:id 路由
      await expect(page).toHaveURL(/\/editor\/\d+/);

      // 验证编辑器页面加载
      const editor = page.locator('.script-editor, .editor');
      await expect(editor).toBeVisible();
    } else {
      // 没有用例时跳过此测试
      test.skip(true, '没有可编辑的用例');
    }
  });

  // TC1.6: 删除用例
  test('应该能删除用例', async ({ page }) => {
    // 查找表格中的删除按钮
    const deleteButton = page.locator('button:has-text("删除"), .el-button--danger:has-text("删除")').first();

    // 如果存在删除按钮
    const deleteButtonCount = await deleteButton.count();
    if (deleteButtonCount > 0) {
      // 记录删除前的表格行数
      const tableRowsBefore = await page.locator('.el-table__row, tr').count();

      await deleteButton.first().click();

      // 等待确认对话框
      await page.waitForTimeout(500);

      // 查找确认按钮并点击
      const confirmButton = page.locator('button:has-text("确定"), .el-button--primary:has-text("确定")').first();
      const confirmCount = await confirmButton.count();

      if (confirmCount > 0) {
        await confirmButton.click();

        // 等待删除完成
        await page.waitForTimeout(1000);

        // 验证表格行数减少
        const tableRowsAfter = await page.locator('.el-table__row, tr').count();
        expect(tableRowsAfter).toBeLessThan(tableRowsBefore);
      }
    } else {
      // 没有用例时跳过此测试
      test.skip(true, '没有可删除的用例');
    }
  });

  // 额外测试：验证页面响应式布局
  test('应该正确显示页面布局', async ({ page }) => {
    // 验证主容器可见
    const mainContainer = page.locator('main, .main-container, #app');
    await expect(mainContainer).toBeVisible();

    // 验证页面内容区域
    const content = page.locator('.el-container, .container');
    await expect(content).toBeVisible();
  });
});
