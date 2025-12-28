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
  background: #f5f5f5;

  .app-header {
    background: white;
    border-bottom: 1px solid #e8e8e8;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    position: sticky;
    top: 0;
    z-index: 100;

    .header-content {
      max-width: 1600px;
      margin: 0 auto;
      padding: 0 20px;
      height: 60px;
      display: flex;
      align-items: center;
      justify-content: space-between;

      .logo {
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 20px;
        font-weight: 500;
        color: #1890ff;

        .el-icon {
          font-size: 24px;
        }
      }

      .nav-menu {
        display: flex;
        gap: 8px;

        .nav-item {
          display: flex;
          align-items: center;
          gap: 6px;
          padding: 8px 16px;
          border-radius: 4px;
          color: #666;
          text-decoration: none;
          transition: all 0.2s;

          &:hover {
            background: #f5f5f5;
            color: #1890ff;
          }

          &.router-link-active {
            background: #e6f7ff;
            color: #1890ff;
          }
        }
      }
    }
  }

  .app-main {
    min-height: calc(100vh - 60px);
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
