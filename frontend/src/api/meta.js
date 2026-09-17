import http from './client'

export const metaApi = {
  getEnums: () => http.get('/meta/enums'),
  health: () => http.get('/meta/health'),
}
