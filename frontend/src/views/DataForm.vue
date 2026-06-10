<template>
  <div class="form-container">
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
          <el-button type="text" @click="goBack">← 返回</el-button>
          <h1>{{ isEdit ? '编辑数据' : '新增数据' }}</h1>
        </div>
        <div class="user-info">
          <span>{{ user?.username }}</span>
        </div>
      </header>

      <div class="content-area">
        <div class="form-card">
          <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
            <el-form-item label="分类" prop="category">
              <el-select v-model="form.category" placeholder="请选择分类">
                <el-option v-for="cat in categories" :key="cat" :label="cat" :value="cat" />
                <el-option label="其他" value="其他" />
              </el-select>
              <el-button type="text" size="small" @click="showAddCategory = true">+ 添加分类</el-button>
            </el-form-item>

            <el-form-item label="标题" prop="title">
              <el-input v-model="form.title" placeholder="请输入标题" />
            </el-form-item>

            <el-form-item label="数值" prop="value">
              <el-input v-model.number="form.value" type="number" placeholder="请输入数值" />
            </el-form-item>

            <el-form-item label="单位">
              <el-input v-model="form.unit" placeholder="请输入单位（可选）" />
            </el-form-item>

            <el-form-item label="日期" prop="date">
              <el-date-picker v-model="form.date" type="date" placeholder="请选择日期" />
            </el-form-item>

            <el-form-item label="备注">
              <el-textarea v-model="form.remark" rows="3" placeholder="请输入备注（可选）" />
            </el-form-item>

            <el-form-item class="form-actions">
              <el-button type="primary" @click="handleSubmit" :loading="submitting">
                {{ isEdit ? '保存修改' : '提交数据' }}
              </el-button>
              <el-button @click="goBack">取消</el-button>
            </el-form-item>
          </el-form>
        </div>
      </div>
    </main>

    <el-dialog title="添加分类" v-model="showAddCategory" width="400px">
      <el-input v-model="newCategory" placeholder="请输入新分类名称" />
      <template #footer>
        <el-button @click="showAddCategory = false">取消</el-button>
        <el-button type="primary" @click="addCategory">添加</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { dataAPI } from '@/utils/api'
import { getUser, logout } from '@/utils/auth'

const router = useRouter()
const route = useRoute()

const user = ref(getUser())
const formRef = ref(null)
const submitting = ref(false)
const showAddCategory = ref(false)
const newCategory = ref('')

const isEdit = computed(() => !!route.params.id)

const activeMenu = computed(() => '/data')

const categories = ref([])

const form = reactive({
  category: '',
  title: '',
  value: '',
  unit: '',
  date: '',
  remark: ''
})

const rules = {
  category: [{ required: true, message: '请选择分类', trigger: 'blur' }],
  title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
  value: [{ required: true, message: '请输入数值', trigger: 'blur' }],
  date: [{ required: true, message: '请选择日期', trigger: 'blur' }]
}

const loadCategories = async () => {
  try {
    const response = await dataAPI.categories()
    categories.value = response.data
  } catch (error) {
    console.error('Failed to load categories:', error)
  }
}

const loadData = async () => {
  if (!isEdit.value) return
  
  try {
    const response = await dataAPI.get(route.params.id)
    const data = response.data
    form.category = data.category
    form.title = data.title
    form.value = data.value
    form.unit = data.unit || ''
    form.date = new Date(data.date)
    form.remark = data.remark || ''
  } catch (error) {
    ElMessage.error('加载数据失败')
    router.push('/data')
  }
}

const handleSubmit = async () => {
  if (!form.category || !form.title || !form.value || !form.date) {
    ElMessage.warning('请填写必填项')
    return
  }
  
  submitting.value = true
  
  try {
    const data = {
      category: form.category,
      title: form.title,
      value: form.value,
      unit: form.unit || null,
      date: form.date instanceof Date ? form.date.toISOString().split('T')[0] : form.date,
      remark: form.remark || null
    }
    
    if (isEdit.value) {
      await dataAPI.update(route.params.id, data)
      ElMessage.success('修改成功')
    } else {
      await dataAPI.create(data)
      ElMessage.success('添加成功')
    }
    
    router.push('/data')
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '操作失败')
  } finally {
    submitting.value = false
  }
}

const goBack = () => {
  router.push('/data')
}

const addCategory = () => {
  if (!newCategory.value.trim()) {
    ElMessage.warning('请输入分类名称')
    return
  }
  
  if (!categories.value.includes(newCategory.value)) {
    categories.value.push(newCategory.value)
  }
  form.category = newCategory.value
  newCategory.value = ''
  showAddCategory.value = false
}

const handleLogout = () => {
  logout()
  ElMessage.success('已退出登录')
  router.push('/login')
}

onMounted(() => {
  loadCategories()
  loadData()
})
</script>

<style scoped>
.form-container {
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

.header-left {
  display: flex;
  align-items: center;
  gap: 15px;
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
  display: flex;
  justify-content: center;
}

.form-card {
  background: white;
  border-radius: 12px;
  padding: 30px;
  width: 100%;
  max-width: 600px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.form-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}
</style>
