<template>
  <div>
    <div class="topbar">
      <div class="topbar-title">My Dashboard</div>
      <div class="text-mono" style="font-size:11px; color:var(--ink-faint);">{{ today }}</div>
    </div>
    <div class="content-area">
      <div v-if="loading" class="loading-spinner"><div class="spinner-ring"></div></div>
      <template v-else>
        <!-- Profile banner -->
        <div class="doc-banner mb-4">
          <div class="doc-avatar-lg">{{ info.doctor?.full_name?.[0] }}</div>
          <div>
            <div style="font-family:var(--font-display); font-size:22px; font-weight:800;">
              Dr. {{ info.doctor?.full_name }}
            </div>
            <div class="text-mono" style="font-size:11px; color:rgba(255,255,255,0.5); letter-spacing:0.12em; text-transform:uppercase; margin-top:3px;">
              {{ info.doctor?.specialization }} · {{ info.doctor?.department }}
            </div>
          </div>
        </div>

        <div class="grid-4 mb-4">
          <div class="stat-card">
            <div class="stat-number">{{ info.today_appointments }}</div>
            <div class="stat-label">Today's Appointments</div>
          </div>
          <div class="stat-card">
            <div class="stat-number">{{ info.week_appointments }}</div>
            <div class="stat-label">This Week</div>
          </div>
          <div class="stat-card">
            <div class="stat-number">{{ info.total_patients }}</div>
            <div class="stat-label">Total Patients</div>
          </div>
          <div class="stat-card">
            <div class="stat-number">{{ info.doctor?.experience_years || 0 }}</div>
            <div class="stat-label">Years Experience</div>
          </div>
        </div>

        <!-- Today's appointments -->
        <div class="card-hms">
          <div class="section-header">
            <div class="section-title">Today's Schedule</div>
            <router-link to="/doctor/appointments" class="btn-outline" style="padding:6px 14px; font-size:12px;">
              View All
            </router-link>
          </div>
          <div v-if="!todayAppts.length" class="empty-state" style="padding:30px 0;">
            <i class="bi bi-calendar-check"></i>
            <p>NO APPOINTMENTS TODAY</p>
          </div>
          <div v-else>
            <div v-for="a in todayAppts" :key="a.id" class="appt-card">
              <div class="d-flex align-items-center gap-3">
                <div class="time-block">{{ a.time }}</div>
                <div>
                  <div style="font-weight:600;">{{ a.patient_name }}</div>
                  <div style="font-size:12px; color:var(--ink-faint);">{{ a.reason || 'General consultation' }}</div>
                </div>
              </div>
              <span :class="`badge-status badge-${a.status.toLowerCase()}`">{{ a.status }}</span>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { axios, API } from '../../store/auth'

const info = ref({ doctor: null, today_appointments: 0, week_appointments: 0, total_patients: 0 })
const todayAppts = ref([])
const loading = ref(true)
const today = new Date().toLocaleDateString('en-GB', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })

onMounted(async () => {
  const [d1, d2] = await Promise.all([
    axios.get(`${API}/doctor/dashboard`),
    axios.get(`${API}/doctor/appointments`, { params: { filter: 'today' } })
  ])
  info.value = d1.data
  todayAppts.value = d2.data
  loading.value = false
})
</script>

<style scoped>
.doc-banner {
  background: var(--ink);
  color: var(--paper);
  border-radius: var(--radius-lg);
  padding: 24px 28px;
  display: flex;
  align-items: center;
  gap: 20px;
}

.doc-avatar-lg {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: #222;
  border: 2px solid #333;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-display);
  font-size: 24px;
  font-weight: 800;
  flex-shrink: 0;
}

.time-block {
  font-family: var(--font-mono);
  font-size: 13px;
  font-weight: 500;
  background: var(--paper-dim);
  padding: 6px 10px;
  border-radius: var(--radius);
  color: var(--ink);
  min-width: 60px;
  text-align: center;
}
</style>
