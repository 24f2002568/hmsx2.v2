<template>
  <div>
    <div class="topbar">
      <div class="topbar-title">Doctors</div>
      <button @click="showAddModal = true" class="btn-ink">
        <i class="bi bi-plus-lg"></i> Add Doctor
      </button>
    </div>
    <div class="content-area">
      <!-- Search -->
      <div class="card-hms mb-4">
        <div class="search-wrap">
          <i class="bi bi-search"></i>
          <input v-model="search" @input="fetchDoctors" class="form-control-hms"
            placeholder="Search by name or specialization..." />
        </div>
      </div>

      <div v-if="loading" class="loading-spinner"><div class="spinner-ring"></div> Loading...</div>

      <div v-else-if="!doctors.length" class="empty-state">
        <i class="bi bi-person-badge"></i>
        <p>NO DOCTORS FOUND</p>
      </div>

      <div v-else class="card-hms">
        <table class="table-hms">
          <thead>
            <tr>
              <th>Doctor</th>
              <th>Specialization</th>
              <th>Department</th>
              <th>Contact</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="doc in doctors" :key="doc.id">
              <td>
                <div class="d-flex align-items-center gap-2">
                  <div class="doctor-avatar" style="width:36px;height:36px;font-size:14px;">
                    {{ doc.full_name[0] }}
                  </div>
                  <div>
                    <div style="font-weight:600; font-size:13px;">{{ doc.full_name }}</div>
                    <div class="text-mono" style="font-size:11px; color:var(--ink-faint);">{{ doc.email }}</div>
                  </div>
                </div>
              </td>
              <td><span class="tag">{{ doc.specialization }}</span></td>
              <td style="color:var(--ink-muted); font-size:13px;">{{ doc.department || '—' }}</td>
              <td style="font-size:13px;">{{ doc.phone || '—' }}</td>
              <td>
                <span :class="doc.is_active ? 'badge-status badge-active' : 'badge-status badge-inactive'">
                  {{ doc.is_active ? 'Active' : 'Blocked' }}
                </span>
              </td>
              <td>
                <div class="d-flex gap-2">
                  <button @click="openEdit(doc)" class="btn-outline" style="padding:5px 10px; font-size:12px;">
                    <i class="bi bi-pencil"></i>
                  </button>
                  <button @click="toggleDoctor(doc)" class="btn-danger" style="padding:5px 10px; font-size:12px;">
                    <i :class="doc.is_active ? 'bi bi-slash-circle' : 'bi bi-check-circle'"></i>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Add/Edit Modal -->
    <div v-if="showAddModal || editDoctor" class="modal-overlay" @click.self="closeModal">
      <div class="modal-box">
        <div class="modal-title">{{ editDoctor ? 'Edit Doctor' : 'Add New Doctor' }}</div>
        <button @click="closeModal" class="modal-close"><i class="bi bi-x-lg"></i></button>

        <div v-if="formError" class="alert-hms alert-error">{{ formError }}</div>

        <div class="row g-3">
          <div class="col-md-6">
            <label class="form-label-hms">Full Name *</label>
            <input v-model="form.full_name" class="form-control-hms" />
          </div>
          <div class="col-md-6" v-if="!editDoctor">
            <label class="form-label-hms">Username *</label>
            <input v-model="form.username" class="form-control-hms" />
          </div>
          <div class="col-md-6">
            <label class="form-label-hms">Email *</label>
            <input v-model="form.email" class="form-control-hms" type="email" />
          </div>
          <div class="col-md-6" v-if="!editDoctor">
            <label class="form-label-hms">Password</label>
            <input v-model="form.password" class="form-control-hms" placeholder="doctor@123" />
          </div>
          <div class="col-md-6">
            <label class="form-label-hms">Specialization</label>
            <input v-model="form.specialization" class="form-control-hms" />
          </div>
          <div class="col-md-6">
            <label class="form-label-hms">Department</label>
            <select v-model="form.department_id" class="form-control-hms">
              <option value="">Select</option>
              <option v-for="d in departments" :key="d.id" :value="d.id">{{ d.name }}</option>
            </select>
          </div>
          <div class="col-md-6">
            <label class="form-label-hms">Phone</label>
            <input v-model="form.phone" class="form-control-hms" />
          </div>
          <div class="col-md-6">
            <label class="form-label-hms">Experience (years)</label>
            <input v-model.number="form.experience_years" class="form-control-hms" type="number" min="0" />
          </div>
          <div class="col-md-6">
            <label class="form-label-hms">Consultation Fee (₹)</label>
            <input v-model.number="form.consultation_fee" class="form-control-hms" type="number" min="0" />
          </div>
          <div class="col-12">
            <label class="form-label-hms">Bio</label>
            <textarea v-model="form.bio" class="form-control-hms" rows="2"></textarea>
          </div>
        </div>

        <div class="d-flex gap-2 mt-4">
          <button @click="saveDoctor" :disabled="saving" class="btn-ink">
            <span v-if="saving" class="spinner-ring" style="width:14px;height:14px;margin-right:4px;"></span>
            {{ editDoctor ? 'Update' : 'Add Doctor' }}
          </button>
          <button @click="closeModal" class="btn-outline">Cancel</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { axios, API } from '../../store/auth'

const doctors = ref([])
const departments = ref([])
const loading = ref(true)
const search = ref('')
const showAddModal = ref(false)
const editDoctor = ref(null)
const saving = ref(false)
const formError = ref('')
const form = ref({ full_name: '', username: '', email: '', password: 'doctor@123', specialization: '', department_id: '', phone: '', experience_years: 0, consultation_fee: 0, bio: '' })

const fetchDoctors = async () => {
  const { data } = await axios.get(`${API}/admin/doctors`, { params: { search: search.value } })
  doctors.value = data
}

const fetchDepts = async () => {
  const { data } = await axios.get(`${API}/departments/`)
  departments.value = data
}

const openEdit = (doc) => {
  editDoctor.value = doc
  form.value = { ...doc }
}

const closeModal = () => {
  showAddModal.value = false
  editDoctor.value = null
  formError.value = ''
  form.value = { full_name: '', username: '', email: '', password: 'doctor@123', specialization: '', department_id: '', phone: '', experience_years: 0, consultation_fee: 0, bio: '' }
}

const saveDoctor = async () => {
  if (!form.value.full_name || !form.value.email) { formError.value = 'Fill required fields'; return }
  saving.value = true
  formError.value = ''
  try {
    if (editDoctor.value) {
      await axios.put(`${API}/admin/doctors/${editDoctor.value.id}`, form.value)
    } else {
      await axios.post(`${API}/admin/doctors`, form.value)
    }
    await fetchDoctors()
    closeModal()
  } catch (e) {
    formError.value = e.response?.data?.error || 'Error saving'
  } finally { saving.value = false }
}

const toggleDoctor = async (doc) => {
  if (!confirm(`${doc.is_active ? 'Block' : 'Activate'} Dr. ${doc.full_name}?`)) return
  await axios.post(`${API}/admin/doctors/${doc.id}/toggle`)
  await fetchDoctors()
}

onMounted(async () => {
  await Promise.all([fetchDoctors(), fetchDepts()])
  loading.value = false
})
</script>
