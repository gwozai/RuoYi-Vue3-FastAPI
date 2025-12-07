<template>
  <div class="app-container">
    <el-form :model="queryParams" ref="queryRef" :inline="true" v-show="showSearch" label-width="68px">
      <el-form-item v-if="isAdmin" label="用户" prop="userId">
        <el-select
          v-model="queryParams.userId"
          placeholder="请选择用户"
          clearable
          filterable
          style="width: 240px"
        >
          <el-option
            v-for="user in userList"
            :key="user.userId"
            :label="user.nickName + ' (' + user.userName + ')'"
            :value="user.userId"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="配置名称" prop="configName">
        <el-input
          v-model="queryParams.configName"
          placeholder="请输入配置名称"
          clearable
          style="width: 240px"
          @keyup.enter="handleQuery"
        />
      </el-form-item>
      <el-form-item label="API地址" prop="apiUrl">
        <el-input
          v-model="queryParams.apiUrl"
          placeholder="请输入API地址"
          clearable
          style="width: 240px"
          @keyup.enter="handleQuery"
        />
      </el-form-item>
      <el-form-item label="API密钥" prop="apiKey">
        <el-input
          v-model="queryParams.apiKey"
          placeholder="请输入API密钥"
          clearable
          style="width: 240px"
          @keyup.enter="handleQuery"
        />
      </el-form-item>
      <el-form-item label="API模型" prop="apiModel">
        <el-input
          v-model="queryParams.apiModel"
          placeholder="请输入API模型"
          clearable
          style="width: 240px"
          @keyup.enter="handleQuery"
        />
      </el-form-item>
      <el-form-item label="是否默认" prop="isDefault">
        <el-input
          v-model="queryParams.isDefault"
          placeholder="请输入是否默认"
          clearable
          style="width: 240px"
          @keyup.enter="handleQuery"
        />
      </el-form-item>
      <el-form-item label="状态" prop="status">
        <el-select v-model="queryParams.status" placeholder="请选择状态" clearable style="width: 240px">
          <el-option label="请选择字典生成" value="" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" icon="Search" @click="handleQuery">搜索</el-button>
        <el-button icon="Refresh" @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>

    <el-row :gutter="10" class="mb8">
      <el-col :span="1.5">
        <el-button
          type="primary"
          plain
          icon="Plus"
          @click="handleAdd"
          v-hasPermi="['system:ttsConfig:add']"
        >新增</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="success"
          plain
          icon="Edit"
          :disabled="single"
          @click="handleUpdate"
          v-hasPermi="['system:ttsConfig:edit']"
        >修改</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="danger"
          plain
          icon="Delete"
          :disabled="multiple"
          @click="handleDelete"
          v-hasPermi="['system:ttsConfig:remove']"
        >删除</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="warning"
          plain
          icon="Download"
          @click="handleExport"
          v-hasPermi="['system:ttsConfig:export']"
        >导出</el-button>
      </el-col>
      <right-toolbar v-model:showSearch="showSearch" @queryTable="getList"></right-toolbar>
    </el-row>

    <el-table v-loading="loading" :data="ttsConfigList" @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="55" align="center" />
      <el-table-column label="配置ID" align="center" prop="configId" />
      <el-table-column label="用户ID" align="center" prop="userId" />
      <el-table-column label="配置名称" align="center" prop="configName" />
      <el-table-column label="API地址" align="center" prop="apiUrl" />
      <el-table-column label="API密钥" align="center" prop="apiKey" />
      <el-table-column label="API模型" align="center" prop="apiModel" />
      <el-table-column label="是否默认" align="center" prop="isDefault" />
      <el-table-column label="状态" align="center" prop="status" />
      <el-table-column label="备注" align="center" prop="remark" />
      <el-table-column label="操作" align="center" class-name="small-padding fixed-width">
        <template #default="scope">
          <el-button link type="primary" icon="Edit" @click="handleUpdate(scope.row)" v-hasPermi="['system:ttsConfig:edit']">修改</el-button>
          <el-button link type="primary" icon="Delete" @click="handleDelete(scope.row)" v-hasPermi="['system:ttsConfig:remove']">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <pagination
      v-show="total>0"
      :total="total"
      v-model:page="queryParams.pageNum"
      v-model:limit="queryParams.pageSize"
      @pagination="getList"
    />

    <!-- 添加或修改TTS API配置对话框 -->
    <el-dialog :title="title" v-model="open" width="500px" append-to-body>
      <el-form ref="ttsConfigRef" :model="form" :rules="rules" label-width="80px">
      <el-form-item v-if="isAdmin && renderField(true, true)" label="用户" prop="userId">
        <el-select
          v-model="form.userId"
          placeholder="留空则为当前用户"
          clearable
          filterable
          style="width: 100%"
        >
          <el-option
            v-for="user in userList"
            :key="user.userId"
            :label="user.nickName + ' (' + user.userName + ')'"
            :value="user.userId"
          />
        </el-select>
      </el-form-item>
      <el-form-item v-if="renderField(true, true)" label="配置名称" prop="configName">
        <el-input v-model="form.configName" placeholder="请输入配置名称" />
      </el-form-item>
      <el-form-item v-if="renderField(true, true)" label="API地址" prop="apiUrl">
        <el-input v-model="form.apiUrl" placeholder="请输入API地址" />
      </el-form-item>
      <el-form-item v-if="renderField(true, true)" label="API密钥" prop="apiKey">
        <el-input v-model="form.apiKey" placeholder="请输入API密钥" />
      </el-form-item>
      <el-form-item v-if="renderField(true, true)" label="API模型" prop="apiModel">
        <el-input v-model="form.apiModel" placeholder="请输入API模型" />
      </el-form-item>
      <el-form-item v-if="renderField(true, true)" label="是否默认" prop="isDefault">
        <el-radio-group v-model="form.isDefault">
          <el-radio label="1">是</el-radio>
          <el-radio label="0">否</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item v-if="renderField(true, true)" label="状态" prop="status">
        <el-radio-group v-model="form.status">
          <el-radio label="0">正常</el-radio>
          <el-radio label="1">停用</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item v-if="renderField(true, true)" label="备注" prop="remark">
        <el-input v-model="form.remark" placeholder="请输入备注" />
      </el-form-item>

      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button type="primary" @click="submitForm">确 定</el-button>
          <el-button @click="cancel">取 消</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup name="Ttsconfig">
import { listTtsconfig, getTtsconfig, delTtsconfig, addTtsconfig, updateTtsconfig } from "@/api/system/ttsConfig";
import { listUser } from "@/api/system/user";
import useUserStore from '@/store/modules/user';

const { proxy } = getCurrentInstance();
const userStore = useUserStore();

// 判断是否为管理员
const isAdmin = computed(() => {
  return userStore.roles.includes('admin');
});

const ttsConfigList = ref([]);
const userList = ref([]);
const open = ref(false);
const loading = ref(true);
const showSearch = ref(true);
const ids = ref([]);
const single = ref(true);
const multiple = ref(true);
const total = ref(0);
const title = ref("");

const data = reactive({
  form: {},
  queryParams: {
    pageNum: 1,
    pageSize: 10,
    userId: null,
    configName: null,
    apiUrl: null,
    apiKey: null,
    apiModel: null,
    isDefault: null,
    status: null,
  },
  rules: {
    configName: [
      { required: true, message: "配置名称不能为空", trigger: "blur" }
    ],
    apiUrl: [
      { required: true, message: "API地址不能为空", trigger: "blur" }
    ],
  }
});

const { queryParams, form, rules } = toRefs(data);

/** 查询TTS API配置列表 */
function getList() {
  loading.value = true;
  listTtsconfig(queryParams.value).then(response => {
    ttsConfigList.value = response.rows;
    total.value = response.total;
    loading.value = false;
  });
}

/** 取消按钮 */
function cancel() {
  open.value = false;
  reset();
}

/** 表单重置 */
function reset() {
  form.value = {
    configId: null,
    userId: null,
    configName: null,
    apiUrl: null,
    apiKey: null,
    apiModel: null,
    isDefault: null,
    status: null,
    createBy: null,
    createTime: null,
    updateBy: null,
    updateTime: null,
    remark: null,
  };
  proxy.resetForm("ttsConfigRef");
}

/** 搜索按钮操作 */
function handleQuery() {
  queryParams.value.pageNum = 1;
  getList();
}

/** 重置按钮操作 */
function resetQuery() {
  proxy.resetForm("queryRef");
  handleQuery();
}

/** 多选框选中数据  */
function handleSelectionChange(selection) {
  ids.value = selection.map(item => item.configId);
  single.value = selection.length != 1;
  multiple.value = !selection.length;
}

/** 新增按钮操作 */
function handleAdd() {
  reset();
  open.value = true;
  title.value = "添加TTS API配置";
}

/** 修改按钮操作 */
function handleUpdate(row) {
  reset();
  const _configId = row.configId || ids.value;
  getTtsconfig(_configId).then(response => {
    form.value = response.data;
    open.value = true;
    title.value = "修改TTS API配置";
  });
}

/** 提交按钮 */
function submitForm() {
  proxy.$refs["ttsConfigRef"].validate(valid => {
    if (valid) {
      if (form.value.configId != null) {
        updateTtsconfig(form.value).then(response => {
          proxy.$modal.msgSuccess("修改成功");
          open.value = false;
          getList();
        });
      } else {
        addTtsconfig(form.value).then(response => {
          proxy.$modal.msgSuccess("新增成功");
          open.value = false;
          getList();
        });
      }
    }
  });
}

/** 删除按钮操作 */
function handleDelete(row) {
  const _configIds = row.configId || ids.value;
  proxy.$modal.confirm('是否确认删除TTS API配置编号为"' + _configIds + '"的数据项？').then(function() {
    return delTtsconfig(_configIds);
  }).then(() => {
    getList();
    proxy.$modal.msgSuccess("删除成功");
  }).catch(() => {});
}


/** 导出按钮操作 */
function handleExport() {
  proxy.download('system/ttsConfig/export', {
    ...queryParams.value
  }, `ttsConfig_${new Date().getTime()}.xlsx`);
}

/** 是否渲染字段 */
function renderField(insert, edit) {
  return form.value.configId == null ? insert : edit;
}

/** 加载用户列表 */
function loadUserList() {
  if (isAdmin.value) {
    listUser({ pageNum: 1, pageSize: 1000 }).then(response => {
      userList.value = response.rows || [];
    });
  }
}

loadUserList();
getList();
</script>