// 导入 defineConfig 用于定义 Vite 配置
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'

export default defineConfig({
  plugins: [
    vue(),
    AutoImport({
      imports: ['vue', 'vue-router', 'pinia'],
      resolvers: [ElementPlusResolver()],
      dts: 'src/auto-imports.d.ts',
    }),
    Components({
      resolvers: [ElementPlusResolver()],
      dts: 'src/components.d.ts',
    }),
  ],
  resolve: {
    alias: { '@': '/src' },
  },
  server: {
    port: 5173,
    host: '0.0.0.0',  // 监听所有网络接口
    open: false,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',  // 使用 IPv4 地址
        changeOrigin: true,
        // 启用 WebSocket 代理支持
        ws: true,
        configure: (proxy, _options) => {
          proxy.on('error', (err, _req, _res) => {
            console.log('proxy error', err);
          });
          proxy.on('proxyReq', (proxyReq, req, _res) => {
            console.log('Sending:', req.method, req.url, '->', proxyReq.getHeader('host'));
          });
          // WebSocket 升级请求日志
          proxy.on('upgrade', (req, socket, head) => {
            console.log('WebSocket upgrade:', req.url);
          });
        }
      },
    },
  },
  // Vitest 测试配置
  test: {
    // 使用 happy-dom 作为测试环境（比 jsdom 更快，功能更现代）
    environment: 'happy-dom',
    // 测试文件匹配模式
    include: ['src/**/*.{test,spec}.{js,ts,vue}', 'tests/**/*.{test,spec}.{js,ts,vue}'],
    // 排除的文件
    exclude: ['node_modules', 'dist', '.idea', '.git', '.cache'],
    // 全局配置文件
    setupFiles: ['./src/test-setup.ts'],
    // 覆盖率配置
    coverage: {
      // 覆盖率提供者
      provider: 'v8',
      // 报告格式
      reporter: ['text', 'json', 'html', 'lcov'],
      // 输出目录
      outputDir: 'coverage',
      // 排除的文件
      exclude: [
        'node_modules/',
        'src/main.ts',
        '**/*.d.ts',
        '**/*.config.*',
        '**/mockData',
        'src/auto-imports.d.ts',
        'src/components.d.ts',
      ],
    },
    // 模拟别名
    alias: {
      '@': '/src',
    },
    // CSS 模块处理（测试时不需要 CSS）
    css: {
      modules: {
        classNameStrategy: 'non-scoped'
      }
    },
    // 处理 .vue 文件
    transformMode: {
      ssr: [],
      web: [/.vue$/]
    }
  },
})
