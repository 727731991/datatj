<template>
  <div class="report-container">
    <aside class="sidebar">
      <div class="logo">
        <h2>数据报表系统</h2>
      </div>
      <el-menu :default-active="activeMenu" class="sidebar-menu">
        <el-menu-item index="/">
          <template #icon><span class="icon">📊</span></template>
          仪表盘
        </el-menu-item>
        <el-menu-item index="/data">
          <template #icon><span class="icon">📁</span></template>
          数据管理
        </el-menu-item>
        <el-menu-item index="/reports">
          <template #icon><span class="icon">📈</span></template>
          报表中心
        </el-menu-item>
        <el-menu-item index="/users" v-if="user?.role === 'admin'">
          <template #icon><span class="icon">👥</span></template>
          用户管理
        </el-menu-item>
      </el-menu>
      <div class="logout-btn">
        <el-button type="text" @click="handleLogout">退出登录</el-button>
      </div>
    </aside>

    <main class="main-content">
      <header class="top-header">
        <div class="header-left">
          <h1>报表中心</h1>
        </div>
        <div class="user-info">
          <span>{{ user?.username }}</span>
        </div>
      </header>

      <div class="content-area">
        <div class="filter-panel">
          <div class="filter-row">
            <el-select
              v-model="filter.category"
              placeholder="选择分类"
              class="filter-select"
            >
              <el-option label="全部" value="" />
              <el-option v-for="cat in categories" :key="cat" :label="cat" :value="cat" />
            </el-select>
            <el-date-picker
              v-model="filter.startDate"
              type="date"
              placeholder="开始日期"
              class="date-picker"
            />
            <el-date-picker
              v-model="filter.endDate"
              type="date"
              placeholder="结束日期"
              class="date-picker"
            />
            <el-button type="primary" @click="generateReport">生成报表</el-button>
            <el-button @click="exportReport">
              <span>📤</span> 导出Excel
            </el-button>
          </div>
        </div>

        <div class="report-content" v-if="reportData">
          <div class="stats-row">
            <div class="stat-item">
              <div class="stat-num">{{ reportData.total_records }}</div>
              <div class="stat-text">数据记录总数</div>
            </div>
          </div>

          <div class="chart-section">
            <div ref="chartRef" class="chart"></div>
          </div>

          <div class="summary-section">
            <h3>分类汇总</h3>
            <el-table :data="summaryTableData" border>
              <el-table-column prop="category" label="分类" />
              <el-table-column prop="count" label="数量" />
              <el-table-column prop="total" label="合计" />
              <el-table-column prop="avg" label="平均值" />
            </el-table>
          </div>

          <div class="detail-section" v-if="expandedCategory">
            <h3>{{ expandedCategory }} - 明细数据</h3>
            <el-table :data="expandedItems" border>
              <el-table-column prop="title" label="标题" />
              <el-table-column prop="value" label="数值" />
              <el-table-column prop="unit" label="单位" />
              <el-table-column prop="date" label="日期" />
              <el-table-column prop="remark" label="备注" />
            </el-table>
          </div>
        </div>

        <div class="empty-state" v-else>
          <div class="empty-icon">📊</div>
          <p>请选择筛选条件并点击"生成报表"</p>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { dataAPI, reportAPI } from '@/utils/api'
import { getUser, logout } from '@/utils/auth'

const router = useRouter()
const route = useRoute()

const user = ref(getUser())
const activeMenu = computed(() => route.path)

const filter = reactive({
  category: '',
  startDate: '',
  endDate: ''
})

const categories = ref([])
const reportData = ref(null)
const chartRef = ref(null)
let chartInstance = null

const expandedCategory = ref('')

const summaryTableData = computed(() => {
  if (!reportData.value?.summary) return []
  
  return Object.entries(reportData.value.summary).map(([category, data]) => ({
    category,
    count: data.count,
    total: data.total,
    avg: (data.total / data.count).toFixed(2)
  }))
})

const expandedItems = computed(() => {
  if (!reportData.value?.summary || !expandedCategory.value) return []
  
  return reportData.value.summary[expandedCategory.value]?.items || []
})

const loadCategories = async () => {
  try {
    const response = await dataAPI.categories()
    categories.value = response.data
  } catch (error) {
    console.error('Failed to load categories:', error)
  }
}

const generateReport = async () => {
  try {
    const requestData = {
      category: filter.category || null,
      start_date: filter.startDate ? filter.startDate.toISOString().split('T')[0] : null,
      end_date: filter.endDate ? filter.endDate.toISOString().split('T')[0] : null
    }
    
    const response = await reportAPI.generate(requestData)
    reportData.value = response.data
    expandedCategory.value = ''
    renderChart()
  } catch (error) {
    ElMessage.error('生成报表失败')
    console.error('Failed to generate report:', error)
  }
}

const renderChart = () => {
  if (!chartRef.value || !reportData.value) return
  
  if (chartInstance) {
    chartInstance.dispose()
  }
  
  chartInstance = echarts.init(chartRef.value)
  
  const chartData = reportData.value.chart_data
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'horizontal',
      bottom: 10
    },
    series: [
      {
        name: '数据统计',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: true,
          formatter: '{b}\n{c}'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        data: chartData.categories.map((cat, index) => ({
          value: chartData.values[index],
          name: cat,
          itemStyle: {
            color: [
              '#667eea',
              '#764ba2',
              '#f093fb',
              '#f5576c',
              '#4facfe',
              '#00f2fe',
              '#43e97b',
              '#38f9d7'
            ][index % 8]
          }
        }))
      }
    ]
  }
  
  chartInstance.setOption(option)
}

const exportReport = async () => {
  if (!reportData.value) {
    ElMessage.warning('请先生成报表')
    return
  }
  
  try {
    const requestData = {
      category: filter.category || null,
      start_date: filter.startDate ? filter.startDate.toISOString().split('T')[0] : null,
      end_date: filter.endDate ? filter.endDate.toISOString().split('T')[0] : null
    }
    
    const response = await reportAPI.export(requestData)
    const blob = new Blob([response.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'report.xlsx'
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)
    
    ElMessage.success('导出成功')
  } catch (error) {
    ElMessage.error('导出失败')
  }
}

const toggleCategory = (category) => {
  expandedCategory.value = expandedCategory.value === category ? '' : category
}

const handleLogout = () => {
  logout()
  ElMessage.success('已退出登录')
  router.push('/login')
}

const handleResize = () => {
  chartInstance?.resize()
}

onMounted(() => {
  loadCategories()
  window.addEventListener('resize', handleResize)
})
</script>

<style scoped>
.report-container {
  display: flex;
  min-height: 100vh;
  background-color: #f0f2f5;
}

.sidebar {
  width: 250px;
  background: linear-gradient(180deg, #1f1c2c 0%, #928dab 100%);
  color: white;
  display: flex;
  flex-direction: column;
}

.logo {
  padding: 20px;
  text-align: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo h2 {
  font-size: 18px;
  margin: 0;
}

.sidebar-menu {
  flex: 1;
  border-right: none;
}

.sidebar-menu :deep(.el-menu-item) {
  color: rgba(255, 255, 255, 0.8);
  border-radius: 0;
}

.sidebar-menu :deep(.el-menu-item:hover) {
  background-color: rgba(255, 255, 255, 0.1);
}

.sidebar-menu :deep(.el-menu-item.is-active) {
  background-color: rgba(255, 255, 255, 0.2);
  color: white;
}

.icon {
  font-size: 18px;
  margin-right: 8px;
}

.logout-btn {
  padding: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.logout-btn :deep(.el-button) {
  color: rgba(255, 255, 255, 0.8);
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.top-header {
  height: 60px;
  background-color: white;
  padding: 0 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.header-left h1 {
  font-size: 20px;
  margin: 0;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.content-area {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.filter-panel {
  background: white;
  border-radius: 12px;
  padding: 15px 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.filter-row {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
  align-items: center;
}

.filter-select {
  width: 180px;
}

.date-picker {
  width: 180px;
}

.report-content {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.stats-row {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.stat-item {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  padding: 20px;
  color: white;
  min-width: 200px;
}

.stat-num {
  font-size: 32px;
  font-weight: bold;
}

.stat-text {
  font-size: 14px;
  opacity: 0.9;
}

.chart-section {
  margin-bottom: 20px;
}

.chart {
  height: 350px;
}

.summary-section,
.detail-section {
  margin-bottom: 20px;
}

.summary-section h3,
.detail-section h3 {
  margin: 0 0 15px 0;
  font-size: 16px;
  color: #303133;
}

.empty-state {
  background: white;
  border-radius: 12px;
  padding: 60px 20px;
  text-align: center;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 15px;
}

.empty-state p {
  color: #909399;
  font-size: 16px;
}
</style>
