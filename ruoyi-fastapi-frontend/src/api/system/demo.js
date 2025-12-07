import request from '@/utils/request'

// 查询演示ID列表
export function listDemo(query) {
  return request({
    url: '/system/demo/list',
    method: 'get',
    params: query
  })
}

// 查询演示ID详情
export function getDemo(id) {
  return request({
    url: '/system/demo/' + id,
    method: 'get'
  })
}

// 新增演示ID
export function addDemo(data) {
  return request({
    url: '/system/demo',
    method: 'post',
    data: data
  })
}

// 修改演示ID
export function updateDemo(data) {
  return request({
    url: '/system/demo',
    method: 'put',
    data: data
  })
}

// 删除演示ID
export function delDemo(id) {
  return request({
    url: '/system/demo/' + id,
    method: 'delete'
  })
}
