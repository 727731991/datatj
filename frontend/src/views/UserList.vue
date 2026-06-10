<template>
  <div class="user-container">
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
          <h1>用户管理</h1>
        </div>
        <div class="user-info">
          <span>{{ user?.username }}</span>
          <span class="role">管理员</span>
        </div>
      </header>

      <div class="content-area">
        <div class="toolbar">
          <div class="search-area">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索用户名"
              class="search-input"
              @keyup.enter="handleSearch"
            />
            <el-button type="primary" @click="handleSearch">搜索</el-button>
          </div>
          <div class="action-area">
            <el-button type="primary" @click="showAddUser = true">
              <span>➕</span> 新增用户
            </el-button>
          </div>
        </div>

        <div class="table-container">
          <el-table :data="tableData" border class="data-table">
            <el-table-column prop="id" label="ID" width="60" />
            <el-table-column prop="username" label="用户名" />
            <el-table-column prop="email" label="邮箱" />
            <el-table-column prop="role" label="角色" width="100">
              <template #default="scope">
                <el-tag :type="scope.row.role === 'admin' ? 'danger' : 'success'">
                  {{ scope.row.role === 'admin' ? '管理员' : '普通用户' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="180" />
            <el-table-column label="操作" width="160">
              <template #default="scope">
                <el-button
                  size="small"
                  @click="handleEdit(scope.row)"
                >编辑</el-button>
                <el-button
                  size="small"
                  type="danger"
                  @click="handleDelete(scope.row.id, scope.row.username)"
                  :disabled="scope.row.id === user?.id"
                >删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </main>

    <el-dialog :title="editingUser ? '编辑用户' : '新增用户'" v-model="showAddUser" width="450px">
      <el-form ref="userFormRef" :model="form" :rules="rules">
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="用户名" />
        </el-form-item>
        <el-form-item prop="password" v-if="!editingUser">
          <el-input v-model="form.password" type="password" placeholder="密码" />
        </el-form-item>
        <el-form-item prop="email">
          <el-input v-model="form.email" placeholder="邮箱（可选）" />
        </el-form-item>
        <el-form-item prop="role">
          <el-select v-model="form.role" placeholder="选择角色">
            <el-option label="普通用户" value="user" />
            <el-option label="管理员" value="admin" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="closeDialog">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          {{ editingUser ? '保存修改' : '创建用户' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { userAPI } from '@/utils/api'
import { getUser, logout } from '@/utils/auth'

const router = useRouter()
const route = useRoute()

const user = ref(getUser())
const activeMenu = computed(() => route.path)

const tableData = ref([])
const searchKeyword = ref('')

const showAddUser = ref(false)
const userFormRef = ref(null)
const submitting = ref(false)
const editingUser = ref(null)

const form = reactive({
  username: '',
  password: '',
  email: '',
  role: 'user'
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  role: [{ required: true, message: '请选择角色', trigger: 'blur' }]
}

const loadUsers = async () => {
  try {
    const params = {}
    if (searchKeyword.value) {
      params.username = searchKeyword.value
    }
    
    const response = await userAPI.list(params)
    tableData.value = response.data
  } catch (error) {
    if (error.response?.status === 403) {
      ElMessage.error('没有权限访问')
      router.push('/')
    } else {
      ElMessage.error('加载用户列表失败')
    }
    console.error('Failed to load users:', error)
  }
}

const handleSearch = () => {
  loadUsers()
}

const handleEdit = (userData) => {
  editingUser.value = userData
  form.username = userData.username
  form.email = userData.email || ''
  form.role = userData.role
  form.password = ''
  showAddUser.value = true
}

const handleDelete = async (id, username) => {
  try {
    await ElMessage.confirm(`确定要删除用户"${username}"吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await userAPI.delete(id)
    ElMessage.success('删除成功')
    loadUsers()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleSubmit = async () => {
  if (!form.username || !form.role) {
    ElMessage.warning('请填写必填项')
    return
  }
  
  if (!editingUser.value && !form.password) {
    ElMessage.warning('请输入密码')
    return
  }
  
  submitting.value = true
  
  try {
    const data = {
      username: form.username,
      email: form.email || null,
      role: form.role
    }
    
    if (!editingUser.value) {
      data.password = form.password
      await userAPI.create(data)
      ElMessage.success('创建成功')
    } else {
      if (form.password) {
        data.password = form.password
      }
      await userAPI.update(editingUser.value.id, data)
      ElMessage.success('修改成功')
    }
    
    closeDialog()
    loadUsers()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '操作失败')
  } finally {
    submitting.value = false
  }
}

const closeDialog = () => {
  showAddUser.value = false
  editingUser.value = null
  form.username = ''
  form.password = ''
  form.email = ''
  form.role = 'user'
}

const handleLogout = () => {
  logout()
  ElMessage.success('已退出登录')
  router.push('/login')
}

onMounted(() => {
  if (user.value?.role !== 'admin') {
    ElMessage.error('没有权限访问')
    router.push('/')
    return
  }
  loadUsers()
})
</script>

<style scoped>
.user-container {
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
  width: 250px;
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
}
</style>
