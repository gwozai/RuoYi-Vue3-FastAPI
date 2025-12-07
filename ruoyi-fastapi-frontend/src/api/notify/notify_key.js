import request from '@/utils/request'

// 查询密钥ID列表
export function listNotifyKey(query) {
  return request({
    url: '/notify/key/list',
    method: 'get',
    params: query
  })
}

// 查询密钥ID详情
export function getNotifyKey(id) {
  return request({
    url: '/notify/key/' + id,
    method: 'get'
  })
}

// 新增密钥ID
export function addNotifyKey(data) {
  return request({
    url: '/notify/key',
    method: 'post',
    data: data
  })
}

// 修改密钥ID
export function updateNotifyKey(data) {
  return request({
    url: '/notify/key',
    method: 'put',
    data: data
  })
}

// 删除密钥ID
export function delNotifyKey(id) {
  return request({
    url: '/notify/key/' + id,
    method: 'delete'
  })
}

// 生成API密钥
export function generateNotifyKey(data) {
  return request({
    url: '/notify/key/generate',
    method: 'post',
    data: data
  })
}

// 重置API密钥
export function resetNotifyKey(id) {
  return request({
    url: '/notify/key/reset/' + id,
    method: 'post'
  })
}
