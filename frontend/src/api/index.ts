/**
 * Axios HTTP 客户端配置
 * 统一配置 baseURL、请求/响应拦截器
 */
import axios from 'axios'
import type { AxiosError, InternalAxiosRequestConfig, AxiosResponse } from 'axios'

// 创建 axios 实例
const request = axios.create({
  baseURL: '/api/v1',
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
request.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // 可以在这里添加 token 等认证信息
    // const token = localStorage.getItem('token')
    // if (token && config.headers) {
    //   config.headers.Authorization = `Bearer ${token}`
    // }
    return config
  },
  (error: AxiosError) => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response: AxiosResponse) => {
    // 后端返回格式: { code: number, message: string, data: any }
    return response.data
  },
  (error: AxiosError) => {
    // 处理错误响应
    if (error.response) {
      const status = error.response.status
      const data = error.response.data as any

      switch (status) {
        case 400:
          console.error('请求参数错误:', data?.detail || '参数错误')
          break
        case 404:
          console.error('资源不存在:', data?.detail || '未找到')
          break
        case 500:
          console.error('服务器错误:', data?.detail || '内部错误')
          break
        default:
          console.error('请求失败:', data?.detail || error.message)
      }
    } else if (error.request) {
      console.error('网络错误: 服务器无响应')
    } else {
      console.error('请求配置错误:', error.message)
    }

    return Promise.reject(error)
  }
)

export default request
