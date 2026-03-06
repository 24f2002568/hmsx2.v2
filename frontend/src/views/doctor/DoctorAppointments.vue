<template>
  <div>
    <div class="topbar">
      <div class="topbar-title">Appointments</div>
      <div class="d-flex gap-2">
        <button v-for="f in filters" :key="f.val" @click="activeFilter = f.val; fetchAppts()"
          :class="['btn-outline', { 'btn-ink': activeFilter === f.val }]" style="padding:6px 14px; font-size:12px;">
          {{ f.label }}
        </button>
      </div>
    </div>
    <div class="content-area">
      <div v-if="loading" class="loading-spinner"><div class="spinner-ring"></div></div>
      <div v-else-if="!appointments.length" class="empty-state">
        <i class="bi bi-calendar3"></i><p>NO APPOINTMENTS</p>
      </div>
      <div v-else>
        <div v-for="a in appointments" :key="a.id" class="appt-row">
          <div class="appt-date-col">
            <div class="appt-date">{{ new Date(a.date).getDate() }}</div>
            <div class="appt-month">{{ new Date(a.date).toLocaleDateString('en', { month: 'short' }) }}</div>
            <div class="mono" style="font-size:11px; margin-top:2px;">{{ a.time }}</div>
          </div>
          <div class="appt-info">
            <div style="font-weight:700; font-size:15px;">{{ a.patient_name }}</div>
            <div style="font-size:13px; color:var(--ink-muted);">{{ a.reason || 'General consultation' }}</div>
            <div v-if="a.treatment" class="treatment-record mt-2">
              <div class="treatment-field">
                <label>Diagnosis</label><p>{{ a.treatment.diagnosis }}</p>
              </div>
              <div class="treatment-field">
                <label>Prescription</label><p>{{ a.treatment.prescription }}</p>
              </div>
            </div>
          </div>
          <div class="appt-actions">
            <span :class="`badge-status badge-${a.status.toLowerCase()}`">{{ a.status }}</span>
            <div v-if="a.status === 'Booked'" class="d-flex gap-2 mt-2">
              <button @click="openComplete(a)" class="btn-ink" style="padding:6px 12px; font-size:12px;">
                <i class="bi bi-check-lg"></i> Complete
              </button>
              <button @click="cancelAppt(a)" class="btn-danger" style="padding:6px 12px; font-size:12px;">
                <i class="bi bi-x-lg"></i> Cancel
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Complete Modal -->
    <div v-if="completeAppt" class="modal-overlay" @click.self="completeAppt = null">
      <div class="modal-box">
        <div class="modal-title">Mark as Completed — {{ completeAppt.patient_name }}</div>
        <button @click="completeAppt = null" class="modal-close"><i class="bi bi-x-lg"></i></button>
        <div class="form-group">
          <label class="form-label-hms">Diagnosis *</label>
          <textarea v-model="treatForm.diagnosis" class="form-control-hms" rows="2" placeholder="Patient diagnosis..."></textarea>
        </div>
        <div class="form-group">
          <label class="form-label-hms">Prescription</label>
          <textarea v-model="treatForm.prescription" class="form-control-hms" rows="2" placeholder="Medications and dosage..."></textarea>
        </div>
        <div class="form-group">
          <label class="form-label-hms">Notes</label>
          <textarea v-model="treatForm.notes" class="form-control-hms" rows="2" placeholder="Additional notes..."></textarea>
        </div>
        <div class="form-group">
          <label class="form-label-hms">Next Visit Date</label>
          <input v-model="treatForm.next_visit" class="form-control-hms" type="date" />
        </div>
        <div class="d-flex gap-2">
          <button @click="submitComplete" class="btn-ink">Save & Complete</button>
          <button @click="completeAppt = null" class="btn-outline">Cancel</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { axios, API } from '../../store/auth'

const appointments = ref([])
const loading = ref(true)
const activeFilter = ref('upcoming')
const filters = [
  { val: 'today', label: 'Today' },
  { val: 'upcoming', label: 'Upcoming' },
  { val: 'past', label: 'Past' },
  { val: '', label: 'All' },
]

const completeAppt = ref(null)
const treatForm = ref({ diagnosis: '', prescription: '', notes: '', next_visit: '' })

const fetchAppts = async () => {
  loading.value = true
  const { data } = await axios.get(`${API}/doctor/appointments`, { params: { filter: activeFilter.value } })
  appointments.value = data
  loading.value = false
}

const openComplete = (a) => {
  completeAppt.value = a
  treatForm.value = { diagnosis: a.treatment?.diagnosis || '', prescription: a.treatment?.prescription || '', notes: a.treatment?.notes || '', next_visit: '' }
}

const submitComplete = async () => {
  await axios.post(`${API}/doctor/appointments/${completeAppt.value.id}/complete`, treatForm.value)
  completeAppt.value = null
  await fetchAppts()
}

const cancelAppt = async (a) => {
  if (!confirm('Cancel this appointment?')) return
  await axios.post(`${API}/doctor/appointments/${a.id}/cancel`)
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
  transition: var(--transition);
}

.appt-row:hover { border-color: var(--border-strong); }

.appt-date-col {
  text-align: center;
  min-width: 56px;
  padding-top: 2px;
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
