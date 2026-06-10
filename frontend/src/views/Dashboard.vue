<template>
  <div class="dashboard-container">
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
        <div class="user-info">
          <span>{{ user?.username }}</span>
          <span class="role" v-if="user?.role === 'admin'">管理员</span>
        </div>
      </header>

      <div class="content-area">
        <div class="stats-cards">
          <div class="stat-card">
            <div class="stat-icon">📊</div>
            <div class="stat-info">
              <div class="stat-value">{{ summary.total_count }}</div>
              <div class="stat-label">数据记录数</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">💰</div>
            <div class="stat-info">
              <div class="stat-value">{{ summary.total_value }}</div>
              <div class="stat-label">数值合计</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">📈</div>
            <div class="stat-info">
              <div class="stat-value">{{ summary.avg_value }}</div>
              <div class="stat-label">平均值</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">📁</div>
            <div class="stat-info">
              <div class="stat-value">{{ categories.length }}</div>
              <div class="stat-label">分类数量</div>
            </div>
          </div>
        </div>

        <div class="charts-section">
          <div class="chart-card">
            <h3>数据分类统计</h3>
            <div ref="chartRef" class="chart"></div>
          </div>
        </div>

        <div class="quick-actions">
          <h3>快捷操作</h3>
          <div class="action-buttons">
            <el-button type="primary" @click="goTo('/data/add')">
              <span class="btn-icon">➕</span>
              录入数据
            </el-button>
            <el-button @click="goTo('/data')">
              <span class="btn-icon">📋</span>
              查看数据
            </el-button>
            <el-button @click="goTo('/reports')">
              <span class="btn-icon">📊</span>
              生成报表
            </el-button>
          </div>
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
const chartRef = ref(null)
let chartInstance = null

const summary = reactive({
  total_count: 0,
  total_value: 0,
  avg_value: 0
})

const categories = ref([])
const chartData = reactive({
  categories: [],
  values: []
})

const activeMenu = computed(() => route.path)

const loadSummary = async () => {
  try {
    const response = await dataAPI.summary()
    summary.total_count = response.data.total_count
    summary.total_value = response.data.total_value
    summary.avg_value = response.data.avg_value
  } catch (error) {
    console.error('Failed to load summary:', error)
  }
}

const loadCategories = async () => {
  try {
    const response = await dataAPI.categories()
    categories.value = response.data
  } catch (error) {
    console.error('Failed to load categories:', error)
  }
}

const loadChartData = async () => {
  try {
    const response = await reportAPI.generate({})
    chartData.categories = response.data.chart_data.categories
    chartData.values = response.data.chart_data.values
    renderChart()
  } catch (error) {
    console.error('Failed to load chart data:', error)
  }
}

const renderChart = () => {
  if (!chartRef.value) return
  
  if (chartInstance) {
    chartInstance.dispose()
  }
  
  chartInstance = echarts.init(chartRef.value)
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: chartData.categories,
      axisLabel: {
        rotate: 30,
        fontSize: 12
      }
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '数值',
        type: 'bar',
        data: chartData.values,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#667eea' },
            { offset: 1, color: '#764ba2' }
          ]),
          borderRadius: [4, 4, 0, 0]
        },
        emphasis: {
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#764ba2' },
              { offset: 1, color: '#667eea' }
            ])
          }
        }
      }
    ]
  }
  
  chartInstance.setOption(option)
}

const handleLogout = () => {
  logout()
  ElMessage.success('已退出登录')
  router.push('/login')
}

const goTo = (path) => {
  router.push(path)
}

const handleResize = () => {
  chartInstance?.resize()
}

onMounted(() => {
  loadSummary()
  loadCategories()
  loadChartData()
  window.addEventListener('resize', handleResize)
})
</script>

<style scoped>
.dashboard-container {
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
  justify-content: flex-end;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.role {
  background-color: #409eff;
  color: white;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
}

.content-area {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 15px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.charts-section {
  margin-bottom: 20px;
}

.chart-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.chart-card h3 {
  margin: 0 0 15px 0;
  font-size: 16px;
  color: #303133;
}

.chart {
  height: 350px;
}

.quick-actions {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.quick-actions h3 {
  margin: 0 0 15px 0;
  font-size: 16px;
  color: #303133;
}

.action-buttons {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.btn-icon {
  margin-right: 5px;
}
</style>
