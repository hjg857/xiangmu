/**
 * 评估系统API
 */
import request from './request'

/**
 * 获取当前学校的评估列表
 */
export function getAssessments() {
  return request({
    url: '/assessments/',
    method: 'get'
  })
}

/**
 * 创建新评估
 */
export function createAssessment() {
  return request({
    url: '/assessments/',
    method: 'post'
  })
}

/**
 * 获取评估详情
 * @param {number} assessmentId - 评估ID
 */
export function getAssessment(assessmentId) {
  return request({
    url: `/assessments/${assessmentId}/`,
    method: 'get'
  })
}

/**
 * 更新评估状态
 * @param {number} assessmentId - 评估ID
 * @param {object} data - 更新数据
 */
export function updateAssessment(assessmentId, data) {
  return request({
    url: `/assessments/${assessmentId}/`,
    method: 'patch',
    data
  })
}

/**
 * 提交评估并生成报告
 * @param {number} assessmentId - 评估ID
 */
export function generateReport(assessmentId) {
  return request({
    url: `/assessments/${assessmentId}/submit/`,
    method: 'post'
  })
}

/**
 * 获取评估报告数据
 * @param {number} assessmentId - 评估ID
 */
export function getReportData(assessmentId) {
  return request({
    url: `/assessments/${assessmentId}/data/`,
    method: 'get'
  })
}

export function getReportDataDetail(id) {
  return request({
    // 确保请求的是 /report/ 接口，该接口返回计算后的分值和AI建议
    url: `/assessments/${id}/report-detail/`, 
    method: 'get'
  })
}
