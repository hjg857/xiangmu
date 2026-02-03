import request from './request'

// 区域概览
export function regionOverview() {
  return request({
    url: '/region-admin/overview/',
    method: 'get'
  })
}

// 区域学校列表
export function regionSchoolList(params) {
  return request({
    url: '/region-admin/schools/',
    method: 'get',
    params
  })
}

// 新增学校（区域管理员）
export function regionCreateSchool(data) {
  return request({
    url: '/region-admin/schools/create/',
    method: 'post',
    data
  })
}
