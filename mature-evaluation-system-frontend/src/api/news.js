/**
 * 实践动态相关API
 */
import request from './request'

/**
 * 获取实践动态列表
 */
export function getNewsList() {
  return request({
    url: '/news/',
    method: 'get'
  })
}

/**
 * 获取实践动态详情
 */
export function getNewsDetail(id) {
  return request({
    url: `/news/${id}/`,
    method: 'get'
  })
}

/**
 * 创建实践动态（管理员）
 */
export function createNews(data) {
  return request({
    url: '/admin/news/',
    method: 'post',
    data
  })
}

/**
 * 更新实践动态（管理员）
 */
export function updateNews(id, data) {
  return request({
    url: `/admin/news/${id}/`,
    method: 'put',
    data
  })
}

/**
 * 删除实践动态（管理员）
 */
export function deleteNews(id) {
  return request({
    url: `/admin/news/${id}/delete/`,
    method: 'delete'
  })
}

/**
 * 上传图片（管理员）
 */
export function uploadNewsImage(file) {
  const formData = new FormData()
  formData.append('image', file)
  
  return request({
    url: '/admin/news/upload-image/',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    timeout: 60000 // 上传文件超时时间设置为60秒
  })
}
