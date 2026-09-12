<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import * as echarts from 'echarts'

import request from '@/api/request'

type TaskStatus = 'todo' | 'doing' | 'done'

interface TaskItem {
  id: number
  status: TaskStatus
  created_at: string
}

const pieRef = ref<HTMLDivElement>()
const lineRef = ref<HTMLDivElement>()

let pieChart: echarts.ECharts | null = null
let lineChart: echarts.ECharts | null = null

const statusLabels: Record<TaskStatus, string> = {
  todo: '待办',
  doing: '进行中',
  done: '已完成',
}

const loading = ref(false)

function renderPie(tasks: TaskItem[]) {
  if (!pieRef.value) return
  const counts: Record<TaskStatus, number> = { todo: 0, doing: 0, done: 0 }
  tasks.forEach((task) => {
    if (counts[task.status] !== undefined) counts[task.status] += 1
  })

  const data = (Object.keys(counts) as TaskStatus[]).map((key) => ({
    name: statusLabels[key],
    value: counts[key],
  }))

  pieChart = echarts.init(pieRef.value)
  pieChart.setOption({
    title: { text: '任务状态分布', left: 'center' },
    tooltip: { trigger: 'item' },
    legend: { bottom: 0 },
    series: [
      {
        name: '任务状态',
        type: 'pie',
        radius: '55%',
        center: ['50%', '50%'],
        data,
        emphasis: {
          itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0, 0, 0, 0.3)' },
        },
      },
    ],
  })
}

function renderLine(tasks: TaskItem[]) {
  if (!lineRef.value) return

  const days: string[] = []
  const counters: Record<string, number> = {}
  for (let i = 6; i >= 0; i -= 1) {
    const d = new Date()
    d.setHours(0, 0, 0, 0)
    d.setDate(d.getDate() - i)
    const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(
      d.getDate(),
    ).padStart(2, '0')}`
    days.push(key)
    counters[key] = 0
  }

  tasks.forEach((task) => {
    const key = new Date(task.created_at).toLocaleDateString('sv-SE')
    if (key in counters) counters[key] += 1
  })

  lineChart = echarts.init(lineRef.value)
  lineChart.setOption({
    title: { text: '最近 7 天新建任务', left: 'center' },
    tooltip: { trigger: 'axis' },
    grid: { left: 40, right: 20, top: 60, bottom: 40 },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: days.map((d) => d.slice(5)),
    },
    yAxis: { type: 'value', minInterval: 1 },
    series: [
      {
        name: '新建任务',
        type: 'line',
        smooth: true,
        areaStyle: {},
        data: days.map((d) => counters[d]),
      },
    ],
  })
}

function resizeCharts() {
  pieChart?.resize()
  lineChart?.resize()
}

async function loadDashboard() {
  loading.value = true
  try {
    const { data } = await request.get<{ data: TaskItem[]; total: number }>('/tasks', {
      params: { skip: 0, limit: 100 },
    })
    renderPie(data.data)
    renderLine(data.data)
  } catch {
    // surfaced by the axios response interceptor
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadDashboard()
  window.addEventListener('resize', resizeCharts)
})

onUnmounted(() => {
  window.removeEventListener('resize', resizeCharts)
  pieChart?.dispose()
  lineChart?.dispose()
  pieChart = null
  lineChart = null
})
</script>

<template>
  <div v-loading="loading" class="dashboard-view">
    <el-row :gutter="16">
      <el-col :xs="24" :md="12">
        <el-card>
          <div ref="pieRef" class="chart"></div>
        </el-card>
      </el-col>
      <el-col :xs="24" :md="12">
        <el-card>
          <div ref="lineRef" class="chart"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
.dashboard-view {
  min-height: 200px;
}

.chart {
  width: 100%;
  height: 360px;
}
</style>
