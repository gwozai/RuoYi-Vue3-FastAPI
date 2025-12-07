import request from '@/utils/request'

// 查询【请填写功能名称】列表
export function listStudent(query) {
  return request({
    url: '/student/info/list',
    method: 'get',
    params: query
  })
}

// 查询【请填写功能名称】详细
export function getStudent(studentId) {
  return request({
    url: '/student/info/' + studentId,
    method: 'get'
  })
}

// 新增【请填写功能名称】
export function addStudent(data) {
  return request({
    url: '/student/info',
    method: 'post',
    data: data
  })
}

// 修改【请填写功能名称】
export function updateStudent(data) {
  return request({
    url: '/student/info',
    method: 'put',
    data: data
  })
}

// 删除【请填写功能名称】
export function delStudent(studentId) {
  return request({
    url: '/student/info/' + studentId,
    method: 'delete'
  })
}
