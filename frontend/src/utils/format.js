/** 展示层格式化工具。 */

const numberFormatter = new Intl.NumberFormat('zh-CN', { maximumFractionDigits: 2 })
const currencyFormatter = new Intl.NumberFormat('zh-CN', {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
})

export function formatNumber(value, fallback = '-') {
  if (value === null || value === undefined || value === '') return fallback
  const number = Number(value)
  return Number.isFinite(number) ? numberFormatter.format(number) : fallback
}

export function formatCurrency(value, fallback = '-') {
  if (value === null || value === undefined || value === '') return fallback
  const number = Number(value)
  return Number.isFinite(number) ? `¥ ${currencyFormatter.format(number)}` : fallback
}

export function formatArea(value) {
  return value === null || value === undefined ? '-' : `${formatNumber(value)} ㎡`
}

export function formatHours(value) {
  return value === null || value === undefined ? '-' : `${formatNumber(value)} h`
}

export function formatPercent(value) {
  const number = Number(value)
  return Number.isFinite(number) ? `${number.toFixed(1)}%` : '0.0%'
}

export function formatDate(value, fallback = '-') {
  return value ? String(value).slice(0, 10) : fallback
}

export function formatDateTime(value, fallback = '-') {
  return value ? String(value).slice(0, 16) : fallback
}

/** 返回最近 n 个月的区间，用于日期筛选默认值。 */
export function recentMonthRange(months = 6) {
  const end = new Date()
  const start = new Date(end.getFullYear(), end.getMonth() - (months - 1), 1)
  return [toIsoDate(start), toIsoDate(end)]
}

export function toIsoDate(date) {
  const year = date.getFullYear()
  const month = `${date.getMonth() + 1}`.padStart(2, '0')
  const day = `${date.getDate()}`.padStart(2, '0')
  return `${year}-${month}-${day}`
}

export function today() {
  return toIsoDate(new Date())
}
