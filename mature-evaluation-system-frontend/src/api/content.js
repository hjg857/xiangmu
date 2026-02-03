import request from './request'

/**
 * 获取页面内容
 * @param {string} pageKey - 页面标识 (about/culture/guide/news)
 */
export function getPageContent(pageKey) {
  return request({
    url: `/api/content/${pageKey}`,
    method: 'get'
  })
}

/**
 * 更新页面内容（管理员）
 * @param {string} pageKey - 页面标识
 * @param {object} data - 内容数据
 */
export function updatePageContent(pageKey, data) {
  return request({
    url: `/api/admin/content/${pageKey}`,
    method: 'put',
    data
  })
}
