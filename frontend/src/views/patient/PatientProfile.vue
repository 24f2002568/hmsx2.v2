<template>
  <div>
    <div class="topbar"><div class="topbar-title">My Profile</div></div>
    <div class="content-area">
      <div v-if="loading" class="loading-spinner"><div class="spinner-ring"></div></div>
      <div v-else class="row g-4">
        <div class="col-md-4">
          <div class="card-hms text-center">
            <div class="profile-avatar">{{ profile?.full_name?.[0] }}</div>
            <div style="font-family:var(--font-display); font-size:20px; font-weight:700; margin:12px 0 4px;">{{ profile?.full_name }}</div>
            <div class="mono" style="font-size:10px; letter-spacing:0.15em; color:var(--ink-faint);">PATIENT ID #{{ profile?.id }}</div>
            <div class="mt-3 d-flex flex-column gap-2" style="font-size:13px; color:var(--ink-muted);">
              <div><i class="bi bi-envelope me-2"></i>{{ profile?.email }}</div>
              <div v-if="profile?.phone"><i class="bi bi-phone me-2"></i>{{ profile.phone }}</div>
              <div v-if="profile?.blood_group"><i class="bi bi-droplet me-2"></i>{{ profile.blood_group }}</div>
            </div>
          </div>
        </div>
        <div class="col-md-8">
          <div class="card-hms">
            <div class="section-header">
              <div class="section-title">Edit Profile</div>
            </div>
            <div v-if="success" class="alert-hms alert-success">Profile updated!</div>
            <div v-if="error" class="alert-hms alert-error">{{ error }}</div>
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
                <label class="form-label-hms">Date of Birth</label>
                <input v-model="form.dob" class="form-control-hms" type="date" />
              </div>
              <div class="col-md-6">
                <label class="form-label-hms">Gender</label>
                <select v-model="form.gender" class="form-control-hms">
                  <option value="">Select</option>
                  <option>Male</option><option>Female</option><option>Other</option>
                </select>
              </div>
              <div class="col-md-6">
                <label class="form-label-hms">Blood Group</label>
                <select v-model="form.blood_group" class="form-control-hms">
                  <option value="">Select</option>
                  <option v-for="bg in ['A+','A-','B+','B-','O+','O-','AB+','AB-']" :key="bg">{{ bg }}</option>
                </select>
              </div>
              <div class="col-md-6">
                <label class="form-label-hms">Emergency Contact</label>
                <input v-model="form.emergency_contact" class="form-control-hms" />
              </div>
              <div class="col-12">
                <label class="form-label-hms">Address</label>
                <textarea v-model="form.address" class="form-control-hms" rows="2"></textarea>
              </div>
            </div>
            <button @click="saveProfile" :disabled="saving" class="btn-ink mt-4">
              <span v-if="saving" class="spinner-ring" style="width:14px;height:14px;margin-right:4px;"></span>
              Save Changes
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { axios, API } from '../../store/auth'

const profile = ref(null)
const form = ref({})
const loading = ref(true)
const saving = ref(false)
const success = ref(false)
const error = ref('')

const saveProfile = async () => {
  saving.value = true
  success.value = false
  error.value = ''
  try {
    const { data } = await axios.put(`${API}/patient/profile`, form.value)
    profile.value = data
    success.value = true
  } catch (e) {
    error.value = e.response?.data?.error || 'Update failed'
  } finally { saving.value = false }
}

onMounted(async () => {
  const { data } = await axios.get(`${API}/patient/profile`)
  profile.value = data.profile
  form.value = { ...data.profile }
  loading.value = false
})
</script>

<style scoped>
.profile-avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: var(--ink);
  color: var(--paper);
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-display);
  font-size: 32px;
  font-weight: 800;
  margin: 0 auto;
}
</style>
