<template>
  <div class="auth-page">
    <div class="auth-bg-lines"></div>

    <div class="auth-panel-left">
      <div class="pulse-ring"></div>
      <div class="auth-panel-content">
        <div class="panel-symbol">⊕</div>
        <h1 class="panel-headline">Modern<br/>Healthcare<br/>Management</h1>
        <p class="panel-sub">Connecting doctors, patients,<br/>and administrators in one platform.</p>
      </div>
    </div>

    <div class="auth-form-area">
      <div class="auth-card">
        <div class="auth-brand">MEDIX</div>
        <div class="auth-tagline">Hospital Management System</div>

        <div v-if="error" class="alert-hms alert-error">
          <i class="bi bi-exclamation-triangle me-2"></i>{{ error }}
        </div>

        <div class="form-group">
          <label class="form-label-hms">Username</label>
          <input v-model="form.username" class="form-control-hms" type="text"
            placeholder="Enter your username" @keyup.enter="handleLogin" />
        </div>

        <div class="form-group">
          <label class="form-label-hms">Password</label>
          <div style="position:relative">
            <input v-model="form.password" class="form-control-hms"
              :type="showPw ? 'text' : 'password'"
              placeholder="Enter your password" @keyup.enter="handleLogin" />
            <button @click="showPw = !showPw" class="pw-toggle">
              <i :class="showPw ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
            </button>
          </div>
        </div>

        <button @click="handleLogin" :disabled="loading" class="btn-ink w-100 mt-2"
          style="justify-content:center; padding:13px;">
          <span v-if="loading" class="spinner-ring" style="width:16px;height:16px;margin-right:6px;"></span>
          {{ loading ? 'Signing in...' : 'Sign In' }}
        </button>

        <div class="auth-divider">
          <span>New patient?</span>
        </div>

        <router-link to="/register" class="btn-outline w-100" style="justify-content:center; padding:11px;">
          Create Account
        </router-link>

        <div class="demo-credentials">
          <div class="demo-label">Demo Credentials</div>
          <div class="demo-grid">
            <div class="demo-item" @click="fillDemo('admin', 'admin@123')">
              <span class="demo-role">ADMIN</span>
              <span>admin / admin@123</span>
            </div>
          </div>
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

const form = ref({ username: '', password: '' })
const loading = ref(false)
const error = ref('')
const showPw = ref(false)

const fillDemo = (u, p) => { form.value.username = u; form.value.password = p }

const handleLogin = async () => {
  if (!form.value.username || !form.value.password) {
    error.value = 'Please enter username and password'
    return
  }
  loading.value = true
  error.value = ''
  try {
    const user = await auth.login(form.value.username, form.value.password)
    const redirectMap = { admin: '/admin/dashboard', doctor: '/doctor/dashboard', patient: '/patient/dashboard' }
    router.push(redirectMap[user.role] || '/login')
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
  align-items: stretch;
}

.auth-panel-left {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px;
  position: relative;
  overflow: hidden;
}

.pulse-ring {
  position: absolute;
  width: 500px;
  height: 500px;
  border: 1px solid rgba(255,255,255,0.05);
  border-radius: 50%;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
}

.pulse-ring::before, .pulse-ring::after {
  content: '';
  position: absolute;
  inset: -80px;
  border: 1px solid rgba(255,255,255,0.03);
  border-radius: 50%;
}

.pulse-ring::after { inset: -160px; }

.auth-panel-content { position: relative; }

.panel-symbol {
  font-size: 48px;
  color: rgba(255,255,255,0.15);
  margin-bottom: 24px;
  line-height: 1;
}

.panel-headline {
  font-family: var(--font-display);
  font-size: 48px;
  font-weight: 800;
  color: var(--paper);
  line-height: 1.1;
  margin-bottom: 20px;
}

.panel-sub {
  font-family: var(--font-body);
  font-size: 15px;
  color: rgba(255,255,255,0.4);
  line-height: 1.7;
}

.auth-form-area {
  width: 440px;
  background: var(--paper-off);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.auth-card {
  background: var(--paper);
  width: 100%;
  padding: 36px;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
}

.auth-brand {
  font-family: var(--font-display);
  font-size: 26px;
  font-weight: 800;
  letter-spacing: 0.12em;
  color: var(--ink);
}

.auth-tagline {
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--ink-faint);
  margin-bottom: 28px;
}

.pw-toggle {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  color: var(--ink-faint);
  padding: 4px;
  font-size: 15px;
}

.auth-divider {
  text-align: center;
  margin: 20px 0;
  position: relative;
  color: var(--ink-faint);
  font-family: var(--font-mono);
  font-size: 11px;
  letter-spacing: 0.1em;
}

.auth-divider::before, .auth-divider::after {
  content: '';
  position: absolute;
  top: 50%;
  width: 35%;
  height: 1px;
  background: var(--border);
}

.auth-divider::before { left: 0; }
.auth-divider::after { right: 0; }

.demo-credentials {
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid var(--border);
}

.demo-label {
  font-family: var(--font-mono);
  font-size: 9px;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--ink-faint);
  margin-bottom: 8px;
}

.demo-grid { display: flex; flex-direction: column; gap: 6px; }

.demo-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  background: var(--paper-off);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  cursor: pointer;
  font-size: 12px;
  color: var(--ink-muted);
  transition: var(--transition);
}

.demo-item:hover { border-color: var(--ink); color: var(--ink); }

.demo-role {
  font-family: var(--font-mono);
  font-size: 9px;
  letter-spacing: 0.1em;
  background: var(--ink);
  color: var(--paper);
  padding: 2px 6px;
  border-radius: 2px;
}

@media (max-width: 900px) {
  .auth-panel-left { display: none; }
  .auth-form-area { width: 100%; }
}
</style>