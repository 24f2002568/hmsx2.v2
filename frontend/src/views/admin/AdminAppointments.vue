<template>
  <div>
    <div class="topbar">
      <div class="topbar-title">All Appointments</div>
      <div class="d-flex gap-2">
        <button v-for="s in statuses" :key="s" @click="statusFilter = s; fetchAppointments()"
          :class="['btn-outline', { 'btn-ink': statusFilter === s }]" style="padding:6px 14px; font-size:12px;">
          {{ s || 'All' }}
        </button>
      </div>
    </div>
    <div class="content-area">
      <div v-if="loading" class="loading-spinner"><div class="spinner-ring"></div> Loading...</div>
      <div v-else-if="!appointments.length" class="empty-state">
        <i class="bi bi-calendar3"></i><p>NO APPOINTMENTS</p>
      </div>
      <div v-else class="card-hms">
        <table class="table-hms">
          <thead>
            <tr>
              <th>#ID</th>
              <th>Patient</th>
              <th>Doctor</th>
              <th>Date & Time</th>
              <th>Status</th>
              <th>Reason</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="a in appointments" :key="a.id">
              <td class="mono" style="color:var(--ink-faint); font-size:12px;">#{{ a.id }}</td>
              <td style="font-size:13px; font-weight:500;">{{ a.patient_name }}</td>
              <td>
                <div style="font-size:13px; font-weight:500;">{{ a.doctor_name }}</div>
                <div class="text-mono" style="font-size:10px; color:var(--ink-faint);">{{ a.doctor_specialization }}</div>
              </td>
              <td>
                <div style="font-size:13px; font-weight:600;">{{ formatDate(a.date) }}</div>
                <div class="mono" style="font-size:11px; color:var(--ink-faint);">{{ a.time }}</div>
              </td>
              <td>
                <span :class="`badge-status badge-${a.status.toLowerCase()}`">{{ a.status }}</span>
              </td>
              <td style="font-size:12px; color:var(--ink-muted); max-width:180px;">
                {{ a.reason || '—' }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { axios, API } from '../../store/auth'

const appointments = ref([])
const loading = ref(true)
const statuses = ['', 'Booked', 'Completed', 'Cancelled']
const statusFilter = ref('')

const formatDate = (d) => new Date(d).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })

const fetchAppointments = async () => {
  loading.value = true
  const { data } = await axios.get(`${API}/admin/appointments`, { params: { status: statusFilter.value } })
  appointments.value = data
  loading.value = false
}

onMounted(fetchAppointments)
</script>
