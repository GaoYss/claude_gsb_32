import http from './client'

export const statisticsApi = {
  dashboard: (params) => http.get('/statistics/dashboard', { params }),
  overview: () => http.get('/statistics/overview'),
  distributions: () => http.get('/statistics/distributions'),
  trends: (params) => http.get('/statistics/trends', { params }),
  ranking: (params) => http.get('/statistics/ranking', { params }),
  reminders: () => http.get('/statistics/reminders'),
}
