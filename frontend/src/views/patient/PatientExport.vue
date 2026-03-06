<template>
  <div>
    <div class="topbar"><div class="topbar-title">Export & Reports</div></div>
    <div class="content-area">

      <!-- CSV Export Card -->
      <div class="card-hms mb-4">
        <div class="section-header">
          <div class="section-title">Treatment History Export</div>
        </div>
        <div class="export-hero">
          <div class="export-icon"><i class="bi bi-file-earmark-spreadsheet"></i></div>
          <div>
            <div style="font-family:var(--font-display); font-size:16px; font-weight:700; margin-bottom:6px;">
              Export as CSV
            </div>
            <div style="font-size:13px; color:var(--ink-muted); line-height:1.6; margin-bottom:16px;">
              Download your complete treatment history including appointments, diagnoses,
              prescriptions, and doctor notes. You'll get an email notification when it's ready.
            </div>
            <div class="d-flex gap-3 align-items-center flex-wrap">
              <button @click="triggerExport" :disabled="exporting || !canExport"
                class="btn-ink" style="padding:10px 20px;">
                <span v-if="exporting" class="spinner-ring" style="width:14px;height:14px;margin-right:6px;"></span>
                <i v-else class="bi bi-cloud-arrow-down me-2"></i>
                {{ exporting ? 'Preparing...' : 'Generate Export' }}
              </button>
              <a v-if="exportReady" :href="`/api/jobs/export-csv/download`" class="btn-outline"
                style="padding:9px 18px;">
                <i class="bi bi-download me-2"></i> Download CSV
              </a>
            </div>
          </div>
        </div>

        <!-- Export status tracking -->
        <div v-if="currentTask" class="task-tracker mt-4">
          <div class="task-tracker-label">EXPORT STATUS</div>
          <div class="task-tracker-bar">
            <div class="task-tracker-fill" :class="currentTask.status.toLowerCase()"></div>
          </div>
          <div class="task-tracker-status">
            <span class="mono" style="font-size:11px; color:var(--ink-faint);">{{ currentTask.task_id }}</span>
            <span :class="['task-status-badge', currentTask.status.toLowerCase()]">
              {{ currentTask.status }}
            </span>
          </div>
          <div v-if="currentTask.result" class="mt-2" style="font-size:13px; color:var(--ink-muted);">
            ✓ Export ready — {{ currentTask.result.records }} records
          </div>
        </div>

        <div v-if="exportError" class="alert-hms alert-error mt-3">{{ exportError }}</div>
        <div v-if="exportReady" class="alert-hms alert-success mt-3">
          Export ready! Click "Download CSV" above. An email has also been sent to you.
        </div>
      </div>

      <!-- What's included -->
      <div class="card-hms">
        <div class="section-title mb-3" style="font-size:16px;">What's Included in the Export</div>
        <div class="grid-2">
          <div v-for="field in exportFields" :key="field.label" class="field-item">
            <i :class="field.icon" style="width:18px;"></i>
            <div>
              <div style="font-weight:600; font-size:13px;">{{ field.label }}</div>
              <div style="font-size:12px; color:var(--ink-faint);">{{ field.desc }}</div>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { axios, API } from '../../store/auth'

const exporting = ref(false)
const exportReady = ref(false)
const exportError = ref('')
const canExport = ref(true)
const currentTask = ref(null)

const exportFields = [
  { icon: 'bi bi-hash', label: 'Appointment ID', desc: 'Unique appointment reference' },
  { icon: 'bi bi-calendar3', label: 'Date & Time', desc: 'When the appointment occurred' },
  { icon: 'bi bi-person-badge', label: 'Doctor & Specialization', desc: 'Treating physician details' },
  { icon: 'bi bi-clipboard2-pulse', label: 'Diagnosis', desc: 'Medical diagnosis given' },
  { icon: 'bi bi-capsule', label: 'Prescription', desc: 'Medications prescribed' },
  { icon: 'bi bi-journal-text', label: 'Notes', desc: "Doctor's consultation notes" },
  { icon: 'bi bi-calendar-check', label: 'Next Visit', desc: 'Recommended follow-up date' },
  { icon: 'bi bi-activity', label: 'Status', desc: 'Appointment status (Booked/Completed/Cancelled)' },
]

const triggerExport = async () => {
  exporting.value = true
  exportReady.value = false
  exportError.value = ''
  canExport.value = false
  currentTask.value = null

  try {
    const { data } = await axios.post(`${API}/jobs/export-csv`)
    currentTask.value = { task_id: data.task_id, status: 'PENDING', result: null }

    // Poll for completion
    for (let i = 0; i < 20; i++) {
      await new Promise(r => setTimeout(r, 2000))
      try {
        const { data: statusData } = await axios.get(`${API}/jobs/task-status/${data.task_id}`)
        currentTask.value.status = statusData.status

        if (statusData.status === 'SUCCESS') {
          currentTask.value.result = statusData.result
          exportReady.value = true
          break
        }
        if (statusData.status === 'FAILURE') {
          exportError.value = 'Export failed. Please try again.'
          break
        }
      } catch {}
    }
  } catch (e) {
    exportError.value = e.response?.data?.error || 'Failed to start export'
  } finally {
    exporting.value = false
    setTimeout(() => { canExport.value = true }, 10000)
  }
}
</script>

<style scoped>
.export-hero {
  display: flex;
  gap: 20px;
  align-items: flex-start;
}

.export-icon {
  width: 64px; height: 64px;
  background: var(--ink);
  border-radius: var(--radius-lg);
  display: flex; align-items: center; justify-content: center;
  color: var(--paper);
  font-size: 28px;
  flex-shrink: 0;
}

.task-tracker {
  background: var(--paper-off);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 16px;
}

.task-tracker-label {
  font-family: var(--font-mono);
  font-size: 9px;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--ink-faint);
  margin-bottom: 8px;
}

.task-tracker-bar {
  height: 4px;
  background: var(--border);
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: 10px;
}

.task-tracker-fill {
  height: 100%;
  border-radius: 2px;
  transition: all 0.5s ease;
}
.task-tracker-fill.pending { width: 30%; background: #888; animation: shimmer 1.5s infinite; }
.task-tracker-fill.started { width: 60%; background: #888; animation: shimmer 1.5s infinite; }
.task-tracker-fill.success { width: 100%; background: #1a6b1a; }
.task-tracker-fill.failure { width: 100%; background: #c00; }

@keyframes shimmer {
  0%,100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.task-tracker-status { display: flex; justify-content: space-between; align-items: center; }

.task-status-badge {
  font-family: var(--font-mono); font-size: 10px;
  letter-spacing: 0.1em; text-transform: uppercase;
  padding: 2px 8px; border-radius: 20px; border: 1px solid;
}
.task-status-badge.pending  { background: #f5f5f5; color: #666; border-color: #ddd; }
.task-status-badge.success  { background: #f5fff5; color: #1a6b1a; border-color: #b8d8b8; }
.task-status-badge.failure  { background: #fff5f5; color: #9b2020; border-color: #e5b0b0; }
.task-status-badge.started  { background: #f5f5f5; color: #333; border-color: #ccc; }

.field-item {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  padding: 10px;
  background: var(--paper-off);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  font-size: 13px;
}
</style>
