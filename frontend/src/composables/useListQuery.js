import { onMounted, reactive, ref } from 'vue'

/**
 * 列表页通用逻辑：分页 + 筛选条件 + 加载状态 + 汇总信息。
 *
 * @param {(params: object) => Promise<object>} fetcher 调用后端列表接口的方法
 */
export function useListQuery(fetcher, { initialFilters = {}, pageSize = 10, immediate = true } = {}) {
  const defaults = { ...initialFilters }
  const filters = reactive({ ...defaults })
  const meta = reactive({ page: 1, page_size: pageSize, total: 0, pages: 0 })
  const items = ref([])
  const summary = ref(null)
  const loading = ref(false)

  function buildParams() {
    const params = { page: meta.page, page_size: meta.page_size }
    Object.entries(filters).forEach(([key, value]) => {
      if (value === null || value === undefined || value === '') return
      if (Array.isArray(value)) {
        if (value.length === 0) return
        params[key] = value.join(',')
        return
      }
      params[key] = value
    })
    return params
  }

  async function load() {
    loading.value = true
    try {
      const data = await fetcher(buildParams())
      items.value = data?.items ?? []
      summary.value = data?.summary ?? null
      if (data?.meta) Object.assign(meta, data.meta)
    } catch {
      items.value = []
      summary.value = null
    } finally {
      loading.value = false
    }
  }

  function search() {
    meta.page = 1
    return load()
  }

  function resetFilters() {
    Object.keys(filters).forEach((key) => {
      if (key in defaults) return
      delete filters[key]
    })
    Object.assign(filters, defaults)
    return search()
  }

  function handlePageChange(page) {
    meta.page = page
    return load()
  }

  function handleSizeChange(size) {
    meta.page_size = size
    meta.page = 1
    return load()
  }

  if (immediate) onMounted(load)

  return {
    filters,
    meta,
    items,
    summary,
    loading,
    load,
    search,
    resetFilters,
    handlePageChange,
    handleSizeChange,
  }
}
