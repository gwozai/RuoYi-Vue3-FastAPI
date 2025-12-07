import request from '@/utils/request'

// 查询平台ID列表
export function listNotifyPlatform(query) {
  return request({
    url: '/notify/platform/list',
    method: 'get',
    params: query
  })
}

// 查询平台ID详情
export function getNotifyPlatform(id) {
  return request({
    url: '/notify/platform/' + id,
    method: 'get'
  })
}

// 新增平台ID
export function addNotifyPlatform(data) {
  return request({
    url: '/notify/platform',
    method: 'post',
    data: data
  })
}

// 修改平台ID
export function updateNotifyPlatform(data) {
  return request({
    url: '/notify/platform',
    method: 'put',
    data: data
  })
}

// 删除平台ID
export function delNotifyPlatform(id) {
  return request({
    url: '/notify/platform/' + id,
    method: 'delete'
  })
}
