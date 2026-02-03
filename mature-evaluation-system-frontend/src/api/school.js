/**
 * 学校相关API
 */
import request from './request'

/**
 * 提交账号申请
 */
export function createApplication(data) {
  return request({
    url: '/application/submit/',
    method: 'post',
    data
  })
}

/**
 * 查询申请状态
 */
export function getApplicationStatus(applicationId) {
  return request({
    url: `/application/${applicationId}/status/`,
    method: 'get'
  })
}

/**
 * 获取学校信息
 */
export function getSchoolInfo() {
  return request({
    url: '/school/info/',
    method: 'get'
  })
}

/**
 * 更新学校信息
 */
export function updateSchoolInfo(data) {
  return request({
    url: '/school/update/',
    method: 'put',
    data
  })
}
