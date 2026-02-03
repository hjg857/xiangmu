import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  const userInfo = ref(null)
  const token = ref(localStorage.getItem('access_token') || '')

  const setToken = (newToken) => {
    token.value = newToken
    localStorage.setItem('access_token', newToken)
  }

  const setUserInfo = (info) => {
    userInfo.value = info
    localStorage.setItem('user', JSON.stringify(info))
  }

  const logout = () => {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
  }

  return {
    userInfo,
    token,
    setToken,
    setUserInfo,
    logout
  }
})
