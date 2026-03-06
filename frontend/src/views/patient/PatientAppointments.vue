<template>
  <div>
    <div class="topbar">
      <div class="topbar-title">My Appointments</div>
      <div class="d-flex gap-2">
        <button v-for="f in filters" :key="f.val" @click="activeFilter = f.val; fetchAppts()"
          :class="['btn-outline', { 'btn-ink': activeFilter === f.val }]" style="padding:6px 14px; font-size:12px;">
          {{ f.label }}
        </button>
        <a :href="csvUrl" download class="btn-outline" style="padding:6px 14px; font-size:12px;">
          <i class="bi bi-download"></i> Export CSV
        </a>
      </div>
    </div>
    <div class="content-area">
      <div v-if="loading" class="loading-spinner"><div class="spinner-ring"></div></div>
      <div v-else-if="!appointments.length" class="empty-state">
        <i class="bi bi-calendar3"></i><p>NO APPOINTMENTS FOUND</p>
      </div>
      <div v-else>
        <div v-for="a in appointments" :key="a.id" class="appt-row">
          <div class="appt-date-col">
            <div class="appt-date">{{ new Date(a.date).getDate() }}</div>
            <div class="appt-month">{{ new Date(a.date).toLocaleDateString('en', { month: 'short' }) }}</div>
            <div class="mono" style="font-size:11px; margin-top:2px;">{{ a.time }}</div>
          </div>
          <div class="appt-info">
            <div style="font-weight:700; font-size:15px;">Dr. {{ a.doctor_name }}</div>
            <div style="font-size:12px; color:var(--ink-faint);">{{ a.doctor_specialization }}</div>
            <div v-if="a.reason" style="font-size:13px; color:var(--ink-muted); margin-top:4px;">{{ a.reason }}</div>
            <div v-if="a.treatment" class="treatment-record mt-2">
              <div class="row">
                <div class="col-md-4"><div class="treatment-field"><label>Diagnosis</label><p>{{ a.treatment.diagnosis }}</p></div></div>
                <div class="col-md-4"><div class="treatment-field"><label>Prescription</label><p>{{ a.treatment.prescription }}</p></div></div>
                <div class="col-md-4"><div class="treatment-field"><label>Next Visit</label><p>{{ a.treatment.next_visit || '—' }}</p></div></div>
              </div>
              <div class="treatment-field" v-if="a.treatment.notes"><label>Notes</label><p>{{ a.treatment.notes }}</p></div>
            </div>
          </div>
          <div class="appt-actions">
            <span :class="`badge-status badge-${a.status.toLowerCase()}`">{{ a.status }}</span>
            <div v-if="a.status === 'Booked'" class="d-flex gap-2 mt-2">
              <button @click="openReschedule(a)" class="btn-outline" style="padding:5px 10px; font-size:12px;">
                <i class="bi bi-arrow-repeat"></i>
              </button>
              <button @click="cancelAppt(a)" class="btn-danger" style="padding:5px 10px; font-size:12px;">
                <i class="bi bi-x-lg"></i>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Reschedule Modal -->
    <div v-if="rescheduleAppt" class="modal-overlay" @click.self="rescheduleAppt = null">
      <div class="modal-box">
        <div class="modal-title">Reschedule Appointment</div>
        <button @click="rescheduleAppt = null" class="modal-close"><i class="bi bi-x-lg"></i></button>
        <div class="form-group">
          <label class="form-label-hms">New Date</label>
          <input v-model="rescheduleForm.date" class="form-control-hms" type="date" />
        </div>
        <div class="form-group">
          <label class="form-label-hms">New Time</label>
          <div class="slot-grid">
            <div v-for="t in timeSlots" :key="t" :class="['slot-btn', { selected: rescheduleForm.time === t }]"
              @click="rescheduleForm.time = t">{{ t }}</div>
          </div>
        </div>
        <div class="d-flex gap-2">
          <button @click="submitReschedule" class="btn-ink">Reschedule</button>
          <button @click="rescheduleAppt = null" class="btn-outline">Cancel</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { axios, API } from '../../store/auth'

const appointments = ref([])
const loading = ref(true)
const activeFilter = ref('all')
const filters = [
  { val: 'upcoming', label: 'Upcoming' },
  { val: 'past', label: 'Past' },
  { val: 'all', label: 'All' },
]
const timeSlots = ['09:00', '09:30', '10:00', '10:30', '11:00', '11:30', '14:00', '14:30', '15:00', '15:30', '16:00', '16:30']

const rescheduleAppt = ref(null)
const rescheduleForm = ref({ date: '', time: '' })
const csvUrl = `${API}/patient/export-csv`

const fetchAppts = async () => {
  loading.value = true
  const { data } = await axios.get(`${API}/patient/appointments`, { params: { filter: activeFilter.value } })
  appointments.value = data
  loading.value = false
}

const cancelAppt = async (a) => {
  if (!confirm('Cancel this appointment?')) return
  await axios.post(`${API}/patient/appointments/${a.id}/cancel`)
  await fetchAppts()
}

const openReschedule = (a) => {
  rescheduleAppt.value = a
  rescheduleForm.value = { date: a.date, time: a.time }
}

const submitReschedule = async () => {
  await axios.post(`${API}/patient/appointments/${rescheduleAppt.value.id}/reschedule`, rescheduleForm.value)
  rescheduleAppt.value = null
  await fetchAppts()
}

onMounted(fetchAppts)
</script>

<style scoped>
.appt-row {
  display: flex;
  gap: 20px;
  padding: 18px 20px;
  background: var(--paper);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  margin-bottom: 10px;
  align-items: flex-start;
}

.appt-date-col {
  text-align: center;
  min-width: 56px;
}

.appt-date {
  font-family: var(--font-display);
  font-size: 28px;
  font-weight: 800;
  line-height: 1;
}

.appt-month {
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--ink-faint);
}

.appt-info { flex: 1; }

.appt-actions {
  min-width: 120px;
  text-align: right;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}
</style>
