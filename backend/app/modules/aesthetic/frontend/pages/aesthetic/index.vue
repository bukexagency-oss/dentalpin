<script setup lang="ts">
import { PERMISSIONS } from '~~/app/config/permissions'
import { useAesthetic, type ConsultationNote, type PhotoJourney } from '../../composables/useAesthetic'

definePageMeta({ middleware: ['auth'] })

const { t } = useI18n()
const { can } = usePermissions()
const toast = useToast()
const api = useAesthetic()

if (!can(PERMISSIONS.aesthetic.read)) await navigateTo('/')

const canWrite = computed(() => can(PERMISSIONS.aesthetic.write))

// --- Tab state ------------------------------------------------------------
const activeTab = ref(0)
const TABS = [
  { key: 'consultations', label: t('aesthetic.consultations'), icon: 'i-lucide-notebook' },
  { key: 'photos', label: t('aesthetic.photos'), icon: 'i-lucide-camera' },
  { key: 'treatments', label: t('aesthetic.treatments'), icon: 'i-lucide-activity' },
  { key: 'recommendations', label: t('aesthetic.recommendations'), icon: 'i-lucide-star' }
]

// --- Consultations --------------------------------------------------------
const consultations = ref<ConsultationNote[]>([])
const consultationsLoading = ref(false)
const consultationsTotal = ref(0)
const consultationsPage = ref(1)
const PAGE_SIZE = 20

async function loadConsultations() {
  consultationsLoading.value = true
  try {
    const res = await api.listConsultations(undefined, consultationsPage.value, PAGE_SIZE)
    consultations.value = res.data
    consultationsTotal.value = res.total
  } catch {
    toast.add({ title: t('aesthetic.error'), color: 'red' })
  } finally {
    consultationsLoading.value = false
  }
}

const showNewConsultation = ref(false)
const newConsultation = ref({ patient_id: '', consultation_type: 'initial', findings: '', recommendations: '', skin_analysis: '' })

async function submitConsultation() {
  try {
    await api.createConsultation(newConsultation.value)
    toast.add({ title: 'Consultation created', color: 'green' })
    showNewConsultation.value = false
    newConsultation.value = { patient_id: '', consultation_type: 'initial', findings: '', recommendations: '', skin_analysis: '' }
    await loadConsultations()
  } catch {
    toast.add({ title: 'Failed to create consultation', color: 'red' })
  }
}

// --- Photos ---------------------------------------------------------------
const photos = ref<PhotoJourney[]>([])
const photosLoading = ref(false)
const photosTotal = ref(0)
const photosPage = ref(1)

async function loadPhotos() {
  photosLoading.value = true
  try {
    const res = await api.listPhotos(undefined, photosPage.value, PAGE_SIZE)
    photos.value = res.data
    photosTotal.value = res.total
  } catch {
    toast.add({ title: t('aesthetic.error'), color: 'red' })
  } finally {
    photosLoading.value = false
  }
}

const showNewPhoto = ref(false)
const newPhoto = ref({ patient_id: '', photo_type: 'before', photo_url: '', notes: '' })

async function submitPhoto() {
  try {
    await api.createPhoto(newPhoto.value)
    toast.add({ title: 'Photo added', color: 'green' })
    showNewPhoto.value = false
    newPhoto.value = { patient_id: '', photo_type: 'before', photo_url: '', notes: '' }
    await loadPhotos()
  } catch {
    toast.add({ title: 'Failed to add photo', color: 'red' })
  }
}

// --- Init ----------------------------------------------------------------
onMounted(() => {
  loadConsultations()
  loadPhotos()
})
</script>

<template>
  <div class="p-6">
    <h1 class="text-2xl font-bold mb-4">{{ t('aesthetic.title') }}</h1>

    <UTabs v-model="activeTab" :items="TABS" class="mb-4" />

    <!-- Tab: Consultations -->
    <div v-if="activeTab === 0">
      <div class="flex justify-between mb-3">
        <h2 class="text-lg font-semibold">{{ t('aesthetic.consultations') }}</h2>
        <UButton v-if="canWrite" @click="showNewConsultation = true" icon="i-lucide-plus" size="sm">
          {{ t('aesthetic.newConsultation') }}
        </UButton>
      </div>

      <UCard v-if="showNewConsultation" class="mb-4">
        <UForm :state="newConsultation" @submit="submitConsultation">
          <UFormGroup :label="t('aesthetic.type')" required>
            <USelect v-model="newConsultation.consultation_type"
              :options="[{ value: 'initial', label: 'Initial' }, { value: 'follow_up', label: 'Follow-up' }, { value: 'review', label: 'Review' }]"
              option-attribute="label" />
          </UFormGroup>
          <UFormGroup :label="t('aesthetic.findings')">
            <UTextarea v-model="newConsultation.findings" />
          </UFormGroup>
          <UFormGroup :label="t('aesthetic.recommendations')">
            <UTextarea v-model="newConsultation.recommendations" />
          </UFormGroup>
          <UFormGroup :label="t('aesthetic.skinAnalysis')">
            <UTextarea v-model="newConsultation.skin_analysis" />
          </UFormGroup>
          <div class="flex gap-2 mt-3">
            <UButton type="submit" color="primary">{{ t('aesthetic.save') }}</UButton>
            <UButton variant="ghost" @click="showNewConsultation = false">{{ t('aesthetic.cancel') }}</UButton>
          </div>
        </UForm>
      </UCard>

      <UCard>
        <UTable v-if="consultations.length" :rows="consultations" :columns="[
          { key: 'consultation_type', label: t('aesthetic.type') },
          { key: 'findings', label: t('aesthetic.findings') },
          { key: 'created_at', label: t('aesthetic.date') }
        ]" />
        <p v-else class="text-gray-400 text-center py-6">{{ consultationsLoading ? t('aesthetic.loading') : t('aesthetic.empty') }}</p>
      </UCard>
    </div>

    <!-- Tab: Photo Journey -->
    <div v-if="activeTab === 1">
      <div class="flex justify-between mb-3">
        <h2 class="text-lg font-semibold">{{ t('aesthetic.photos') }}</h2>
        <UButton v-if="canWrite" @click="showNewPhoto = true" icon="i-lucide-plus" size="sm">
          {{ t('aesthetic.newPhoto') }}
        </UButton>
      </div>

      <UCard v-if="showNewPhoto" class="mb-4">
        <UForm :state="newPhoto" @submit="submitPhoto">
          <UFormGroup :label="t('aesthetic.photoType')" required>
            <USelect v-model="newPhoto.photo_type"
              :options="[
                { value: 'before', label: t('aesthetic.before') },
                { value: 'after', label: t('aesthetic.after') },
                { value: 'progress', label: t('aesthetic.progress') }
              ]" option-attribute="label" />
          </UFormGroup>
          <UFormGroup label="Photo URL" required>
            <UInput v-model="newPhoto.photo_url" placeholder="https://..." />
          </UFormGroup>
          <UFormGroup :label="t('aesthetic.notes')">
            <UTextarea v-model="newPhoto.notes" />
          </UFormGroup>
          <div class="flex gap-2 mt-3">
            <UButton type="submit" color="primary">{{ t('aesthetic.save') }}</UButton>
            <UButton variant="ghost" @click="showNewPhoto = false">{{ t('aesthetic.cancel') }}</UButton>
          </div>
        </UForm>
      </UCard>

      <UCard>
        <div v-if="photos.length" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div v-for="photo in photos" :key="photo.id" class="border rounded-lg p-3">
            <img :src="photo.photo_url" alt="Photo" class="w-full h-48 object-cover rounded mb-2" />
            <p class="text-sm font-medium">{{ photo.photo_type }}</p>
            <p v-if="photo.notes" class="text-xs text-gray-500">{{ photo.notes }}</p>
            <p class="text-xs text-gray-400 mt-1">{{ photo.created_at }}</p>
          </div>
        </div>
        <p v-else class="text-gray-400 text-center py-6">{{ photosLoading ? t('aesthetic.loading') : t('aesthetic.empty') }}</p>
      </UCard>
    </div>

    <!-- Tab: Treatment History (placeholder) -->
    <div v-if="activeTab === 2">
      <p class="text-gray-400 text-center py-6">Treatment history — coming in Fase 2b.</p>
    </div>

    <!-- Tab: Product Recommendations (placeholder) -->
    <div v-if="activeTab === 3">
      <p class="text-gray-400 text-center py-6">Product recommendations — coming in Fase 2b.</p>
    </div>
  </div>
</template>