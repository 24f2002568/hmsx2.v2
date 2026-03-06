<template>
  <div class="auth-page">
    <div class="auth-bg-lines"></div>
    <div class="auth-form-area" style="max-width:560px; margin:0 auto; width:100%; padding:40px 20px;">
      <div class="auth-card">
        <div class="auth-brand">MEDIX</div>
        <div class="auth-tagline">Patient Registration</div>

        <div v-if="error" class="alert-hms alert-error">{{ error }}</div>
        <div v-if="success" class="alert-hms alert-success">{{ success }}</div>

        <div class="row g-3">
          <div class="col-12">
            <div class="form-group">
              <label class="form-label-hms">Full Name *</label>
              <input v-model="form.full_name" class="form-control-hms" placeholder="John Doe" />
            </div>
          </div>
          <div class="col-md-6">
            <div class="form-group">
              <label class="form-label-hms">Username *</label>
              <input v-model="form.username" class="form-control-hms" placeholder="johndoe" />
            </div>
          </div>
          <div class="col-md-6">
            <div class="form-group">
              <label class="form-label-hms">Email *</label>
              <input v-model="form.email" class="form-control-hms" type="email" placeholder="john@email.com" />
            </div>
          </div>
          <div class="col-md-6">
            <div class="form-group">
              <label class="form-label-hms">Password *</label>
              <input v-model="form.password" class="form-control-hms" type="password" placeholder="••••••••" />
            </div>
          </div>
          <div class="col-md-6">
            <div class="form-group">
              <label class="form-label-hms">Phone</label>
              <input v-model="form.phone" class="form-control-hms" placeholder="+91 9876543210" />
            </div>
          </div>
          <div class="col-md-6">
            <div class="form-group">
              <label class="form-label-hms">Date of Birth</label>
              <input v-model="form.dob" class="form-control-hms" type="date" />
            </div>
          </div>
          <div class="col-md-6">
            <div class="form-group">
              <label class="form-label-hms">Gender</label>
              <select v-model="form.gender" class="form-control-hms">
                <option value="">Select</option>
                <option>Male</option>
                <option>Female</option>
                <option>Other</option>
              </select>
            </div>
          </div>
        </div>

        <button @click="handleRegister" :disabled="loading" class="btn-ink w-100 mt-3"
          style="justify-content:center; padding:13px;">
          <span v-if="loading" class="spinner-ring" style="width:16px;height:16px;margin-right:6px;"></span>
          {{ loading ? 'Creating Account...' : 'Create Account' }}
        </button>

        <div class="text-center mt-3">
          <router-link to="/login" style="font-size:13px; color:var(--ink-faint); text-decoration:none;">
            Already have an account? <strong>Sign in</strong>
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../store/auth'

const router = useRouter()
const auth = useAuthStore()

const form = ref({ username: '', email: '', password: '', full_name: '', phone: '', dob: '', gender: '' })
const loading = ref(false)
const error = ref('')
const success = ref('')

const handleRegister = async () => {
  if (!form.value.username || !form.value.email || !form.value.password || !form.value.full_name) {
    error.value = 'Please fill all required fields'
    return
  }
  loading.value = true
  error.value = ''
  try {
    await auth.register(form.value)
    success.value = 'Account created! Redirecting to login...'
    setTimeout(() => router.push('/login'), 2000)
  } catch (e) {
    error.value = e
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  background: var(--ink);
  display: flex;
  align-items: center;
  justify-content: center;
}

.auth-card {
  background: var(--paper);
  padding: 36px;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
}
</style>
