import request from '@/utils/request'

// 查询TTS API配置列表
export function listTtsconfig(query) {
  return request({
    url: '/system/ttsConfig/list',
    method: 'get',
    params: query
  })
}

// 查询TTS API配置详细
export function getTtsconfig(configId) {
  return request({
    url: '/system/ttsConfig/' + configId,
    method: 'get'
  })
}

// 新增TTS API配置
export function addTtsconfig(data) {
  return request({
    url: '/system/ttsConfig',
    method: 'post',
    data: data
  })
}

// 修改TTS API配置
export function updateTtsconfig(data) {
  return request({
    url: '/system/ttsConfig',
    method: 'put',
    data: data
  })
}

// 删除TTS API配置
export function delTtsconfig(configId) {
  return request({
    url: '/system/ttsConfig/' + configId,
    method: 'delete'
  })
}
