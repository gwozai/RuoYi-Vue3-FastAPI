<template>
  <div class="app-container">
    <el-form :model="queryParams" ref="queryRef" :inline="true" v-show="showSearch">
      <el-form-item label="渠道名称" prop="channelName">
        <el-input v-model="queryParams.channelName" placeholder="请输入渠道名称" clearable style="width: 200px" @keyup.enter="handleQuery" />
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
        <el-button type="primary" plain icon="Plus" @click="handleAdd" v-hasPermi="['notify:channel:add']">新增</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button type="danger" plain icon="Delete" :disabled="multiple" @click="handleDelete" v-hasPermi="['notify:channel:remove']">删除</el-button>
      </el-col>
      <right-toolbar v-model:showSearch="showSearch" @queryTable="getList"></right-toolbar>
    </el-row>

    <el-table v-loading="loading" :data="channelList" @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="55" align="center" />
      <el-table-column label="渠道ID" align="center" prop="channelId" width="80" />
      <el-table-column label="渠道名称" align="center" prop="channelName" width="150" />
      <el-table-column label="平台" align="center" width="100">
        <template #default="scope">
          <el-tag>{{ getPlatformName(scope.row.platformId) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="Webhook密钥" align="center" prop="webhookKey" min-width="200" show-overflow-tooltip />
      <el-table-column label="默认" align="center" prop="isDefault" width="80">
        <template #default="scope">
          <el-tag :type="scope.row.isDefault === '1' ? 'success' : 'info'">
            {{ scope.row.isDefault === '1' ? '是' : '否' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="使用次数" align="center" prop="useCount" width="90" />
      <el-table-column label="状态" align="center" prop="status" width="80">
        <template #default="scope">
          <el-tag :type="scope.row.status === '0' ? 'success' : 'danger'">
            {{ scope.row.status === '0' ? '正常' : '停用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" align="center" width="200" fixed="right">
        <template #default="scope">
          <el-button link type="primary" icon="Position" @click="handleTest(scope.row)" v-hasPermi="['notify:channel:test']">测试</el-button>
          <el-button link type="primary" icon="Edit" @click="handleUpdate(scope.row)" v-hasPermi="['notify:channel:edit']">修改</el-button>
          <el-button link type="danger" icon="Delete" @click="handleDelete(scope.row)" v-hasPermi="['notify:channel:remove']">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <pagination v-show="total > 0" :total="total" v-model:page="queryParams.pageNum" v-model:limit="queryParams.pageSize" @pagination="getList" />

    <!-- 添加或修改对话框 -->
    <el-dialog :title="title" v-model="open" width="500px" append-to-body>
      <el-form ref="channelRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="渠道名称" prop="channelName">
          <el-input v-model="form.channelName" placeholder="请输入渠道名称" />
        </el-form-item>
        <el-form-item label="平台" prop="platformId">
          <el-select v-model="form.platformId" placeholder="请选择平台" style="width: 100%">
            <el-option v-for="item in platformList" :key="item.platformId" :label="item.platformName" :value="item.platformId" />
          </el-select>
        </el-form-item>
        <el-form-item label="Webhook密钥" prop="webhookKey">
          <el-input v-model="form.webhookKey" placeholder="请输入Webhook密钥" />
        </el-form-item>
        <el-form-item label="设为默认" prop="isDefault">
          <el-switch v-model="form.isDefault" active-value="1" inactive-value="0" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="form.status">
            <el-radio value="0">正常</el-radio>
            <el-radio value="1">停用</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input v-model="form.remark" type="textarea" placeholder="请输入备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button type="primary" @click="submitForm">确 定</el-button>
        <el-button @click="cancel">取 消</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup name="NotifyChannel">
import { ref, reactive, onMounted, getCurrentInstance } from 'vue'
import { listNotifyChannel, getNotifyChannel, addNotifyChannel, updateNotifyChannel, delNotifyChannel, testNotifyChannel } from '@/api/notify/notify_channel'
import { listNotifyPlatform } from '@/api/notify/notify_platform'

const { proxy } = getCurrentInstance()

const loading = ref(false)
const showSearch = ref(true)
const channelList = ref([])
const platformList = ref([])
const total = ref(0)
const ids = ref([])
const multiple = ref(true)
const open = ref(false)
const title = ref('')

const queryParams = reactive({
  pageNum: 1,
  pageSize: 10,
  channelName: undefined,
  platformId: undefined
})

const form = ref({})
const rules = {
  channelName: [{ required: true, message: '渠道名称不能为空', trigger: 'blur' }],
  platformId: [{ required: true, message: '请选择平台', trigger: 'change' }],
  webhookKey: [{ required: true, message: 'Webhook密钥不能为空', trigger: 'blur' }]
}

const getPlatformName = (platformId) => {
  const platform = platformList.value.find(p => p.platformId === platformId)
  return platform ? platform.platformName : '-'
}

const getList = async () => {
  loading.value = true
  try {
    const res = await listNotifyChannel(queryParams)
    channelList.value = res.rows
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
  queryParams.channelName = undefined
  queryParams.platformId = undefined
  handleQuery()
}

const handleSelectionChange = (selection) => {
  ids.value = selection.map(item => item.channelId)
  multiple.value = !selection.length
}

const reset = () => {
  form.value = {
    channelId: undefined,
    channelName: undefined,
    platformId: undefined,
    webhookKey: undefined,
    isDefault: '0',
    status: '0',
    remark: undefined
  }
}

const handleAdd = () => {
  reset()
  open.value = true
  title.value = '添加渠道'
}

const handleUpdate = async (row) => {
  reset()
  const channelId = row.channelId || ids.value[0]
  const res = await getNotifyChannel(channelId)
  form.value = res.data
  open.value = true
  title.value = '修改渠道'
}

const submitForm = async () => {
  await proxy.$refs.channelRef.validate()
  if (form.value.channelId) {
    await updateNotifyChannel(form.value)
    proxy.$modal.msgSuccess('修改成功')
  } else {
    await addNotifyChannel(form.value)
    proxy.$modal.msgSuccess('新增成功')
  }
  open.value = false
  getList()
}

const cancel = () => {
  open.value = false
  reset()
}

const handleDelete = async (row) => {
  const channelIds = row.channelId || ids.value.join(',')
  await proxy.$modal.confirm('是否确认删除？')
  await delNotifyChannel(channelIds)
  getList()
  proxy.$modal.msgSuccess('删除成功')
}

const handleTest = async (row) => {
  try {
    await testNotifyChannel(row.channelId)
    proxy.$modal.msgSuccess('测试消息发送成功，请检查对应平台')
  } catch (e) {
    proxy.$modal.msgError('测试失败: ' + (e.message || e))
  }
}

onMounted(() => {
  getList()
  getPlatformList()
})
</script>
