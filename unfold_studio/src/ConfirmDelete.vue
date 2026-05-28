<template>
  <span>
    <button type="button" @click="showConfirm = true">{{ label }}</button>
    <span v-if="showConfirm" class="confirm-dialog">
      <span>Are you sure?</span>
      <form :action="action" method="post" @submit.prevent="submit">
        <input type="hidden" name="csrfmiddlewaretoken" :value="csrfToken">
        <button type="submit">Yes, delete</button>
        <button type="button" @click="showConfirm = false">Cancel</button>
      </form>
    </span>
  </span>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps<{
  label: string
  action: string
  csrfToken: string
}>()

const showConfirm = ref(false)

function submit(): void {
  const form = document.createElement('form')
  form.method = 'post'
  form.action = props.action
  const csrf = document.createElement('input')
  csrf.type = 'hidden'
  csrf.name = 'csrfmiddlewaretoken'
  csrf.value = props.csrfToken
  form.appendChild(csrf)
  document.body.appendChild(form)
  form.submit()
}
</script>
