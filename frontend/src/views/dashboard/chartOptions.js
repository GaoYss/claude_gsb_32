/** 看板图表配置：只做 echarts option 组装，数据由视图映射后传入。 */

export const PALETTE = [
  '#2f855a',
  '#48a17a',
  '#e6a23c',
  '#7ebb9c',
  '#f0a020',
  '#a9d4bd',
  '#909399',
  '#c0653b',
]

const AXIS_LABEL = { color: '#606266', fontSize: 12 }
const SPLIT_LINE = { lineStyle: { color: '#eef2ef' } }

export function pieOption(data, { unit = '', center = ['50%', '46%'] } = {}) {
  return {
    color: PALETTE,
    tooltip: {
      trigger: 'item',
      formatter: (params) => `${params.name}<br/>${params.value} ${unit}（${params.percent}%）`,
    },
    legend: {
      bottom: 0,
      icon: 'circle',
      itemWidth: 8,
      itemHeight: 8,
      textStyle: { fontSize: 12, color: '#606266' },
    },
    series: [
      {
        type: 'pie',
        radius: ['45%', '70%'],
        center,
        itemStyle: { borderColor: '#fff', borderWidth: 2 },
        label: { formatter: '{b}\n{c}', fontSize: 12, color: '#606266', lineHeight: 16 },
        labelLine: { length: 6, length2: 6 },
        avoidLabelOverlap: true,
        data,
      },
    ],
  }
}

export function barOption(data, { unit = '', horizontal = false, color = '#48a17a' } = {}) {
  const category = {
    type: 'category',
    data: data.map((item) => item.name),
    axisLabel: { ...AXIS_LABEL, interval: 0, rotate: !horizontal && data.length > 5 ? 18 : 0 },
  }
  const value = {
    type: 'value',
    name: unit,
    nameTextStyle: { color: '#909399', fontSize: 12 },
    axisLabel: { color: '#909399', fontSize: 12 },
    splitLine: SPLIT_LINE,
  }
  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      valueFormatter: (value) => `${value} ${unit}`,
    },
    grid: { left: 8, right: 20, top: 28, bottom: 4, containLabel: true },
    xAxis: horizontal ? value : category,
    yAxis: horizontal ? category : value,
    series: [
      {
        type: 'bar',
        barMaxWidth: 26,
        itemStyle: { color, borderRadius: horizontal ? [0, 4, 4, 0] : [4, 4, 0, 0] },
        data: data.map((item) => item.value),
      },
    ],
  }
}

/** 近几个月养护记录与工时趋势：柱状 + 折线双轴。 */
export function trendOption(rows) {
  return {
    color: ['#48a17a', '#e6a23c'],
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: {
      bottom: 0,
      icon: 'circle',
      itemWidth: 8,
      itemHeight: 8,
      textStyle: { fontSize: 12, color: '#606266' },
    },
    grid: { left: 8, right: 12, top: 30, bottom: 34, containLabel: true },
    xAxis: { type: 'category', data: rows.map((row) => row.month), axisLabel: AXIS_LABEL },
    yAxis: [
      {
        type: 'value',
        name: '养护记录(条)',
        nameTextStyle: { color: '#909399', fontSize: 12 },
        axisLabel: { color: '#909399', fontSize: 12 },
        splitLine: SPLIT_LINE,
      },
      {
        type: 'value',
        name: '工时(h)',
        nameTextStyle: { color: '#909399', fontSize: 12 },
        axisLabel: { color: '#909399', fontSize: 12 },
        splitLine: { show: false },
      },
    ],
    series: [
      {
        name: '养护记录',
        type: 'bar',
        barMaxWidth: 24,
        itemStyle: { borderRadius: [4, 4, 0, 0] },
        data: rows.map((row) => row.record_count),
      },
      {
        name: '养护工时',
        type: 'line',
        smooth: true,
        symbolSize: 6,
        yAxisIndex: 1,
        data: rows.map((row) => row.work_hours),
      },
    ],
  }
}
