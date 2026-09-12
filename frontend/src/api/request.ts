import axios, {
  type AxiosError,
  type AxiosInstance,
  type AxiosResponse,
  type InternalAxiosRequestConfig,
} from 'axios'
import { ElMessage } from 'element-plus'

declare module 'axios' {
  export interface AxiosRequestConfig {
    silent?: boolean
  }
}

const request: AxiosInstance = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

request.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error),
)

function resolveErrorMessage(error: AxiosError): string {
  const response = error.response

  if (!response) {
    if (error.code === 'ECONNABORTED') return '请求超时，请稍后重试'
    return '网络异常，请检查网络连接'
  }

  const data = response.data as { detail?: string } | undefined
  if (data?.detail) {
    return typeof data.detail === 'string' ? data.detail : '请求参数校验失败'
  }

  const statusMap: Record<number, string> = {
    400: '请求参数有误',
    401: '登录已过期，请重新登录',
    403: '没有权限执行该操作',
    404: '请求的资源不存在',
    422: '提交的数据格式不正确',
    500: '服务器内部错误',
  }
  return statusMap[response.status] ?? `请求失败（${response.status}）`
}

request.interceptors.response.use(
  (response: AxiosResponse) => {
    const method = (response.config.method ?? 'get').toLowerCase()
    const isMutation = ['post', 'put', 'patch', 'delete'].includes(method)
    if (isMutation && !response.config.silent) {
      ElMessage.success('操作成功')
    }
    return response
  },
  (error: AxiosError) => {
    const status = error.response?.status
    const url = error.config?.url ?? ''
    const isLoginRequest = url.includes('/login')

    if (status === 401 && !isLoginRequest) {
      localStorage.removeItem('token')
      window.location.href = '/login'
      return Promise.reject(error)
    }

    if (!error.config?.silent) {
      ElMessage.error(resolveErrorMessage(error))
    }
    return Promise.reject(error)
  },
)

export default request
