<template>
  <div class="page-wrap">
    <aside class="sidebar">
      <div class="sidebar-logo">
        <div class="brand">MEDIX</div>
        <div class="sub">Patient Portal</div>
      </div>
      <nav class="sidebar-nav">
        <div class="nav-section-label">Overview</div>
        <router-link to="/patient/dashboard" :class="{ active: route.path === '/patient/dashboard' }">
          <i class="bi bi-grid-1x2"></i> Dashboard
        </router-link>
        <div class="nav-section-label">Healthcare</div>
        <router-link to="/patient/doctors" :class="{ active: route.path === '/patient/doctors' }">
          <i class="bi bi-person-badge"></i> Find Doctors
        </router-link>
        <router-link to="/patient/appointments" :class="{ active: route.path === '/patient/appointments' }">
          <i class="bi bi-calendar3"></i> Appointments
        </router-link>
        <div class="nav-section-label">Account</div>
        <router-link to="/patient/profile" :class="{ active: route.path === '/patient/profile' }">
          <i class="bi bi-person-circle"></i> My Profile
        </router-link>
        <router-link to="/patient/export" :class="{ active: route.path === '/patient/export' }">
          <i class="bi bi-download"></i> Export Data
        </router-link>
      </nav>
      <div class="sidebar-footer">
        <div class="sidebar-user">
          <div class="user-avatar">{{ initial }}</div>
          <div class="user-info">
            <div class="name">{{ auth.user?.username }}</div>
            <div class="role-badge">Patient</div>
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
const initial = computed(() => auth.user?.username?.[0]?.toUpperCase() || 'P')
const logout = () => { auth.logout(); router.push('/login') }
</script>
