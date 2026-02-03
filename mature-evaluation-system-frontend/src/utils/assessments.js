
// 获取评估详细数据的 API
export function getAssessmentData(id) {
  return request({
    url: `/assessments/${id}/data/`, // 这里就是我们刚才后端改的那个接口
    method: 'get'
  })
}

// 顺便检查一下是否有 getAssessmentDetail，有时候名字可能写混了
export function getAssessmentDetail(id) {
  return request({
    url: `/assessments/${id}/`,
    method: 'get'
  })
}

export function createAssessment() {
  return request({
    url: '/assessments/', // 对应后端 AssessmentViewSet 的 create 方法
    method: 'post'
  })
}