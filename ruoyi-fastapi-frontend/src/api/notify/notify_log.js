import request from '@/utils/request'

// 查询日志ID列表
export function listNotifyLog(query) {
  return request({
    url: '/notify/log/list',
    method: 'get',
    params: query
  })
}

// 查询日志ID详情
export function getNotifyLog(id) {
  return request({
    url: '/notify/log/' + id,
    method: 'get'
  })
}

// 新增日志ID
export function addNotifyLog(data) {
  return request({
    url: '/notify/log',
    method: 'post',
    data: data
  })
}

// 修改日志ID
export function updateNotifyLog(data) {
  return request({
    url: '/notify/log',
    method: 'put',
    data: data
  })
}

// 删除日志ID
export function delNotifyLog(id) {
  return request({
    url: '/notify/log/' + id,
    method: 'delete'
  })
}
