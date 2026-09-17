import axios from 'axios'
import { ElMessage } from 'element-plus'

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1'

/** 统一的后端业务异常：字段错误在 details 中，供表单逐项展示。 */
export class ApiError extends Error {
  constructor(message, { code = 0, status = 0, details = null } = {}) {
    super(message)
    this.name = 'ApiError'
    this.code = code
    this.status = status
    this.details = details && typeof details === 'object' ? details : {}
  }
}

const http = axios.create({
  baseURL: API_BASE_URL,
  timeout: 20000,
  headers: { 'Content-Type': 'application/json' },
})

function toApiError(body, status) {
  return new ApiError(body?.message || '请求失败，请稍后重试', {
    code: body?.code ?? 0,
    status,
    details: body?.data,
  })
}

http.interceptors.response.use(
  (response) => {
    const body = response.data
    if (body && typeof body === 'object' && 'success' in body) {
      if (body.success) return body.data
      const error = toApiError(body, response.status)
      ElMessage.error(error.message)
      return Promise.reject(error)
    }
    return body
  },
  (error) => {
    const status = error.response?.status ?? 0
    const apiError = toApiError(error.response?.data, status)
    // 422 由表单逐字段提示，避免重复弹出
    if (status !== 422) {
      ElMessage.error(apiError.message)
    }
    return Promise.reject(apiError)
  },
)

/** 生成标准的 REST 资源方法：列表、详情、新增、修改、删除。 */
export function createResourceApi(resource) {
  return {
    list: (params) => http.get(`/${resource}`, { params }),
    detail: (id) => http.get(`/${resource}/${id}`),
    create: (payload) => http.post(`/${resource}`, payload),
    update: (id, payload) => http.put(`/${resource}/${id}`, payload),
    remove: (id, params) => http.delete(`/${resource}/${id}`, { params }),
  }
}

export default http
