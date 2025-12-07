import request from '@/utils/request'

// 查询渠道ID列表
export function listNotifyChannel(query) {
  return request({
    url: '/notify/channel/list',
    method: 'get',
    params: query
  })
}

// 查询渠道ID详情
export function getNotifyChannel(id) {
  return request({
    url: '/notify/channel/' + id,
    method: 'get'
  })
}

// 新增渠道ID
export function addNotifyChannel(data) {
  return request({
    url: '/notify/channel',
    method: 'post',
    data: data
  })
}

// 修改渠道ID
export function updateNotifyChannel(data) {
  return request({
    url: '/notify/channel',
    method: 'put',
    data: data
  })
}

// 删除渠道ID
export function delNotifyChannel(id) {
  return request({
    url: '/notify/channel/' + id,
    method: 'delete'
  })
}

// 测试渠道
export function testNotifyChannel(id) {
  return request({
    url: '/notify/channel/test/' + id,
    method: 'post'
  })
}
