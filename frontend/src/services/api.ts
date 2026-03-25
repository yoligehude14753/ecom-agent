import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
})

export const productResearchApi = {
  getCategories: () => api.get('/product-research/categories').then(r => r.data),
  runResearch: (params: { category: string; limit?: number; min_score?: number }) =>
    api.post('/product-research/research', params).then(r => r.data),
  scoreAsin: (asin: string) => api.get(`/product-research/score/${asin}`).then(r => r.data),
}

export const listingApi = {
  generate: (params: { keyword: string; product_details?: object; language?: string }) =>
    api.post('/listing/generate', params).then(r => r.data),
  optimize: (params: { asin: string; language?: string }) =>
    api.post('/listing/optimize', params).then(r => r.data),
  getLanguages: () => api.get('/listing/languages').then(r => r.data),
}

export const reviewsApi = {
  analyze: (params: { asin: string; max_pages?: number }) =>
    api.post('/reviews/analyze', params).then(r => r.data),
}

export const monitorApi = {
  list: () => api.get('/monitor/list').then(r => r.data),
  add: (params: { asin: string; label?: string; alert_rules?: object }) =>
    api.post('/monitor/add', params).then(r => r.data),
  remove: (asin: string) => api.delete(`/monitor/remove/${asin}`).then(r => r.data),
  snapshots: (asin: string, limit?: number) =>
    api.get(`/monitor/snapshots/${asin}`, { params: { limit } }).then(r => r.data),
  snapshot: (asin: string) => api.post(`/monitor/snapshot/${asin}`).then(r => r.data),
}

export const adsApi = {
  optimize: (params?: { target_acos?: number }) =>
    api.post('/ads/optimize', null, { params }).then(r => r.data),
}

export default api
