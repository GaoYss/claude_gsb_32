import { createResourceApi } from './client'
import http from './client'

export const maintenanceRecordApi = {
  ...createResourceApi('maintenance-records'),
  summary: (params) => http.get('/maintenance-records/summary', { params }),
}
