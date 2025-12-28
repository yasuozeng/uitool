<script setup lang="ts">
// 主应用组件
</script>

<template>
  <div class="app">
    <!-- 顶部导航栏 -->
    <header class="app-header">
      <div class="header-content">
        <div class="logo">
          <el-icon><Monitor /></el-icon>
          <span>uiTool1.0</span>
        </div>
        <nav class="nav-menu">
          <router-link to="/" class="nav-item">
            <el-icon><Document /></el-icon>
            用例管理
          </router-link>
          <router-link to="/execution" class="nav-item">
            <el-icon><VideoPlay /></el-icon>
            执行控制台
          </router-link>
          <router-link to="/reports" class="nav-item">
            <el-icon><DataAnalysis /></el-icon>
            报告中心
          </router-link>
        </nav>
      </div>
    </header>

    <!-- 主内容区域 -->
    <main class="app-main">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<style scoped lang="scss">
.app {
  min-height: 100vh;
  background: #f0f2f5;

  .app-header {
    background: white;
    border-bottom: 1px solid #f0f0f0;
    box-shadow: 0 1px 6px rgba(0, 0, 0, 0.04);
    position: sticky;
    top: 0;
    z-index: 100;

    .header-content {
      max-width: 1600px;
      margin: 0 auto;
      padding: 0 24px;
      height: 64px; // 从 60px 增加到 64px
      display: flex;
      align-items: center;
      justify-content: space-between;

      .logo {
        display: flex;
        align-items: center;
        gap: 12px;
        font-size: 22px;
        font-weight: 600; // 从 500 增加到 600
        color: #1677ff; // 更新为新的主色

        .el-icon {
          font-size: 26px; // 从 24px 增加
        }
      }

      .nav-menu {
        display: flex;
        gap: 4px;

        .nav-item {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 8px 18px; // 增加内边距
          border-radius: 6px; // 从 4px 增加到 6px
          color: #595959; // 更新文本色
          text-decoration: none;
          font-weight: 500;
          transition: all 0.2s;
          position: relative;

          &:hover {
            background: #f5f5f5;
            color: #1677ff;
          }

          &.router-link-active {
            background: #e6f4ff; // 更新为新的浅蓝背景
            color: #1677ff;

            // 底部指示器
            &::after {
              content: '';
              position: absolute;
              bottom: -20px; // 调整位置到导航栏底部
              left: 50%;
              transform: translateX(-50%);
              width: 20px;
              height: 2px;
              background: #1677ff;
              border-radius: 2px 2px 0 0;
            }
          }
        }
      }
    }
  }

  .app-main {
    min-height: calc(100vh - 64px); // 从 60px 更新为 64px
  }
}

// 路由过渡动画
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
