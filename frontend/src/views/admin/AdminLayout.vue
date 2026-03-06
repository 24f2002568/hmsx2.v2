<template>
  <div class="page-wrap">
    <aside class="sidebar">
      <div class="sidebar-logo">
        <div class="brand">MEDIX</div>
        <div class="sub">Admin Console</div>
      </div>
      <nav class="sidebar-nav">
        <div class="nav-section-label">Overview</div>
        <router-link to="/admin/dashboard" :class="{ active: route.path === '/admin/dashboard' }">
          <i class="bi bi-grid-1x2"></i> Dashboard
        </router-link>

        <div class="nav-section-label">Management</div>
        <router-link to="/admin/doctors" :class="{ active: route.path === '/admin/doctors' }">
          <i class="bi bi-person-badge"></i> Doctors
        </router-link>
        <router-link to="/admin/patients" :class="{ active: route.path === '/admin/patients' }">
          <i class="bi bi-people"></i> Patients
        </router-link>
        <router-link to="/admin/departments" :class="{ active: route.path === '/admin/departments' }">
          <i class="bi bi-diagram-3"></i> Departments
        </router-link>
        <router-link to="/admin/appointments" :class="{ active: route.path === '/admin/appointments' }">
          <i class="bi bi-calendar3"></i> Appointments
        </router-link>
        <div class="nav-section-label">System</div>
        <router-link to="/admin/jobs" :class="{ active: route.path === '/admin/jobs' }">
          <i class="bi bi-cpu"></i> Background Jobs
        </router-link>
      </nav>
      <div class="sidebar-footer">
        <div class="sidebar-user">
          <div class="user-avatar">A</div>
          <div class="user-info">
            <div class="name">{{ auth.user?.username }}</div>
            <div class="role-badge">Administrator</div>
          </div>
        </div>
        <button @click="logout" class="btn-outline w-100" style="justify-content:center; font-size:12px; padding:7px;">
          <i class="bi bi-box-arrow-right"></i> Sign Out
        </button>
      </div>
    </aside>
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../../store/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const logout = () => { auth.logout(); router.push('/login') }
</script>
