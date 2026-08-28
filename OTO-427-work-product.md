# OTO-427 Work Product — Fase 2a: Klinik Estetika (Otomedis)

## Ringkasan

Adaptasi DentalPin v2.0.0 menjadi aplikasi klinik estetika/kecantikan. Fork dilakukan sebagai branch `estetika` di repositori bukexagency-oss/dentalpin.

## Commit

**Commit**: `6934a53` — OTO-427: fix frontend build (rename aesthetic_plan composable + import path), di atas `b7b7b38` (migration collisions + boot stack) dan `60daea1` (estetika fork)
**Branch**: https://github.com/bukexagency-oss/dentalpin/tree/estetika

## Modul Baru

| Modul | Path | Fungsi |
|-------|------|--------|
| `aesthetic_plan` | `backend/app/modules/aesthetic_plan/` | Copy treatment_plan untuk paket perawatan estetika (aesthetic_plans, aesthetic_plan_items, aesthetic_plan_item_sessions). Migrasi: ae_0001–ae_0006 |
| `aesthetic` | `backend/app/modules/aesthetic/` | Modul baru: PhotoJourney, ConsultationNote, TreatmentHistory, ProductRecommendation. Migrasi: aes_0001 |
| `skin_analysis` | `backend/app/modules/skin_analysis/` | Modul baru: Fitzpatrick scale, skin type assessment |

## Modul yang Dimodifikasi

| Modul | Perubahan |
|-------|-----------|
| `catalog/seed.py` | +207 baris seed estetika (filler, botox, laser, peeling, microneedling, PRP, thread lift) dalam 5 kategori baru: facial, injectables, laser, skin, body |
| `clinical_notes/seed.py` | +131 baris: aesthetic treatment notes |
| `inventory/schemas.py` | Schema adjustments untuk produk estetika |
| `lab_orders/schemas.py` | Schema adjustments untuk lab estetika |
| `seed_demo.py` | Gating: aesthetic_fork signal → skip dental journey (odontogram/plans/budgets/invoices) |
| `docker-compose.estetic.yml` | Isolated stack (5435/8101/3102), DENTALPIN_MODULE_EXCLUDE framework |
| `frontend/modules.json` | Include aesthetic_plan + aesthetic layers |
| `frontend/app/config/permissions.ts` | Aesthetic module permissions |

## Modul yang Dormant (tidak dihapus fisik, tapi tidak dipakai di fork)

- `odontogram` — tetap ter-install (diperlukan oleh FK `aesthetic_plan_items.treatment_id → treatments.id`)
- `treatment_plan` — tetap ter-install (dormant; clinical_notes module depends_on treatment_plan di manifest)
- `periodontogram` — tetap ter-install (dormant)

## Perubahan Infrastruktur

| Perubahan | Detail |
|-----------|--------|
| `loader.py` | DENTALPIN_MODULE_EXCLUDE — framework untuk exclude modul di masa depan |
| `config.py` | Settings field DENTALPIN_MODULE_EXCLUDE |
| `docker-compose.estetic.yml` | Port: DB 5435, Backend 8101, Frontend 3102. .env.estetic untuk isolated credentials |

## Fix Migration Collisions

Aesthetic_plan adalah copy treatment_plan yang harus coexist dengan treatment_plan (masih ter-install via filesystem scan). Semua nama global PostgreSQL di-rename untuk menghindari collision:

| Objek | Nama Original | Nama Baru |
|-------|--------------|-----------|
| UniqueConstraint | uq_treatment_plan_number | uq_aesthetic_plan_number |
| UniqueConstraint | uq_planned_item_treatment | uq_aesthetic_plan_item_treatment |
| UniqueConstraint | uq_plan_item_session_sequence | uq_aesthetic_plan_item_session_sequence |
| FK | fk_appointment_treatments_planned_item | fk_appointment_treatments_aesthetic_item |
| FK | fk_planned_items_assigned_professional | fk_aesthetic_plan_items_assigned_professional |
| Index | idx_planned_items_plan/status/treatment | idx_aesthetic_plan_items_plan/status/treatment |
| Index | idx_planned_items_plan_professional | idx_aesthetic_plan_items_plan_professional |
| Index | idx_pti_session_plan_item | idx_aesthetic_plan_item_session_plan_item |
| Index | ix_pti_session_plan_item_status | ix_aesthetic_plan_item_session_plan_item_status |
| Table | treatment_media | dihapus dari ae_0001 (dibuat oleh tp_0001) |
| Migration | ae_0002 | no-op (clinical_notes dikelola clinical_notes module) |
| Migration | ae_0004 | no-op (treatment_media→media handled by tp_0004) |
| ORM | back_populates="aesthetic_plan" | back_populates="treatment_plan" (match actual attribute) |
| Model | catalog_item_id (extra) | dihapus (tidak ada di migration) |
| Model | treatment_id (missing) | ditambahkan (sync dengan ae_0001 migration) |

## Bukti Verifikasi

### Stack

| Component | Status | Port |
|-----------|--------|------|
| PostgreSQL | Healthy | 5435 |
| Backend (FastAPI) | Healthy | 8101 |
| Frontend (Nuxt) | Healthy | 3102 |

### API Endpoints

| Endpoint | Status | Response |
|----------|--------|----------|
| `/health` | 200 | OK |
| `/api/v1/auth/login` | 200 | access_token (279 chars) |
| `/api/v1/aesthetic_plan/aesthetic-plans` | 200 | `{"data":[],"total":0}` |
| `/api/v1/aesthetic/aesthetic/consultations` | 201 POST / 200 GET | Created + listed |
| `/api/v1/aesthetic/aesthetic/photos` | 201 POST / 200 GET | Created + listed |
| `/api/v1/aesthetic/aesthetic/treatments` | 200 | `{"data":[],"total":0}` |
| `/api/v1/aesthetic/aesthetic/recommendations` | 200 | `{"data":[],"total":0}` |
| `/api/v1/skin_analysis/skin_analysis/fitzpatrick` | 200 | Fitzpatrick scale data |
| `/api/v1/patients` | 200 | 15 demo patients |
| `/api/v1/catalog/items` | 200 | 144 items (15 estetika) |

### Frontend (verified 28Agu26, commit 6934a53)

- Container `dentalpin-estetika-frontend-1` **Up (healthy)**, port 3102
- `GET /login` → 200, Nuxt 4.4.2 SSR render, `<title>DentalPin</title>`
- `GET /` → 302 → /login (auth redirect normal)
- Build log: `✓ built in 38.20s`, `✔ Server built`, `Listening on http://0.0.0.0:3000`

### Fix Frontend Build (baru, run 28Agu28)

Build gagal di run sebelumnya: `RollupError: Could not resolve "../../composables/useAestheticPlans"` dan `"../aesthetic-plans/PlanItemSessionRow.vue"`. Akar masalah: copy treatment_plan → aesthetic_plan tidak rename dua hal:

| File | Sebelum (broken) | Sesudah (fix) |
|------|------------------|---------------|
| `composables/useTreatmentPlans.ts` | file bernama lama, isi export `useAestheticPlans()` | rename → `composables/useAestheticPlans.ts` |
| `components/clinical/PlanTreatmentList.vue` | `import ... from '../aesthetic-plans/PlanItemSessionRow.vue'` | `import ... from '../treatment-plans/PlanItemSessionRow.vue'` |

Kedua file sudah di-commit (`6934a53`) dan push ke origin/estetika. Stack sekarang full healthy.

### Seed Data

- Demo users: admin/dentist/hygienist/assistant/receptionist (password: demo1234)
- 50 pasien demo
- Dental journey **skipped** (gating `aesthetic_fork` berfungsi)
- 144 catalog items termasuk 15 estetika (injectables 4, laser 3, skin 3, facial 3, body 2)

## Known Issues (Follow-up Items)

1. **Double prefix** pada route aesthetic & skin_analysis: `/api/v1/aesthetic/aesthetic/...` dan `/api/v1/skin_analysis/skin_analysis/...`. Router prefix clash dengan module mount prefix. Tidak fatal, path berfungsi.
2. **Catalog seed** masih men-seed dental items juga (129 dental + 15 estetika). Idealnya fork estetika hanya seed estetika. Solusi: tambahkan parameter `aesthetic_only` di seed_catalog.
3. **Frontend build** — ✅ RESOLVED di commit `6934a53` (28Agu28). Stack full healthy (db 5435, backend 8101, frontend 3102).
4. **Physical deletion dental modules** — masih diperlukan refactor besar untuk menghapus odontogram/treatment_plan/periodontogram dari runtime (imports di agenda/service, clinical_notes, migration_import, alembic/env.py, scripts, tests). Ditunggu di Fase 2b atau 3.
5. **Aesthetic_plan decoupling from odontogram** — `treatment_id` FK masih menunjuk `treatments.id` (odontogram). Full decoupling needed untuk membuat fork benar-benar independen.
6. **Medical_reference/lab_orders/inventory seed** — perubahan schema sudah dilakukan, tapi seed data estetika belum diisi penuh.