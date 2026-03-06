<template>
  <div>
    <div class="topbar">
      <div class="topbar-title">Patients</div>
    </div>
    <div class="content-area">
      <div class="card-hms mb-4">
        <div class="search-wrap">
          <i class="bi bi-search"></i>
          <input v-model="search" @input="fetchPatients" class="form-control-hms"
            placeholder="Search by name, phone, or email..." />
        </div>
      </div>

      <div v-if="loading" class="loading-spinner"><div class="spinner-ring"></div> Loading...</div>
      <div v-else-if="!patients.length" class="empty-state">
        <i class="bi bi-people"></i><p>NO PATIENTS FOUND</p>
      </div>
      <div v-else class="card-hms">
        <table class="table-hms">
          <thead>
            <tr>
              <th>Patient</th>
              <th>Contact</th>
              <th>Blood Group</th>
              <th>Gender</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="p in patients" :key="p.id">
              <td>
                <div>
                  <div style="font-weight:600; font-size:13px;">{{ p.full_name }}</div>
                  <div class="text-mono" style="font-size:11px; color:var(--ink-faint);">{{ p.email }}</div>
                </div>
              </td>
              <td style="font-size:13px;">{{ p.phone || '—' }}</td>
              <td><span v-if="p.blood_group" class="tag">{{ p.blood_group }}</span><span v-else>—</span></td>
              <td style="font-size:13px; color:var(--ink-muted);">{{ p.gender || '—' }}</td>
              <td>
                <span :class="p.is_active ? 'badge-status badge-active' : 'badge-status badge-inactive'">
                  {{ p.is_active ? 'Active' : 'Blocked' }}
                </span>
              </td>
              <td>
                <div class="d-flex gap-2">
                  <button @click="openEdit(p)" class="btn-outline" style="padding:5px 10px; font-size:12px;">
                    <i class="bi bi-pencil"></i>
                  </button>
                  <button @click="togglePatient(p)" class="btn-danger" style="padding:5px 10px; font-size:12px;">
                    <i :class="p.is_active ? 'bi bi-slash-circle' : 'bi bi-check-circle'"></i>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="editPatient" class="modal-overlay" @click.self="editPatient = null">
      <div class="modal-box">
        <div class="modal-title">Edit Patient</div>
        <button @click="editPatient = null" class="modal-close"><i class="bi bi-x-lg"></i></button>
        <div class="row g-3">
          <div class="col-md-6">
            <label class="form-label-hms">Full Name</label>
            <input v-model="form.full_name" class="form-control-hms" />
          </div>
          <div class="col-md-6">
            <label class="form-label-hms">Phone</label>
            <input v-model="form.phone" class="form-control-hms" />
          </div>
          <div class="col-md-6">
            <label class="form-label-hms">Blood Group</label>
            <select v-model="form.blood_group" class="form-control-hms">
              <option v-for="bg in ['A+','A-','B+','B-','O+','O-','AB+','AB-']" :key="bg" :value="bg">{{ bg }}</option>
            </select>
          </div>
          <div class="col-12">
            <label class="form-label-hms">Address</label>
            <textarea v-model="form.address" class="form-control-hms" rows="2"></textarea>
          </div>
        </div>
        <div class="d-flex gap-2 mt-4">
          <button @click="savePatient" class="btn-ink">Save Changes</button>
          <button @click="editPatient = null" class="btn-outline">Cancel</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { axios, API } from '../../store/auth'

const patients = ref([])
const loading = ref(true)
const search = ref('')
const editPatient = ref(null)
const form = ref({})

const fetchPatients = async () => {
  const { data } = await axios.get(`${API}/admin/patients`, { params: { search: search.value } })
  patients.value = data
}

const openEdit = (p) => { editPatient.value = p; form.value = { ...p } }

const savePatient = async () => {
  await axios.put(`${API}/admin/patients/${editPatient.value.id}`, form.value)
  await fetchPatients()
  editPatient.value = null
}

const togglePatient = async (p) => {
  if (!confirm(`${p.is_active ? 'Block' : 'Activate'} ${p.full_name}?`)) return
  await axios.post(`${API}/admin/patients/${p.id}/toggle`)
  await fetchPatients()
}

onMounted(async () => { await fetchPatients(); loading.value = false })
</script>
