<template>
  <div class="app-container">
    <el-form :model="queryParams" ref="queryRef" :inline="true" v-show="showSearch">
      <el-form-item label="状态" prop="status">
        <el-select v-model="queryParams.status" placeholder="请选择状态" clearable style="width: 120px">
          <el-option label="成功" value="0" />
          <el-option label="失败" value="1" />
        </el-select>
      </el-form-item>
      <el-form-item label="平台" prop="platformId">
        <el-select v-model="queryParams.platformId" placeholder="请选择平台" clearable style="width: 120px">
          <el-option v-for="item in platformList" :key="item.platformId" :label="item.platformName" :value="item.platformId" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" icon="Search" @click="handleQuery">搜索</el-button>
        <el-button icon="Refresh" @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>

    <el-row :gutter="10" class="mb8">
      <el-col :span="1.5">
        <el-button type="danger" plain icon="Delete" :disabled="multiple" @click="handleDelete" v-hasPermi="['notify:log:remove']">删除</el-button>
      </el-col>
      <right-toolbar v-model:showSearch="showSearch" @queryTable="getList"></right-toolbar>
    </el-row>

    <el-table v-loading="loading" :data="logList" @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="55" align="center" />
      <el-table-column label="日志ID" align="center" prop="logId" width="80" />
      <el-table-column label="平台" align="center" prop="platformName" width="100">
        <template #default="scope">
          <el-tag>{{ getPlatformName(scope.row.platformId) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="渠道" align="center" prop="channelName" width="120" show-overflow-tooltip />
      <el-table-column label="标题" align="center" prop="title" width="150" show-overflow-tooltip />
      <el-table-column label="内容" align="center" prop="content" min-width="200" show-overflow-tooltip />
      <el-table-column label="状态" align="center" prop="status" width="80">
        <template #default="scope">
          <el-tag :type="scope.row.status === '0' ? 'success' : 'danger'">
            {{ scope.row.status === '0' ? '成功' : '失败' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="错误信息" align="center" prop="errorMsg" width="150" show-overflow-tooltip />
      <el-table-column label="耗时(ms)" align="center" prop="costTime" width="90" />
      <el-table-column label="发送时间" align="center" prop="sendTime" width="160" />
      <el-table-column label="IP地址" align="center" prop="ipAddress" width="130" />
    </el-table>

    <pagination v-show="total > 0" :total="total" v-model:page="queryParams.pageNum" v-model:limit="queryParams.pageSize" @pagination="getList" />
  </div>
</template>

<script setup name="NotifyLog">
import { ref, reactive, onMounted } from 'vue'
import { listNotifyLog, delNotifyLog } from '@/api/notify/notify_log'
import { listNotifyPlatform } from '@/api/notify/notify_platform'

const loading = ref(false)
const showSearch = ref(true)
const logList = ref([])
const platformList = ref([])
const total = ref(0)
const ids = ref([])
const multiple = ref(true)

const queryParams = reactive({
  pageNum: 1,
  pageSize: 10,
  status: undefined,
  platformId: undefined
})

const getPlatformName = (platformId) => {
  const platform = platformList.value.find(p => p.platformId === platformId)
  return platform ? platform.platformName : '-'
}

const getList = async () => {
  loading.value = true
  try {
    const res = await listNotifyLog(queryParams)
    logList.value = res.rows
    total.value = res.total
  } finally {
    loading.value = false
  }
}

const getPlatformList = async () => {
  const res = await listNotifyPlatform({ pageNum: 1, pageSize: 100 })
  platformList.value = res.rows || []
}

const handleQuery = () => {
  queryParams.pageNum = 1
  getList()
}

const resetQuery = () => {
  queryParams.status = undefined
  queryParams.platformId = undefined
  handleQuery()
}

const handleSelectionChange = (selection) => {
  ids.value = selection.map(item => item.logId)
  multiple.value = !selection.length
}

const handleDelete = async () => {
  await proxy.$modal.confirm('是否确认删除选中的记录？')
  await delNotifyLog(ids.value.join(','))
  getList()
  proxy.$modal.msgSuccess('删除成功')
}

onMounted(() => {
  getList()
  getPlatformList()
})
</script>
