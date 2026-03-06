<template>
  <div>
    <div class="topbar">
      <div class="topbar-title">Departments</div>
      <button @click="showModal = true" class="btn-ink"><i class="bi bi-plus-lg"></i> Add Department</button>
    </div>
    <div class="content-area">
      <div v-if="loading" class="loading-spinner"><div class="spinner-ring"></div></div>
      <div v-else class="grid-3">
        <div v-for="d in departments" :key="d.id" class="card-hms">
          <div style="font-family:var(--font-display); font-size:17px; font-weight:700; margin-bottom:6px;">{{ d.name }}</div>
          <div style="font-size:13px; color:var(--ink-muted); margin-bottom:12px;">{{ d.description }}</div>
          <div class="d-flex align-items-center justify-content-between">
            <span class="mono" style="font-size:12px; color:var(--ink-faint);">{{ d.doctors_count }} doctor(s)</span>
            <button @click="openEdit(d)" class="btn-outline" style="padding:4px 10px; font-size:12px;">Edit</button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showModal || editDept" class="modal-overlay" @click.self="closeModal">
      <div class="modal-box">
        <div class="modal-title">{{ editDept ? 'Edit Department' : 'Add Department' }}</div>
        <button @click="closeModal" class="modal-close"><i class="bi bi-x-lg"></i></button>
        <div class="form-group">
          <label class="form-label-hms">Department Name *</label>
          <input v-model="form.name" class="form-control-hms" />
        </div>
        <div class="form-group">
          <label class="form-label-hms">Description</label>
          <textarea v-model="form.description" class="form-control-hms" rows="3"></textarea>
        </div>
        <div class="d-flex gap-2">
          <button @click="saveDept" class="btn-ink">{{ editDept ? 'Update' : 'Add' }}</button>
          <button @click="closeModal" class="btn-outline">Cancel</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { axios, API } from '../../store/auth'

const departments = ref([])
const loading = ref(true)
const showModal = ref(false)
const editDept = ref(null)
const form = ref({ name: '', description: '' })

const fetchDepts = async () => {
  const { data } = await axios.get(`${API}/departments/`)
  departments.value = data
}

const openEdit = (d) => { editDept.value = d; form.value = { ...d } }
const closeModal = () => { showModal.value = false; editDept.value = null; form.value = { name: '', description: '' } }

const saveDept = async () => {
  if (!form.value.name) return
  if (editDept.value) {
    await axios.put(`${API}/departments/${editDept.value.id}`, form.value)
  } else {
    await axios.post(`${API}/departments/`, form.value)
  }
  await fetchDepts()
  closeModal()
}

onMounted(async () => { await fetchDepts(); loading.value = false })
</script>
