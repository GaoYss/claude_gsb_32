import { createResourceApi } from './client'
import http from './client'

export const maintenanceTaskApi = {
  ...createResourceApi('maintenance-tasks'),
  changeStatus: (id, payload) => http.patch(`/maintenance-tasks/${id}/status`, payload),
}
