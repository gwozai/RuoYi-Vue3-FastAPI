<template>
  <div class="app-container">
    <el-form :model="queryParams" ref="queryRef" :inline="true" v-show="showSearch">
      <el-form-item label="密钥名称" prop="keyName">
        <el-input v-model="queryParams.keyName" placeholder="请输入密钥名称" clearable style="width: 200px" @keyup.enter="handleQuery" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" icon="Search" @click="handleQuery">搜索</el-button>
        <el-button icon="Refresh" @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>

    <el-row :gutter="10" class="mb8">
      <el-col :span="1.5">
        <el-button type="primary" plain icon="Plus" @click="handleAdd" v-hasPermi="['notify:key:add']">生成密钥</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button type="danger" plain icon="Delete" :disabled="multiple" @click="handleDelete" v-hasPermi="['notify:key:remove']">删除</el-button>
      </el-col>
      <right-toolbar v-model:showSearch="showSearch" @queryTable="getList"></right-toolbar>
    </el-row>

    <el-table v-loading="loading" :data="keyList" @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="55" align="center" />
      <el-table-column label="密钥ID" align="center" prop="keyId" width="80" />
      <el-table-column label="密钥名称" align="center" prop="keyName" width="150" />
      <el-table-column label="API密钥" align="center" prop="apiKey" min-width="300">
        <template #default="scope">
          <el-input v-model="scope.row.apiKey" readonly>
            <template #append>
              <el-button icon="CopyDocument" @click="copyKey(scope.row.apiKey)" />
            </template>
          </el-input>
        </template>
      </el-table-column>
      <el-table-column label="每日限额" align="center" prop="dailyLimit" width="90" />
      <el-table-column label="今日已用" align="center" prop="dailyUsed" width="90" />
      <el-table-column label="总调用" align="center" prop="totalCount" width="90" />
      <el-table-column label="状态" align="center" prop="status" width="80">
        <template #default="scope">
          <el-tag :type="scope.row.status === '0' ? 'success' : 'danger'">
            {{ scope.row.status === '0' ? '正常' : '停用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" align="center" width="250" fixed="right">
        <template #default="scope">
          <el-button link type="success" icon="Position" @click="showCurlDialog(scope.row)">测试</el-button>
          <el-button link type="warning" icon="Refresh" @click="handleReset(scope.row)" v-hasPermi="['notify:key:reset']">重置</el-button>
          <el-button link type="primary" icon="Edit" @click="handleUpdate(scope.row)" v-hasPermi="['notify:key:edit']">修改</el-button>
          <el-button link type="danger" icon="Delete" @click="handleDelete(scope.row)" v-hasPermi="['notify:key:remove']">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <pagination v-show="total > 0" :total="total" v-model:page="queryParams.pageNum" v-model:limit="queryParams.pageSize" @pagination="getList" />

    <!-- 添加或修改对话框 -->
    <el-dialog :title="title" v-model="open" width="500px" append-to-body>
      <el-form ref="keyRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="密钥名称" prop="keyName">
          <el-input v-model="form.keyName" placeholder="请输入密钥名称" />
        </el-form-item>
        <el-form-item label="绑定渠道" prop="channelIds">
          <el-select v-model="form.channelIdList" multiple placeholder="请选择渠道" style="width: 100%">
            <el-option v-for="item in channelList" :key="item.channelId" :label="item.channelName" :value="item.channelId" />
          </el-select>
        </el-form-item>
        <el-form-item label="每日限额" prop="dailyLimit">
          <el-input-number v-model="form.dailyLimit" :min="1" :max="10000" />
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

    <!-- 显示新密钥对话框 -->
    <el-dialog title="API密钥已生成" v-model="showKeyDialog" width="600px" append-to-body>
      <el-alert title="请妥善保管您的API密钥，关闭后将无法再次查看完整密钥" type="warning" :closable="false" show-icon />
      <div style="margin-top: 20px;">
        <el-input v-model="newApiKey" readonly size="large">
          <template #append>
            <el-button icon="CopyDocument" @click="copyKey(newApiKey)">复制</el-button>
          </template>
        </el-input>
      </div>
      <div style="margin-top: 20px; color: #666;">
        <p>使用方式：</p>
        <code style="background: #f5f5f5; padding: 10px; display: block; border-radius: 4px;">
          curl "http://localhost:9099/notify/send/{{ newApiKey }}?title=标题&content=内容"
        </code>
      </div>
      <template #footer>
        <el-button type="primary" @click="showKeyDialog = false">我已保存</el-button>
      </template>
    </el-dialog>

    <!-- CURL 测试对话框 -->
    <el-dialog title="API 测试" v-model="curlDialogVisible" width="700px" append-to-body>
      <el-form :model="curlForm" label-width="80px">
        <el-form-item label="标题">
          <el-input v-model="curlForm.title" placeholder="请输入消息标题" />
        </el-form-item>
        <el-form-item label="内容">
          <el-input v-model="curlForm.content" type="textarea" :rows="3" placeholder="请输入消息内容" />
        </el-form-item>
      </el-form>
      <div style="margin-top: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
          <span style="font-weight: bold;">GET 请求：</span>
          <el-button size="small" icon="CopyDocument" @click="copyCurl('get')">复制</el-button>
        </div>
        <code style="background: #f5f5f5; padding: 10px; display: block; border-radius: 4px; word-break: break-all; font-size: 12px;">
          {{ curlGetCommand }}
        </code>
      </div>
      <div style="margin-top: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
          <span style="font-weight: bold;">POST 请求：</span>
          <el-button size="small" icon="CopyDocument" @click="copyCurl('post')">复制</el-button>
        </div>
        <code style="background: #f5f5f5; padding: 10px; display: block; border-radius: 4px; word-break: break-all; font-size: 12px;">
          {{ curlPostCommand }}
        </code>
      </div>
      <template #footer>
        <el-button @click="curlDialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="sendTestNotify">发送测试</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup name="NotifyKey">
import { ref, reactive, computed, onMounted, getCurrentInstance } from 'vue'
import { listNotifyKey, getNotifyKey, addNotifyKey, updateNotifyKey, delNotifyKey, generateNotifyKey, resetNotifyKey } from '@/api/notify/notify_key'
import { listNotifyChannel } from '@/api/notify/notify_channel'
import { useClipboard } from '@vueuse/core'

const { proxy } = getCurrentInstance()
const { copy } = useClipboard()

const loading = ref(false)
const showSearch = ref(true)
const keyList = ref([])
const channelList = ref([])
const total = ref(0)
const ids = ref([])
const multiple = ref(true)
const open = ref(false)
const title = ref('')
const showKeyDialog = ref(false)
const newApiKey = ref('')
const curlDialogVisible = ref(false)
const curlForm = reactive({
  apiKey: '',
  title: '测试通知',
  content: '这是一条测试消息'
})

// 获取API基础地址
const getApiBaseUrl = () => {
  // 后端API端口
  const hostname = window.location.hostname
  return `http://${hostname}:9099`
}

// 计算curl命令
const curlGetCommand = computed(() => {
  const baseUrl = getApiBaseUrl()
  const title = encodeURIComponent(curlForm.title || '')
  const content = encodeURIComponent(curlForm.content || '')
  return `curl "${baseUrl}/notify/send/${curlForm.apiKey}?title=${title}&content=${content}"`
})

const curlPostCommand = computed(() => {
  const baseUrl = getApiBaseUrl()
  const body = JSON.stringify({ title: curlForm.title, content: curlForm.content })
  return `curl -X POST "${baseUrl}/notify/send/${curlForm.apiKey}" -H "Content-Type: application/json" -d '${body}'`
})

const queryParams = reactive({
  pageNum: 1,
  pageSize: 10,
  keyName: undefined
})

const form = ref({})
const rules = {
  keyName: [{ required: true, message: '密钥名称不能为空', trigger: 'blur' }]
}

const getList = async () => {
  loading.value = true
  try {
    const res = await listNotifyKey(queryParams)
    keyList.value = res.rows
    total.value = res.total
  } finally {
    loading.value = false
  }
}

const getChannelList = async () => {
  const res = await listNotifyChannel({ pageNum: 1, pageSize: 100 })
  channelList.value = res.rows || []
}

const handleQuery = () => {
  queryParams.pageNum = 1
  getList()
}

const resetQuery = () => {
  queryParams.keyName = undefined
  handleQuery()
}

const handleSelectionChange = (selection) => {
  ids.value = selection.map(item => item.keyId)
  multiple.value = !selection.length
}

const reset = () => {
  form.value = {
    keyId: undefined,
    keyName: undefined,
    channelIdList: [],
    dailyLimit: 100,
    status: '0',
    remark: undefined
  }
}

const handleAdd = () => {
  reset()
  open.value = true
  title.value = '生成API密钥'
}

const handleUpdate = async (row) => {
  reset()
  const keyId = row.keyId || ids.value[0]
  const res = await getNotifyKey(keyId)
  form.value = res.data
  if (form.value.channelIds) {
    form.value.channelIdList = form.value.channelIds.split(',').map(Number)
  }
  open.value = true
  title.value = '修改API密钥'
}

const submitForm = async () => {
  await proxy.$refs.keyRef.validate()
  form.value.channelIds = form.value.channelIdList?.join(',') || ''
  if (form.value.keyId) {
    await updateNotifyKey(form.value)
    proxy.$modal.msgSuccess('修改成功')
  } else {
    const res = await generateNotifyKey(form.value)
    newApiKey.value = res.data.apiKey
    showKeyDialog.value = true
  }
  open.value = false
  getList()
}

const cancel = () => {
  open.value = false
  reset()
}

const handleDelete = async (row) => {
  const keyIds = row.keyId || ids.value.join(',')
  await proxy.$modal.confirm('是否确认删除？')
  await delNotifyKey(keyIds)
  getList()
  proxy.$modal.msgSuccess('删除成功')
}

const handleReset = async (row) => {
  await proxy.$modal.confirm('重置后原密钥将失效，是否继续？')
  const res = await resetNotifyKey(row.keyId)
  newApiKey.value = res.data.apiKey
  showKeyDialog.value = true
  getList()
}

const copyKey = async (key) => {
  await copy(key)
  proxy.$modal.msgSuccess('已复制到剪贴板')
}

// 显示curl测试对话框
const showCurlDialog = (row) => {
  curlForm.apiKey = row.apiKey
  curlForm.title = '测试通知'
  curlForm.content = '这是一条测试消息'
  curlDialogVisible.value = true
}

// 复制curl命令
const copyCurl = async (type) => {
  const cmd = type === 'get' ? curlGetCommand.value : curlPostCommand.value
  await copy(cmd)
  proxy.$modal.msgSuccess('已复制到剪贴板')
}

// 发送测试通知
const sendTestNotify = async () => {
  try {
    // 使用前端代理发送请求
    const response = await fetch(`/dev-api/notify/send/${curlForm.apiKey}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title: curlForm.title, content: curlForm.content })
    })
    const result = await response.json()
    if (result.code === 200) {
      proxy.$modal.msgSuccess(`发送成功 (${result.data.success_count}/${result.data.total})`)
      getList()
    } else {
      proxy.$modal.msgError(result.msg || '发送失败')
    }
  } catch (e) {
    proxy.$modal.msgError('发送失败: ' + e.message)
  }
}

onMounted(() => {
  getList()
  getChannelList()
})
</script>
