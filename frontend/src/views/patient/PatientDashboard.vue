<template>
  <div>
    <div class="topbar">
      <div class="topbar-title">My Health Dashboard</div>
      <div class="text-mono" style="font-size:11px; color:var(--ink-faint);">{{ today }}</div>
    </div>
    <div class="content-area">
      <div v-if="loading" class="loading-spinner"><div class="spinner-ring"></div></div>
      <template v-else>
        <!-- Welcome -->
        <div class="welcome-banner mb-4">
          <div>
            <div style="font-family:var(--font-mono); font-size:10px; letter-spacing:0.2em; text-transform:uppercase; color:rgba(255,255,255,0.4); margin-bottom:6px;">Welcome back</div>
            <div style="font-family:var(--font-display); font-size:24px; font-weight:800; color:var(--paper);">{{ profile?.full_name }}</div>
          </div>
          <router-link to="/patient/doctors" class="btn-outline" style="background:rgba(255,255,255,0.1); color:var(--paper); border-color:rgba(255,255,255,0.2);">
            <i class="bi bi-search"></i> Find a Doctor
          </router-link>
        </div>

        <!-- Upcoming Appointments -->
        <div class="card-hms mb-4">
          <div class="section-header">
            <div class="section-title">Upcoming Appointments</div>
            <router-link to="/patient/appointments" class="btn-outline" style="padding:6px 14px; font-size:12px;">View All</router-link>
          </div>
          <div v-if="!upcoming.length" class="empty-state" style="padding:24px 0;">
            <i class="bi bi-calendar-plus"></i>
            <p>NO UPCOMING APPOINTMENTS</p>
          </div>
          <div v-else>
            <div v-for="a in upcoming.slice(0,3)" :key="a.id" class="appt-card">
              <div class="d-flex gap-3 align-items-center">
                <div class="date-pill">
                  <div>{{ new Date(a.date).getDate() }}</div>
                  <div style="font-family:var(--font-mono); font-size:9px; letter-spacing:0.1em; text-transform:uppercase;">
                    {{ new Date(a.date).toLocaleDateString('en', { month: 'short' }) }}
                  </div>
                </div>
                <div>
                  <div style="font-weight:700;">Dr. {{ a.doctor_name }}</div>
                  <div style="font-size:12px; color:var(--ink-faint);">{{ a.doctor_specialization }} · {{ a.time }}</div>
                </div>
              </div>
              <span :class="`badge-status badge-${a.status.toLowerCase()}`">{{ a.status }}</span>
            </div>
          </div>
        </div>

        <!-- Departments -->
        <div class="card-hms">
          <div class="section-title mb-3" style="font-size:16px;">Specializations Available</div>
          <div class="dept-grid">
            <div v-for="d in departments" :key="d.id" class="dept-chip" @click="goSearch(d.name)">
              <i class="bi bi-plus-circle-dotted" style="font-size:16px; margin-bottom:4px;"></i>
              <div>{{ d.name }}</div>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { axios, API } from '../../store/auth'

const router = useRouter()
const profile = ref(null)
const upcoming = ref([])
const departments = ref([])
const loading = ref(true)
const today = new Date().toLocaleDateString('en-GB', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })

const goSearch = (name) => router.push({ path: '/patient/doctors', query: { specialization: name } })

onMounted(async () => {
  const [p, a, d] = await Promise.all([
    axios.get(`${API}/patient/profile`),
    axios.get(`${API}/patient/appointments`, { params: { filter: 'upcoming' } }),
    axios.get(`${API}/departments/`)
  ])
  profile.value = p.data.profile
  upcoming.value = a.data
  departments.value = d.data
  loading.value = false
})
</script>

<style scoped>
.welcome-banner {
  background: var(--ink);
  border-radius: var(--radius-lg);
  padding: 24px 28px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.date-pill {
  text-align: center;
  background: var(--paper-dim);
  border-radius: var(--radius);
  padding: 6px 12px;
  font-family: var(--font-display);
  font-size: 20px;
  font-weight: 800;
  min-width: 52px;
}

.dept-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 10px;
}

.dept-chip {
  background: var(--paper-off);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 14px 12px;
  text-align: center;
  cursor: pointer;
  font-family: var(--font-display);
  font-size: 12px;
  font-weight: 600;
  transition: var(--transition);
}

.dept-chip:hover {
  background: var(--ink);
  color: var(--paper);
  border-color: var(--ink);
}
</style>
