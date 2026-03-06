import { createRouter, createWebHashHistory } from 'vue-router'
import { useAuthStore } from '../store/auth'

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', component: () => import('../views/Login.vue'), meta: { guest: true } },
  { path: '/register', component: () => import('../views/Register.vue'), meta: { guest: true } },

  { path: '/admin', component: () => import('../views/admin/AdminLayout.vue'), meta: { role: 'admin' }, children: [
    { path: '', redirect: '/admin/dashboard' },
    { path: 'dashboard', component: () => import('../views/admin/AdminDashboard.vue') },
    { path: 'doctors', component: () => import('../views/admin/AdminDoctors.vue') },
    { path: 'patients', component: () => import('../views/admin/AdminPatients.vue') },
    { path: 'appointments', component: () => import('../views/admin/AdminAppointments.vue') },
    { path: 'departments', component: () => import('../views/admin/AdminDepartments.vue') },
    { path: 'jobs', component: () => import('../views/admin/AdminJobs.vue') },
  ]},

  { path: '/doctor', component: () => import('../views/doctor/DoctorLayout.vue'), meta: { role: 'doctor' }, children: [
    { path: '', redirect: '/doctor/dashboard' },
    { path: 'dashboard', component: () => import('../views/doctor/DoctorDashboard.vue') },
    { path: 'appointments', component: () => import('../views/doctor/DoctorAppointments.vue') },
    { path: 'patients', component: () => import('../views/doctor/DoctorPatients.vue') },
    { path: 'availability', component: () => import('../views/doctor/DoctorAvailability.vue') },
  ]},

  { path: '/patient', component: () => import('../views/patient/PatientLayout.vue'), meta: { role: 'patient' }, children: [
    { path: '', redirect: '/patient/dashboard' },
    { path: 'dashboard', component: () => import('../views/patient/PatientDashboard.vue') },
    { path: 'doctors', component: () => import('../views/patient/PatientDoctors.vue') },
    { path: 'appointments', component: () => import('../views/patient/PatientAppointments.vue') },
    { path: 'profile', component: () => import('../views/patient/PatientProfile.vue') },
    { path: 'export', component: () => import('../views/patient/PatientExport.vue') },
  ]},

  { path: '/:pathMatch(.*)*', redirect: '/login' },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const auth = useAuthStore()

  if (to.meta.guest && auth.isLoggedIn) {
    const redirectMap = { admin: '/admin/dashboard', doctor: '/doctor/dashboard', patient: '/patient/dashboard' }
    return next(redirectMap[auth.role] || '/login')
  }

  if (to.meta.role) {
    if (!auth.isLoggedIn) return next('/login')
    if (auth.role !== to.meta.role) return next(`/${auth.role}/dashboard`)
  }

  next()
})

export default router