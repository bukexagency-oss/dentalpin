/**
 * API client for the aesthetic module (Otomedis esthetic clinic fork).
 *
 * Thin wrapper over the shared `useApi()` client. Resources:
 * - /aesthetic/photos         — PhotoJourney (before/after/progress)
 * - /aesthetic/consultations  — consultation notes
 * - /aesthetic/treatments     — treatment history
 * - /aesthetic/recommendations — post-treatment product recommendations
 */

export interface PhotoJourney {
  id: string
  clinic_id: string
  patient_id: string
  photo_type: string
  photo_url: string
  notes: string | null
  taken_at: string | null
  created_at: string
  updated_at: string
}

export interface ConsultationNote {
  id: string
  clinic_id: string
  patient_id: string
  consultation_type: string
  findings: string | null
  recommendations: string | null
  skin_analysis: string | null
  created_by: string
  created_at: string
  updated_at: string
}

export interface TreatmentHistory {
  id: string
  clinic_id: string
  patient_id: string
  treatment_type: string
  product_used: string | null
  dosage_cc: number | null
  area_treated: string | null
  notes: string | null
  performed_by: string
  performed_at: string | null
  created_at: string
  updated_at: string
}

export interface ProductRecommendation {
  id: string
  clinic_id: string
  patient_id: string
  product_name: string
  product_type: string
  usage_instructions: string | null
  frequency: string | null
  duration_days: number | null
  prescribed_by: string
  created_at: string
  updated_at: string
}

interface Paginated<T> {
  data: T[]
  total: number
  page: number
  page_size: number
}

interface Wrapped<T> {
  data: T
}

export function useAesthetic() {
  const api = useApi()

  // --- Photo journey -------------------------------------------------
  const listPhotos = (patientId?: string, page = 1, pageSize = 20) =>
    api.$api<Paginated<PhotoJourney>>('/api/v1/aesthetic/photos', {
      query: { patient_id: patientId, page, page_size: pageSize }
    })

  const createPhoto = (payload: {
    patient_id: string
    photo_type: string
    photo_url: string
    notes?: string
    taken_at?: string
  }) => api.$api<Wrapped<PhotoJourney>>('/api/v1/aesthetic/photos', { method: 'POST', body: payload })

  const deletePhoto = (id: string) =>
    api.$api<Wrapped<{ deleted: boolean }>>(`/api/v1/aesthetic/photos/${id}`, { method: 'DELETE' })

  // --- Consultations ---------------------------------------------------
  const listConsultations = (patientId?: string, page = 1, pageSize = 20) =>
    api.$api<Paginated<ConsultationNote>>('/api/v1/aesthetic/consultations', {
      query: { patient_id: patientId, page, page_size: pageSize }
    })

  const createConsultation = (payload: {
    patient_id: string
    consultation_type: string
    findings?: string
    recommendations?: string
    skin_analysis?: string
  }) =>
    api.$api<Wrapped<ConsultationNote>>('/api/v1/aesthetic/consultations', {
      method: 'POST',
      body: payload
    })

  // --- Treatment history ------------------------------------------------
  const listTreatments = (patientId?: string, page = 1, pageSize = 20) =>
    api.$api<Paginated<TreatmentHistory>>('/api/v1/aesthetic/treatments', {
      query: { patient_id: patientId, page, page_size: pageSize }
    })

  const createTreatment = (payload: {
    patient_id: string
    treatment_type: string
    product_used?: string
    dosage_cc?: number
    area_treated?: string
    notes?: string
    performed_at?: string
  }) =>
    api.$api<Wrapped<TreatmentHistory>>('/api/v1/aesthetic/treatments', {
      method: 'POST',
      body: payload
    })

  // --- Product recommendations -------------------------------------------
  const listRecommendations = (patientId?: string, page = 1, pageSize = 20) =>
    api.$api<Paginated<ProductRecommendation>>('/api/v1/aesthetic/recommendations', {
      query: { patient_id: patientId, page, page_size: pageSize }
    })

  const createRecommendation = (payload: {
    patient_id: string
    product_name: string
    product_type: string
    usage_instructions?: string
    frequency?: string
    duration_days?: number
  }) =>
    api.$api<Wrapped<ProductRecommendation>>('/api/v1/aesthetic/recommendations', {
      method: 'POST',
      body: payload
    })

  return {
    listPhotos,
    createPhoto,
    deletePhoto,
    listConsultations,
    createConsultation,
    listTreatments,
    createTreatment,
    listRecommendations,
    createRecommendation
  }
}
