/**
 * 管理员相关API
 */
import request from './request'

/**
 * 获取待审批申请列表
 */
export function getApplicationList(params) {
  return request({
    url: '/applications/',
    method: 'get',
    params
  })
}

/**
 * 审批通过
 */
export function approveApplication(applicationId) {
  return request({
    url: `/applications/${applicationId}/approve/`,
    method: 'post'
  })
}

/**
 * 拒绝申请
 */
export function rejectApplication(applicationId, data) {
  return request({
    url: `/applications/${applicationId}/reject/`,
    method: 'post',
    data
  })
}

/**
 * 获取学校列表
 */
export function getSchools(params) {
  return request({
    url: '/list/',
    method: 'get',
    params
  })
}

/**
 * 删除学校
 */
export function deleteSchool(schoolId) {
  return request({
    url: `/${schoolId}/delete/`,
    method: 'delete'
  })
}

/**
 * 获取评估报告列表
 */
export function getAssessmentReports(params) {
  return request({
    url: '/assessments/admin_list/',
    method: 'get',
    params
  })
}
