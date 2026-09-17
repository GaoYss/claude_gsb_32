import { createResourceApi } from './client'
import http from './client'

export const plantReplacementApi = {
  ...createResourceApi('plant-replacements'),
  summary: (params) => http.get('/plant-replacements/summary', { params }),
}
