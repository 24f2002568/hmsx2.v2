<template>
  <div>
    <div class="topbar">
      <div class="topbar-title">Dashboard</div>
      <div class="text-mono" style="font-size:11px; color:var(--ink-faint);">{{ today }}</div>
    </div>
    <div class="content-area">
      <div v-if="loading" class="loading-spinner">
        <div class="spinner-ring"></div> Loading...
      </div>
      <template v-else>
        <!-- Stats -->
        <div class="grid-4 mb-4">
          <div class="stat-card">
            <div class="stat-number">{{ stats.total_doctors }}</div>
            <div class="stat-label">Doctors</div>
          </div>
          <div class="stat-card">
            <div class="stat-number">{{ stats.total_patients }}</div>
            <div class="stat-label">Patients</div>
          </div>
          <div class="stat-card">
            <div class="stat-number">{{ stats.total_appointments }}</div>
            <div class="stat-label">Total Appointments</div>
          </div>
          <div class="stat-card">
            <div class="stat-number">{{ stats.booked }}</div>
            <div class="stat-label">Active Bookings</div>
          </div>
        </div>

        <div class="row g-3">
          <div class="col-md-8">
            <div class="card-hms">
              <div class="section-header">
                <div class="section-title">Appointment Status</div>
              </div>
              <div class="d-flex gap-3 flex-wrap">
                <div class="status-bar-item">
                  <div class="status-bar-fill" :style="`width:${pct(stats.booked)}%`"></div>
                  <span>Booked</span>
                  <strong class="mono">{{ stats.booked }}</strong>
                </div>
                <div class="status-bar-item">
                  <div class="status-bar-fill green" :style="`width:${pct(stats.completed)}%`"></div>
                  <span>Completed</span>
                  <strong class="mono">{{ stats.completed }}</strong>
                </div>
                <div class="status-bar-item">
                  <div class="status-bar-fill grey" :style="`width:${pct(stats.cancelled)}%`"></div>
                  <span>Cancelled</span>
                  <strong class="mono">{{ stats.cancelled }}</strong>
                </div>
              </div>
            </div>
          </div>
          <div class="col-md-4">
            <div class="card-hms">
              <div class="section-title mb-3" style="font-size:15px;">Quick Actions</div>
              <div class="d-flex flex-column gap-2">
                <router-link to="/admin/doctors" class="btn-ink" style="justify-content:center;">
                  <i class="bi bi-person-plus"></i> Add Doctor
                </router-link>
                <router-link to="/admin/departments" class="btn-outline" style="justify-content:center;">
                  <i class="bi bi-plus-circle"></i> Add Department
                </router-link>
                <router-link to="/admin/appointments" class="btn-outline" style="justify-content:center;">
                  <i class="bi bi-calendar3"></i> View Appointments
                </router-link>
              </div>
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

const stats = ref({ total_doctors: 0, total_patients: 0, total_appointments: 0, booked: 0, completed: 0, cancelled: 0 })
const loading = ref(true)
const today = new Date().toLocaleDateString('en-GB', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })

const pct = (val) => stats.value.total_appointments ? Math.round(val / stats.value.total_appointments * 100) : 0

onMounted(async () => {
  try {
    const { data } = await axios.get(`${API}/admin/dashboard`)
    stats.value = data
  } finally { loading.value = false }
})
</script>

<style scoped>
.status-bar-item {
  flex: 1;
  min-width: 120px;
  background: var(--paper-off);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 14px 16px;
  position: relative;
  overflow: hidden;
}

.status-bar-fill {
  position: absolute;
  bottom: 0; left: 0;
  height: 3px;
  background: var(--ink);
  transition: width 1s ease;
  min-width: 8px;
}

.status-bar-fill.green { background: #1a6b1a; }
.status-bar-fill.grey { background: #888; }

.status-bar-item span {
  display: block;
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--ink-faint);
  margin-bottom: 4px;
}

.status-bar-item strong {
  font-family: var(--font-display);
  font-size: 28px;
  font-weight: 800;
}
</style>
