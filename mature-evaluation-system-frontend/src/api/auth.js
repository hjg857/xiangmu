/**
 * 认证相关API
 */
import request from './request'

/**
 * 获取验证码
 */
export function getCaptcha() {
  return request({
    url: '/auth/captcha/',
    method: 'get'
  })
}

/**
 * 用户登录
 */
export function login(data) {
  return request({
    url: '/auth/login/',
    method: 'post',
    data
  })
}

/**
 * 用户登出
 */
export function logout() {
  return request({
    url: '/auth/logout/',
    method: 'post'
  })
}

/**
 * 刷新Token
 */
export function refreshToken(data) {
  return request({
    url: '/auth/refresh/',
    method: 'post',
    data
  })
}

/**
 * 重置密码
 */
export function resetPassword(data) {
  return request({
    url: '/auth/reset-password/',
    method: 'post',
    data
  })
}

/**
 * 修改密码
 */
export function changePassword(data) {
  return request({
    url: '/auth/change-password/',
    method: 'post',
    data
  })
}

/**
 * 获取当前用户信息
 */
export function getCurrentUser() {
  return request({
    url: '/auth/current-user/',
    method: 'get'
  })
}
