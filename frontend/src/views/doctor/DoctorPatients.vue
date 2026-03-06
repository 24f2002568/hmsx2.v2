<template>
  <div>
    <div class="topbar"><div class="topbar-title">My Patients</div></div>
    <div class="content-area">
      <div v-if="loading" class="loading-spinner"><div class="spinner-ring"></div></div>
      <div v-else-if="!patients.length" class="empty-state">
        <i class="bi bi-people"></i><p>NO PATIENTS YET</p>
      </div>
      <div v-else class="grid-3">
        <div v-for="p in patients" :key="p.id" class="card-hms" style="cursor:pointer;"
          @click="openHistory(p)">
          <div class="d-flex align-items-center gap-3 mb-3">
            <div class="doctor-avatar">{{ p.full_name[0] }}</div>
            <div>
              <div class="doctor-name">{{ p.full_name }}</div>
              <div class="doctor-spec">{{ p.gender }} · {{ p.blood_group || 'Blood N/A' }}</div>
            </div>
          </div>
          <div style="font-size:13px; color:var(--ink-faint);">{{ p.phone || p.email }}</div>
        </div>
      </div>
    </div>

    <div v-if="selectedPatient" class="modal-overlay" @click.self="selectedPatient = null">
      <div class="modal-box" style="max-width:640px;">
        <div class="modal-title">{{ selectedPatient.full_name }} — Treatment History</div>
        <button @click="selectedPatient = null" class="modal-close"><i class="bi bi-x-lg"></i></button>
        <div v-if="historyLoading" class="loading-spinner" style="padding:20px;">
          <div class="spinner-ring"></div>
        </div>
        <div v-else-if="!history.length" class="empty-state" style="padding:20px 0;">
          <p>NO HISTORY</p>
        </div>
        <div v-else>
          <div v-for="a in history" :key="a.id" class="history-item">
            <div class="d-flex justify-content-between align-items-center mb-2">
              <div style="font-weight:700;">{{ formatDate(a.date) }} at {{ a.time }}</div>
              <span :class="`badge-status badge-${a.status.toLowerCase()}`">{{ a.status }}</span>
            </div>
            <div v-if="a.treatment" class="treatment-record">
              <div class="row">
                <div class="col-md-6">
                  <div class="treatment-field"><label>Diagnosis</label><p>{{ a.treatment.diagnosis }}</p></div>
                </div>
                <div class="col-md-6">
                  <div class="treatment-field"><label>Prescription</label><p>{{ a.treatment.prescription }}</p></div>
                </div>
              </div>
              <div class="treatment-field"><label>Notes</label><p>{{ a.treatment.notes || '—' }}</p></div>
            </div>
            <div v-else style="font-size:13px; color:var(--ink-faint);">No treatment record</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { axios, API } from '../../store/auth'

const patients = ref([])
const loading = ref(true)
const selectedPatient = ref(null)
const history = ref([])
const historyLoading = ref(false)

const formatDate = (d) => new Date(d).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })

const openHistory = async (p) => {
  selectedPatient.value = p
  historyLoading.value = true
  const { data } = await axios.get(`${API}/doctor/patients/${p.id}/history`)
  history.value = data
  historyLoading.value = false
}

onMounted(async () => {
  const { data } = await axios.get(`${API}/doctor/patients`)
  patients.value = data
  loading.value = false
})
</script>

<style scoped>
.history-item {
  padding: 16px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  margin-bottom: 10px;
}
</style>
