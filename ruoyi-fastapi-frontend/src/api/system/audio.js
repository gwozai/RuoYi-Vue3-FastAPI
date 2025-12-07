import request from '@/utils/request'

// 查询音频列表
export function listAudio(query) {
  return request({
    url: '/system/audio/list',
    method: 'get',
    params: query
  })
}

// 查询音频详细
export function getAudio(audioId) {
  return request({
    url: '/system/audio/' + audioId,
    method: 'get'
  })
}

// 生成音频
export function generateAudio(data) {
  return request({
    url: '/system/audio/generate',
    method: 'post',
    data: data
  })
}

// 新增音频记录
export function addAudio(data) {
  return request({
    url: '/system/audio',
    method: 'post',
    data: data
  })
}

// 修改音频记录
export function updateAudio(data) {
  return request({
    url: '/system/audio',
    method: 'put',
    data: data
  })
}

// 删除音频记录
export function delAudio(audioId) {
  return request({
    url: '/system/audio/' + audioId,
    method: 'delete'
  })
}

// 获取可用语音模型列表
export function getVoices() {
  return request({
    url: '/system/audio/voices/list',
    method: 'get'
  })
}

// 下载音频
export function downloadAudio(audioId) {
  return request({
    url: '/system/audio/download/' + audioId,
    method: 'get',
    responseType: 'blob'
  })
}

// 获取用户TTS配置列表
export function getTtsConfigs() {
  return request({
    url: '/system/audio/ttsConfigs/list',
    method: 'get'
  })
}
