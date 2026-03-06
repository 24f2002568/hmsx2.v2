<template>
  <div class="page-wrap">
    <aside class="sidebar">
      <div class="sidebar-logo">
        <div class="brand">MEDIX</div>
        <div class="sub">Doctor Portal</div>
      </div>
      <nav class="sidebar-nav">
        <div class="nav-section-label">Overview</div>
        <router-link to="/doctor/dashboard" :class="{ active: route.path === '/doctor/dashboard' }">
          <i class="bi bi-grid-1x2"></i> Dashboard
        </router-link>
        <div class="nav-section-label">Practice</div>
        <router-link to="/doctor/appointments" :class="{ active: route.path === '/doctor/appointments' }">
          <i class="bi bi-calendar3"></i> Appointments
        </router-link>
        <router-link to="/doctor/patients" :class="{ active: route.path === '/doctor/patients' }">
          <i class="bi bi-people"></i> My Patients
        </router-link>
        <router-link to="/doctor/availability" :class="{ active: route.path === '/doctor/availability' }">
          <i class="bi bi-clock"></i> Availability
        </router-link>
      </nav>
      <div class="sidebar-footer">
        <div class="sidebar-user">
          <div class="user-avatar">{{ initial }}</div>
          <div class="user-info">
            <div class="name">{{ auth.user?.username }}</div>
            <div class="role-badge">Doctor</div>
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
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../../store/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const initial = computed(() => auth.user?.username?.[0]?.toUpperCase() || 'D')
const logout = () => { auth.logout(); router.push('/login') }
</script>
