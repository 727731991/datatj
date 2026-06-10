import { createRouter, createWebHistory } from 'vue-router'
import Login from '@/views/Login.vue'
import Dashboard from '@/views/Dashboard.vue'
import DataList from '@/views/DataList.vue'
import DataForm from '@/views/DataForm.vue'
import ReportCenter from '@/views/ReportCenter.vue'
import UserList from '@/views/UserList.vue'
import { getToken } from '@/utils/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/data',
    name: 'DataList',
    component: DataList,
    meta: { requiresAuth: true }
  },
  {
    path: '/data/add',
    name: 'DataAdd',
    component: DataForm,
    meta: { requiresAuth: true }
  },
  {
    path: '/data/edit/:id',
    name: 'DataEdit',
    component: DataForm,
    meta: { requiresAuth: true }
  },
  {
    path: '/reports',
    name: 'ReportCenter',
    component: ReportCenter,
    meta: { requiresAuth: true }
  },
  {
    path: '/users',
    name: 'UserList',
    component: UserList,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth) {
    if (getToken()) {
      next()
    } else {
      next('/login')
    }
  } else {
    next()
  }
})

export default router
