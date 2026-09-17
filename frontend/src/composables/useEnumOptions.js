import { computed, onMounted } from 'vue'

import { useMetaStore } from '@/stores/meta'

/** 取某一组字典的下拉选项，并在首次使用时拉取字典。 */
export function useEnumOptions(group) {
  const meta = useMetaStore()
  onMounted(() => meta.ensureLoaded())
  const options = computed(() => meta.options(group))
  const label = (value) => meta.label(group, value)
  return { options, label, meta }
}
