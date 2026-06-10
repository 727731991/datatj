<template>
  <div class="data-container">
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
          <h1>数据管理</h1>
        </div>
        <div class="user-info">
          <span>{{ user?.username }}</span>
        </div>
      </header>

      <div class="content-area">
        <div class="toolbar">
          <div class="search-area">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索标题"
              class="search-input"
              @keyup.enter="handleSearch"
            />
            <el-select
              v-model="filterCategory"
              placeholder="选择分类"
              class="category-select"
            >
              <el-option label="全部" value="" />
              <el-option v-for="cat in categories" :key="cat" :label="cat" :value="cat" />
            </el-select>
            <el-date-picker
              v-model="filterDate"
              type="date"
              placeholder="选择日期"
              class="date-picker"
            />
            <el-button type="primary" @click="handleSearch">搜索</el-button>
            <el-button @click="resetFilters">重置</el-button>
          </div>
          <div class="action-area">
            <el-button type="primary" @click="handleImport">
              <span>📥</span> 导入数据
            </el-button>
            <el-button type="success" @click="handleExport">
              <span>📤</span> 导出数据
            </el-button>
            <el-button type="primary" @click="goToAdd">
              <span>➕</span> 新增记录
            </el-button>
          </div>
        </div>

        <div class="table-container">
          <el-table :data="tableData" border class="data-table">
            <el-table-column prop="id" label="ID" width="60" />
            <el-table-column prop="category" label="分类" width="120" />
            <el-table-column prop="title" label="标题" />
            <el-table-column prop="value" label="数值" width="100" />
            <el-table-column prop="unit" label="单位" width="80" />
            <el-table-column prop="date" label="日期" width="120" />
            <el-table-column prop="remark" label="备注" />
            <el-table-column label="操作" width="160">
              <template #default="scope">
                <el-button
                  size="small"
                  @click="handleEdit(scope.row.id)"
                >编辑</el-button>
                <el-button
                  size="small"
                  type="danger"
                  @click="handleDelete(scope.row.id, scope.row.title)"
                >删除</el-button>
              </template>
            </el-table-column>
          </el-table>
          
          <el-pagination
            :current-page="currentPage"
            :page-size="pageSize"
            :total="total"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
            layout="total, sizes, prev, pager, next, jumper"
          />
        </div>
      </div>
    </main>

    <el-dialog title="导入数据" v-model="showImport" width="500px">
      <el-upload
        ref="uploadRef"
        class="upload-demo"
        :auto-upload="false"
        :on-change="handleFileChange"
        accept=".csv,.xlsx,.xls"
      >
        <el-button type="primary">选择文件</el-button>
        <template #tip>
          <div class="el-upload__tip">只能上传CSV、Excel文件</div>
        </template>
      </el-upload>
      <template #footer>
        <el-button @click="showImport = false">取消</el-button>
        <el-button type="primary" @click="submitImport" :loading="importLoading">导入</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { dataAPI } from '@/utils/api'
import { getUser, logout } from '@/utils/auth'

const router = useRouter()
const route = useRoute()

const user = ref(getUser())
const activeMenu = computed(() => route.path)

const tableData = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const searchKeyword = ref('')
const filterCategory = ref('')
const filterDate = ref('')

const categories = ref([])

const showImport = ref(false)
const uploadRef = ref(null)
const importFile = ref(null)
const importLoading = ref(false)

const loadData = async () => {
  try {
    const params = {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value
    }
    if (searchKeyword.value) {
      params.title = searchKeyword.value
    }
    if (filterCategory.value) {
      params.category = filterCategory.value
    }
    if (filterDate.value) {
      params.date = filterDate.value
    }
    
    const response = await dataAPI.list(params)
    tableData.value = response.data
    total.value = response.data.length > 0 ? 100 : 0
  } catch (error) {
    ElMessage.error('加载数据失败')
    console.error('Failed to load data:', error)
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

const handleSearch = () => {
  currentPage.value = 1
  loadData()
}

const resetFilters = () => {
  searchKeyword.value = ''
  filterCategory.value = ''
  filterDate.value = ''
  currentPage.value = 1
  loadData()
}

const handleEdit = (id) => {
  router.push(`/data/edit/${id}`)
}

const handleDelete = async (id, title) => {
  try {
    await ElMessage.confirm(`确定要删除"${title}"吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await dataAPI.delete(id)
    ElMessage.success('删除成功')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const goToAdd = () => {
  router.push('/data/add')
}

const handleImport = () => {
  showImport.value = true
}

const handleFileChange = (file) => {
  importFile.value = file.raw
}

const submitImport = async () => {
  if (!importFile.value) {
    ElMessage.warning('请选择要导入的文件')
    return
  }
  
  importLoading.value = true
  
  const formData = new FormData()
  formData.append('file', importFile.value)
  
  try {
    await dataAPI.import(formData)
    ElMessage.success('导入成功')
    showImport.value = false
    importFile.value = null
    uploadRef.value?.clearFiles()
    loadData()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '导入失败')
  } finally {
    importLoading.value = false
  }
}

const handleExport = async () => {
  try {
    const params = {}
    if (filterCategory.value) {
      params.category = filterCategory.value
    }
    if (filterDate.value) {
      params.date = filterDate.value
    }
    
    const response = await dataAPI.export(params)
    const blob = new Blob([response.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'data_export.xlsx'
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)
    
    ElMessage.success('导出成功')
  } catch (error) {
    ElMessage.error('导出失败')
  }
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  loadData()
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  loadData()
}

const handleLogout = () => {
  logout()
  ElMessage.success('已退出登录')
  router.push('/login')
}

onMounted(() => {
  loadData()
  loadCategories()
})
</script>

<style scoped>
.data-container {
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

.toolbar {
  background: white;
  border-radius: 12px;
  padding: 15px 20px;
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 15px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.search-area {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  align-items: center;
}

.search-input {
  width: 200px;
}

.category-select {
  width: 150px;
}

.date-picker {
  width: 180px;
}

.action-area {
  display: flex;
  gap: 10px;
}

.table-container {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.data-table {
  width: 100%;
  margin-bottom: 20px;
}

:deep(.el-pagination) {
  text-align: right;
}
</style>
