<template>
  <div>
    <div class="topbar"><div class="topbar-title">My Availability</div></div>
    <div class="content-area">
      <div class="card-hms mb-4">
        <div class="section-title mb-4" style="font-size:16px;">Set Your Availability (Next 7 Days)</div>
        <div class="week-grid">
          <div v-for="day in next7Days" :key="day.iso" class="day-card" :class="{ 'day-set': hasAvail(day.iso) }">
            <div class="day-name">{{ day.dayName }}</div>
            <div class="day-date">{{ day.date }}</div>
            <button @click="openSlot(day.iso)" class="btn-outline mt-2 w-100" style="font-size:11px; padding:5px;">
              {{ hasAvail(day.iso) ? 'Edit' : 'Set' }}
            </button>
          </div>
        </div>
      </div>

      <div class="card-hms">
        <div class="section-title mb-3" style="font-size:16px;">Current Availability</div>
        <div v-if="!avails.length" class="empty-state" style="padding:20px 0;">
          <p>NO AVAILABILITY SET</p>
        </div>
        <table v-else class="table-hms">
          <thead>
            <tr><th>Date</th><th>Start</th><th>End</th><th>Max Appointments</th><th>Status</th></tr>
          </thead>
          <tbody>
            <tr v-for="a in avails" :key="a.id">
              <td style="font-weight:600;">{{ formatDate(a.date) }}</td>
              <td class="mono">{{ a.start_time }}</td>
              <td class="mono">{{ a.end_time }}</td>
              <td class="mono">{{ a.max_appointments }}</td>
              <td><span :class="a.is_available ? 'badge-status badge-active' : 'badge-status badge-inactive'">
                {{ a.is_available ? 'Available' : 'Unavailable' }}
              </span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="slotDate" class="modal-overlay" @click.self="slotDate = null">
      <div class="modal-box">
        <div class="modal-title">Set Availability — {{ slotDate }}</div>
        <button @click="slotDate = null" class="modal-close"><i class="bi bi-x-lg"></i></button>
        <div class="row g-3">
          <div class="col-md-6">
            <label class="form-label-hms">Start Time</label>
            <input v-model="slotForm.start_time" class="form-control-hms" type="time" />
          </div>
          <div class="col-md-6">
            <label class="form-label-hms">End Time</label>
            <input v-model="slotForm.end_time" class="form-control-hms" type="time" />
          </div>
          <div class="col-md-6">
            <label class="form-label-hms">Max Appointments</label>
            <input v-model.number="slotForm.max_appointments" class="form-control-hms" type="number" min="1" max="50" />
          </div>
          <div class="col-md-6">
            <label class="form-label-hms">Available?</label>
            <select v-model="slotForm.is_available" class="form-control-hms">
              <option :value="true">Yes</option>
              <option :value="false">No</option>
            </select>
          </div>
        </div>
        <div class="d-flex gap-2 mt-4">
          <button @click="saveSlot" class="btn-ink">Save Availability</button>
          <button @click="slotDate = null" class="btn-outline">Cancel</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { axios, API } from '../../store/auth'

const avails = ref([])
const slotDate = ref(null)
const slotForm = ref({ start_time: '09:00', end_time: '17:00', max_appointments: 10, is_available: true })

const next7Days = computed(() => {
  const days = []
  for (let i = 0; i < 7; i++) {
    const d = new Date()
    d.setDate(d.getDate() + i)
    days.push({
      iso: d.toISOString().split('T')[0],
      dayName: d.toLocaleDateString('en', { weekday: 'short' }),
      date: d.toLocaleDateString('en', { day: 'numeric', month: 'short' })
    })
  }
  return days
})

const hasAvail = (iso) => avails.value.some(a => a.date === iso)
const formatDate = (d) => new Date(d).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })

const openSlot = (iso) => {
  slotDate.value = iso
  const existing = avails.value.find(a => a.date === iso)
  if (existing) slotForm.value = { ...existing }
  else slotForm.value = { start_time: '09:00', end_time: '17:00', max_appointments: 10, is_available: true }
}

const saveSlot = async () => {
  await axios.post(`${API}/doctor/availability`, { ...slotForm.value, date: slotDate.value })
  slotDate.value = null
  await fetchAvails()
}

const fetchAvails = async () => {
  const { data } = await axios.get(`${API}/doctor/availability`)
  avails.value = data
}

onMounted(fetchAvails)
</script>

<style scoped>
.week-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 10px;
}

.day-card {
  background: var(--paper-off);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 12px 10px;
  text-align: center;
  transition: var(--transition);
}

.day-card.day-set {
  background: var(--ink);
  border-color: var(--ink);
}

.day-card.day-set .day-name,
.day-card.day-set .day-date { color: var(--paper); }

.day-card.day-set .btn-outline {
  background: rgba(255,255,255,0.1);
  color: var(--paper);
  border-color: rgba(255,255,255,0.2);
}

.day-name {
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--ink-faint);
}

.day-date {
  font-family: var(--font-display);
  font-size: 15px;
  font-weight: 700;
  margin-top: 2px;
}

@media (max-width: 768px) {
  .week-grid { grid-template-columns: repeat(4, 1fr); }
}
</style>
