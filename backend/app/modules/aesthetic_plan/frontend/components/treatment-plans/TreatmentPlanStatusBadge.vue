<script setup lang="ts">
import type { AestheticPlanStatus } from '~~/app/types'
import type { UiColor } from '~~/app/config/severity'

const props = defineProps<{
  status: AestheticPlanStatus
  size?: 'xs' | 'sm' | 'md'
}>()

const { t } = useI18n()

const colorMap: Record<AestheticPlanStatus, UiColor> = {
  draft: 'neutral',
  pending: 'warning',
  active: 'info',
  completed: 'success',
  closed: 'error',
  archived: 'neutral'
}

const color = computed(() => colorMap[props.status])
const label = computed(() => t(`treatmentPlans.status.${props.status}`))
</script>

<template>
  <UBadge
    :color="color"
    :size="size || 'sm'"
    variant="subtle"
  >
    {{ label }}
  </UBadge>
</template>
