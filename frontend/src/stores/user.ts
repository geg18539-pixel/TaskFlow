import { ref } from 'vue'
import { defineStore } from 'pinia'

import request from '@/api/request'

interface UserInfo {
  id: number
  username: string
  role: string
  created_at: string
}

const TOKEN_KEY = 'token'
const USER_KEY = 'userInfo'

function readStoredUser(): UserInfo | null {
  const raw = localStorage.getItem(USER_KEY)
  if (!raw) return null
  try {
    return JSON.parse(raw) as UserInfo
  } catch {
    return null
  }
}

export const useUserStore = defineStore('user', () => {
  const token = ref<string>(localStorage.getItem(TOKEN_KEY) || '')
  const userInfo = ref<UserInfo | null>(readStoredUser())

  function setToken(value: string) {
    token.value = value
    localStorage.setItem(TOKEN_KEY, value)
  }

  function setUserInfo(value: UserInfo | null) {
    userInfo.value = value
    if (value) {
      localStorage.setItem(USER_KEY, JSON.stringify(value))
    } else {
      localStorage.removeItem(USER_KEY)
    }
  }

  async function getUserInfo() {
    const { data } = await request.get<UserInfo>('/users/me')
    setUserInfo(data)
    return data
  }

  async function login(username: string, password: string) {
    const form = new URLSearchParams()
    form.append('username', username)
    form.append('password', password)

    const { data } = await request.post('/login', form, { silent: true })
    setToken(data.access_token)
    await getUserInfo()
    return data
  }

  async function initUser() {
    if (!token.value) return
    try {
      await getUserInfo()
    } catch {
      logout()
    }
  }

  function logout() {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
    window.location.href = '/login'
  }

  return { token, userInfo, login, getUserInfo, initUser, logout }
})
