<template>
  <div class="app-container">
    <el-form :model="queryParams" ref="queryRef" :inline="true" v-show="showSearch">
      <el-form-item label="平台名称" prop="platformName">
        <el-input v-model="queryParams.platformName" placeholder="请输入平台名称" clearable style="width: 200px" @keyup.enter="handleQuery" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" icon="Search" @click="handleQuery">搜索</el-button>
        <el-button icon="Refresh" @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>

    <el-row :gutter="10" class="mb8">
      <el-col :span="1.5">
        <el-button type="primary" plain icon="Plus" @click="handleAdd" v-hasPermi="['notify:platform:add']">新增</el-button>
      </el-col>
      <right-toolbar v-model:showSearch="showSearch" @queryTable="getList"></right-toolbar>
    </el-row>

    <el-table v-loading="loading" :data="platformList">
      <el-table-column label="平台ID" align="center" prop="platformId" width="80" />
      <el-table-column label="平台名称" align="center" prop="platformName" width="120" />
      <el-table-column label="平台编码" align="center" prop="platformCode" width="100" />
      <el-table-column label="Webhook模板" align="center" prop="webhookTemplate" min-width="300" show-overflow-tooltip />
      <el-table-column label="请求方式" align="center" prop="requestMethod" width="90" />
      <el-table-column label="状态" align="center" prop="status" width="80">
        <template #default="scope">
          <el-tag :type="scope.row.status === '0' ? 'success' : 'danger'">
            {{ scope.row.status === '0' ? '正常' : '停用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="排序" align="center" prop="orderNum" width="60" />
      <el-table-column label="操作" align="center" width="150" fixed="right">
        <template #default="scope">
          <el-button link type="primary" icon="Edit" @click="handleUpdate(scope.row)" v-hasPermi="['notify:platform:edit']">修改</el-button>
          <el-button link type="danger" icon="Delete" @click="handleDelete(scope.row)" v-hasPermi="['notify:platform:remove']">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <pagination v-show="total > 0" :total="total" v-model:page="queryParams.pageNum" v-model:limit="queryParams.pageSize" @pagination="getList" />

    <!-- 添加或修改对话框 -->
    <el-dialog :title="title" v-model="open" width="600px" append-to-body>
      <el-form ref="platformRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="平台名称" prop="platformName">
          <el-input v-model="form.platformName" placeholder="请输入平台名称" />
        </el-form-item>
        <el-form-item label="平台编码" prop="platformCode">
          <el-input v-model="form.platformCode" placeholder="请输入平台编码，如 feishu, wecom" />
        </el-form-item>
        <el-form-item label="Webhook模板" prop="webhookTemplate">
          <el-input v-model="form.webhookTemplate" placeholder="请输入Webhook模板，使用{key}作为密钥占位符" />
        </el-form-item>
        <el-form-item label="请求方式" prop="requestMethod">
          <el-select v-model="form.requestMethod" placeholder="请选择请求方式">
            <el-option label="POST" value="POST" />
            <el-option label="GET" value="GET" />
          </el-select>
        </el-form-item>
        <el-form-item label="Content-Type" prop="contentType">
          <el-input v-model="form.contentType" placeholder="请输入Content-Type" />
        </el-form-item>
        <el-form-item label="请求体模板" prop="bodyTemplate">
          <el-input v-model="form.bodyTemplate" type="textarea" :rows="4" placeholder="请输入请求体模板，使用{content}作为内容占位符" />
        </el-form-item>
        <el-form-item label="排序" prop="orderNum">
          <el-input-number v-model="form.orderNum" :min="0" />
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

<script setup name="NotifyPlatform">
import { ref, reactive, onMounted, getCurrentInstance } from 'vue'
import { listNotifyPlatform, getNotifyPlatform, addNotifyPlatform, updateNotifyPlatform, delNotifyPlatform } from '@/api/notify/notify_platform'

const { proxy } = getCurrentInstance()

const loading = ref(false)
const showSearch = ref(true)
const platformList = ref([])
const total = ref(0)
const open = ref(false)
const title = ref('')

const queryParams = reactive({
  pageNum: 1,
  pageSize: 10,
  platformName: undefined
})

const form = ref({})
const rules = {
  platformName: [{ required: true, message: '平台名称不能为空', trigger: 'blur' }],
  platformCode: [{ required: true, message: '平台编码不能为空', trigger: 'blur' }],
  webhookTemplate: [{ required: true, message: 'Webhook模板不能为空', trigger: 'blur' }]
}

const getList = async () => {
  loading.value = true
  try {
    const res = await listNotifyPlatform(queryParams)
    platformList.value = res.rows
    total.value = res.total
  } finally {
    loading.value = false
  }
}

const handleQuery = () => {
  queryParams.pageNum = 1
  getList()
}

const resetQuery = () => {
  queryParams.platformName = undefined
  handleQuery()
}

const reset = () => {
  form.value = {
    platformId: undefined,
    platformName: undefined,
    platformCode: undefined,
    webhookTemplate: undefined,
    requestMethod: 'POST',
    contentType: 'application/json',
    bodyTemplate: '{"msg_type":"text","content":{"text":"{content}"}}',
    orderNum: 0,
    status: '0',
    remark: undefined
  }
}

const handleAdd = () => {
  reset()
  open.value = true
  title.value = '添加平台'
}

const handleUpdate = async (row) => {
  reset()
  const platformId = row.platformId
  const res = await getNotifyPlatform(platformId)
  form.value = res.data
  open.value = true
  title.value = '修改平台'
}

const submitForm = async () => {
  await proxy.$refs.platformRef.validate()
  if (form.value.platformId) {
    await updateNotifyPlatform(form.value)
    proxy.$modal.msgSuccess('修改成功')
  } else {
    await addNotifyPlatform(form.value)
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
  await proxy.$modal.confirm('是否确认删除？')
  await delNotifyPlatform(row.platformId)
  getList()
  proxy.$modal.msgSuccess('删除成功')
}

onMounted(() => {
  getList()
})
</script>
