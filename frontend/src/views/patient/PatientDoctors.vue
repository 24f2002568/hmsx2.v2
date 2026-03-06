<template>
  <div>
    <div class="topbar">
      <div class="topbar-title">Find Doctors</div>
    </div>
    <div class="content-area">
      <!-- Search -->
      <div class="card-hms mb-4">
        <div class="row g-3">
          <div class="col-md-8">
            <div class="search-wrap">
              <i class="bi bi-search"></i>
              <input v-model="search" @input="fetchDoctors" class="form-control-hms" placeholder="Search by doctor name..." />
            </div>
          </div>
          <div class="col-md-4">
            <select v-model="specFilter" @change="fetchDoctors" class="form-control-hms">
              <option value="">All Specializations</option>
              <option v-for="d in departments" :key="d.id" :value="d.name">{{ d.name }}</option>
            </select>
          </div>
        </div>
      </div>

      <div v-if="loading" class="loading-spinner"><div class="spinner-ring"></div></div>
      <div v-else-if="!doctors.length" class="empty-state">
        <i class="bi bi-person-badge"></i><p>NO DOCTORS FOUND</p>
      </div>
      <div v-else class="grid-3">
        <div v-for="doc in doctors" :key="doc.id" class="doctor-card" @click="openBook(doc)">
          <div class="d-flex align-items-center gap-3 mb-3">
            <div class="doctor-avatar">{{ doc.full_name[0] }}</div>
            <div>
              <div class="doctor-name">Dr. {{ doc.full_name }}</div>
              <div class="doctor-spec">{{ doc.specialization }}</div>
            </div>
          </div>
          <div class="d-flex justify-content-between align-items-center" style="font-size:13px; color:var(--ink-muted);">
            <span><i class="bi bi-star-fill" style="font-size:11px;"></i> {{ doc.experience_years }}yr exp</span>
            <span class="mono" style="font-weight:600; color:var(--ink);">₹{{ doc.consultation_fee }}</span>
          </div>
          <div class="mt-2">
            <span class="tag">{{ doc.department || 'General' }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Book Appointment Modal -->
    <div v-if="selectedDoc" class="modal-overlay" @click.self="selectedDoc = null">
      <div class="modal-box" style="max-width:580px;">
        <div class="modal-title">Book Appointment</div>
        <button @click="selectedDoc = null" class="modal-close"><i class="bi bi-x-lg"></i></button>

        <div class="d-flex gap-3 mb-4 p-3" style="background:var(--paper-off); border-radius:var(--radius); border:1px solid var(--border);">
          <div class="doctor-avatar">{{ selectedDoc.full_name[0] }}</div>
          <div>
            <div class="doctor-name">Dr. {{ selectedDoc.full_name }}</div>
            <div class="doctor-spec">{{ selectedDoc.specialization }}</div>
            <div style="font-size:12px; color:var(--ink-faint); margin-top:2px;">{{ selectedDoc.bio || 'Experienced specialist' }}</div>
          </div>
        </div>

        <div v-if="formError" class="alert-hms alert-error">{{ formError }}</div>

        <div class="form-group">
          <label class="form-label-hms">Select Date (Available Slots)</label>
          <div v-if="avails.length === 0" style="font-size:13px; color:var(--ink-faint); padding:10px 0;">
            No available dates found for this doctor.
          </div>
          <div class="slot-grid" v-else>
            <div v-for="av in avails" :key="av.id"
              :class="['slot-btn', { selected: bookForm.date === av.date, full: av.slots_remaining <= 0 }]"
              @click="av.slots_remaining > 0 && (bookForm.date = av.date)">
              <div style="font-weight:700;">{{ new Date(av.date).toLocaleDateString('en', { day: 'numeric', month: 'short' }) }}</div>
              <div style="font-size:10px; margin-top:2px;">{{ av.slots_remaining }} slots left</div>
            </div>
          </div>
        </div>

        <div v-if="bookForm.date" class="form-group">
          <label class="form-label-hms">Select Time</label>
          <div class="slot-grid">
            <div v-for="t in timeSlots" :key="t"
              :class="['slot-btn', { selected: bookForm.time === t }]"
              @click="bookForm.time = t">
              {{ t }}
            </div>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label-hms">Reason for Visit</label>
          <textarea v-model="bookForm.reason" class="form-control-hms" rows="2" placeholder="Describe your symptoms or concern..."></textarea>
        </div>

        <div class="d-flex gap-2">
          <button @click="bookAppointment" :disabled="booking" class="btn-ink">
            <span v-if="booking" class="spinner-ring" style="width:14px;height:14px;margin-right:4px;"></span>
            Confirm Booking
          </button>
          <button @click="selectedDoc = null" class="btn-outline">Cancel</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { axios, API } from '../../store/auth'

const route = useRoute()
const doctors = ref([])
const departments = ref([])
const loading = ref(true)
const search = ref('')
const specFilter = ref(route.query.specialization || '')

const selectedDoc = ref(null)
const avails = ref([])
const bookForm = ref({ date: '', time: '', reason: '' })
const booking = ref(false)
const formError = ref('')

const timeSlots = ['09:00', '09:30', '10:00', '10:30', '11:00', '11:30', '14:00', '14:30', '15:00', '15:30', '16:00', '16:30']

const fetchDoctors = async () => {
  const { data } = await axios.get(`${API}/patient/doctors`, {
    params: { search: search.value, specialization: specFilter.value }
  })
  doctors.value = data
}

const openBook = async (doc) => {
  selectedDoc.value = doc
  bookForm.value = { date: '', time: '', reason: '' }
  formError.value = ''
  const { data } = await axios.get(`${API}/patient/doctors/${doc.id}/availability`)
  avails.value = data
}

const bookAppointment = async () => {
  if (!bookForm.value.date || !bookForm.value.time) {
    formError.value = 'Please select a date and time'
    return
  }
  booking.value = true
  formError.value = ''
  try {
    await axios.post(`${API}/patient/appointments`, {
      doctor_id: selectedDoc.value.id, ...bookForm.value
    })
    selectedDoc.value = null
    alert('Appointment booked successfully!')
  } catch (e) {
    formError.value = e.response?.data?.error || 'Booking failed'
  } finally { booking.value = false }
}

onMounted(async () => {
  await Promise.all([fetchDoctors(), axios.get(`${API}/departments/`).then(r => departments.value = r.data)])
  loading.value = false
})
</script>
