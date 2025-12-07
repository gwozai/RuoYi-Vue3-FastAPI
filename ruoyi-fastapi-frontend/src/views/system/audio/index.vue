<template>
  <div class="app-container">
    <!-- 生成音频卡片 -->
    <el-card class="box-card mb20">
      <template #header>
        <div class="card-header">
          <span>🎵 音频生成</span>
        </div>
      </template>
      <el-form ref="generateRef" :model="generateForm" :rules="generateRules" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="16">
            <el-form-item label="输入文本" prop="inputText">
              <el-input
                v-model="generateForm.inputText"
                type="textarea"
                :rows="4"
                placeholder="请输入要转换为语音的文本内容..."
                maxlength="5000"
                show-word-limit
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="TTS配置" prop="configId">
              <el-select v-model="generateForm.configId" placeholder="使用默认配置" style="width: 100%" clearable>
                <el-option
                  v-for="item in ttsConfigOptions"
                  :key="item.configId"
                  :label="item.configName + (item.isDefault === '1' ? ' (默认)' : '')"
                  :value="item.configId"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="音频名称" prop="audioName">
              <el-input v-model="generateForm.audioName" placeholder="可选，留空自动生成" />
            </el-form-item>
            <el-form-item label="语音模型" prop="voice">
              <el-select v-model="generateForm.voice" placeholder="请选择语音" style="width: 100%">
                <el-option
                  v-for="item in voiceOptions"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="语速" prop="speed">
              <el-slider v-model="generateForm.speed" :min="0.25" :max="4" :step="0.25" show-input />
            </el-form-item>
            <el-form-item label="音频格式" prop="responseFormat">
              <el-radio-group v-model="generateForm.responseFormat">
                <el-radio label="mp3">MP3</el-radio>
                <el-radio label="wav">WAV</el-radio>
                <el-radio label="flac">FLAC</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item>
          <el-button type="primary" :loading="generating" @click="handleGenerate" icon="Microphone">
            {{ generating ? '生成中...' : '生成音频' }}
          </el-button>
          <el-button @click="resetGenerateForm" icon="Refresh">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 搜索区域 -->
    <el-form :model="queryParams" ref="queryRef" :inline="true" v-show="showSearch" label-width="80px">
      <el-form-item label="音频名称" prop="audioName">
        <el-input
          v-model="queryParams.audioName"
          placeholder="请输入音频名称"
          clearable
          style="width: 200px"
          @keyup.enter="handleQuery"
        />
      </el-form-item>
      <el-form-item label="语音模型" prop="voice">
        <el-select v-model="queryParams.voice" placeholder="请选择" clearable style="width: 200px">
          <el-option
            v-for="item in voiceOptions"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="状态" prop="status">
        <el-select v-model="queryParams.status" placeholder="请选择状态" clearable style="width: 120px">
          <el-option label="生成中" value="0" />
          <el-option label="成功" value="1" />
          <el-option label="失败" value="2" />
        </el-select>
      </el-form-item>
      <el-form-item label="创建时间" style="width: 380px">
        <el-date-picker
          v-model="dateRange"
          value-format="YYYY-MM-DD"
          type="daterange"
          range-separator="-"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
        />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" icon="Search" @click="handleQuery">搜索</el-button>
        <el-button icon="Refresh" @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>

    <!-- 操作按钮 -->
    <el-row :gutter="10" class="mb8">
      <el-col :span="1.5">
        <el-button
          type="danger"
          plain
          icon="Delete"
          :disabled="multiple"
          @click="handleDelete"
          v-hasPermi="['system:audio:remove']"
        >删除</el-button>
      </el-col>
      <right-toolbar v-model:showSearch="showSearch" @queryTable="getList"></right-toolbar>
    </el-row>

    <!-- 数据表格 -->
    <el-table v-loading="loading" :data="audioList" @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="55" align="center" />
      <el-table-column label="ID" align="center" prop="audioId" width="80" />
      <el-table-column label="音频名称" align="center" prop="audioName" min-width="150" show-overflow-tooltip />
      <el-table-column label="输入文本" align="center" prop="inputText" min-width="200" show-overflow-tooltip />
      <el-table-column label="语音模型" align="center" prop="voice" width="180">
        <template #default="scope">
          <span>{{ getVoiceLabel(scope.row.voice) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="语速" align="center" prop="speed" width="80" />
      <el-table-column label="格式" align="center" prop="responseFormat" width="80" />
      <el-table-column label="文件大小" align="center" prop="fileSize" width="100">
        <template #default="scope">
          <span>{{ formatFileSize(scope.row.fileSize) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="状态" align="center" prop="status" width="100">
        <template #default="scope">
          <el-tag v-if="scope.row.status === '0'" type="warning">生成中</el-tag>
          <el-tag v-else-if="scope.row.status === '1'" type="success">成功</el-tag>
          <el-tag v-else-if="scope.row.status === '2'" type="danger">失败</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="创建时间" align="center" prop="createTime" width="180">
        <template #default="scope">
          <span>{{ parseTime(scope.row.createTime) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" align="center" width="200" fixed="right">
        <template #default="scope">
          <el-button
            v-if="scope.row.status === '1'"
            link
            type="primary"
            icon="VideoPlay"
            @click="handlePlay(scope.row)"
          >播放</el-button>
          <el-button
            v-if="scope.row.status === '1'"
            link
            type="primary"
            icon="Download"
            @click="handleDownload(scope.row)"
            v-hasPermi="['system:audio:query']"
          >下载</el-button>
          <el-button
            link
            type="primary"
            icon="Delete"
            @click="handleDelete(scope.row)"
            v-hasPermi="['system:audio:remove']"
          >删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <pagination
      v-show="total > 0"
      :total="total"
      v-model:page="queryParams.pageNum"
      v-model:limit="queryParams.pageSize"
      @pagination="getList"
    />

    <!-- 音频播放对话框 -->
    <el-dialog v-model="playDialogVisible" title="音频播放" width="500px" @close="stopAudio">
      <div class="audio-player">
        <p class="audio-name">{{ currentAudio.audioName }}</p>
        <audio ref="audioPlayer" :src="currentAudioUrl" controls style="width: 100%"></audio>
        <p class="audio-text">{{ currentAudio.inputText }}</p>
      </div>
    </el-dialog>
  </div>
</template>

<script setup name="Audio">
import { listAudio, getAudio, delAudio, generateAudio, getVoices, downloadAudio, getTtsConfigs } from "@/api/system/audio";

const { proxy } = getCurrentInstance();

const audioList = ref([]);
const loading = ref(true);
const showSearch = ref(true);
const ids = ref([]);
const multiple = ref(true);
const total = ref(0);
const dateRange = ref([]);
const generating = ref(false);
const voiceOptions = ref([]);
const ttsConfigOptions = ref([]);
const playDialogVisible = ref(false);
const currentAudio = ref({});
const currentAudioUrl = ref('');
const audioPlayer = ref(null);

const data = reactive({
  queryParams: {
    pageNum: 1,
    pageSize: 10,
    audioName: null,
    voice: null,
    status: null,
    beginTime: null,
    endTime: null,
  },
  generateForm: {
    configId: null,
    inputText: '',
    audioName: '',
    voice: 'zh-CN-XiaoxiaoNeural',
    speed: 1.0,
    responseFormat: 'mp3',
    remark: ''
  },
  generateRules: {
    inputText: [
      { required: true, message: "请输入要转换的文本", trigger: "blur" },
      { min: 1, max: 5000, message: "文本长度在 1 到 5000 个字符", trigger: "blur" }
    ],
  }
});

const { queryParams, generateForm, generateRules } = toRefs(data);

/** 获取语音模型列表 */
function loadVoices() {
  getVoices().then(response => {
    voiceOptions.value = response.data || [];
  });
}

/** 获取TTS配置列表 */
function loadTtsConfigs() {
  getTtsConfigs().then(response => {
    ttsConfigOptions.value = response.data || [];
    // 如果有默认配置，自动选中
    const defaultConfig = ttsConfigOptions.value.find(c => c.isDefault === '1');
    if (defaultConfig) {
      generateForm.value.configId = defaultConfig.configId;
    }
  });
}

/** 查询音频列表 */
function getList() {
  loading.value = true;
  if (dateRange.value && dateRange.value.length === 2) {
    queryParams.value.beginTime = dateRange.value[0];
    queryParams.value.endTime = dateRange.value[1];
  } else {
    queryParams.value.beginTime = null;
    queryParams.value.endTime = null;
  }
  listAudio(queryParams.value).then(response => {
    audioList.value = response.rows;
    total.value = response.total;
    loading.value = false;
  });
}

/** 搜索按钮操作 */
function handleQuery() {
  queryParams.value.pageNum = 1;
  getList();
}

/** 重置按钮操作 */
function resetQuery() {
  dateRange.value = [];
  proxy.resetForm("queryRef");
  handleQuery();
}

/** 多选框选中数据 */
function handleSelectionChange(selection) {
  ids.value = selection.map(item => item.audioId);
  multiple.value = !selection.length;
}

/** 生成音频 */
function handleGenerate() {
  proxy.$refs["generateRef"].validate(valid => {
    if (valid) {
      generating.value = true;
      generateAudio(generateForm.value).then(response => {
        proxy.$modal.msgSuccess("音频生成成功");
        resetGenerateForm();
        getList();
      }).finally(() => {
        generating.value = false;
      });
    }
  });
}

/** 重置生成表单 */
function resetGenerateForm() {
  generateForm.value = {
    inputText: '',
    audioName: '',
    voice: 'zh-CN-XiaoxiaoNeural',
    speed: 1.0,
    responseFormat: 'mp3',
    remark: ''
  };
  proxy.resetForm("generateRef");
}

/** 播放音频 */
function handlePlay(row) {
  currentAudio.value = row;
  // 使用后端接口获取音频
  currentAudioUrl.value = import.meta.env.VITE_APP_BASE_API + row.filePath;
  playDialogVisible.value = true;
}

/** 停止播放 */
function stopAudio() {
  if (audioPlayer.value) {
    audioPlayer.value.pause();
    audioPlayer.value.currentTime = 0;
  }
}

/** 下载音频 */
function handleDownload(row) {
  downloadAudio(row.audioId).then(response => {
    const blob = new Blob([response], { type: `audio/${row.responseFormat}` });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${row.audioName}.${row.responseFormat}`;
    link.click();
    window.URL.revokeObjectURL(url);
  });
}

/** 删除按钮操作 */
function handleDelete(row) {
  const audioIds = row.audioId || ids.value;
  proxy.$modal.confirm('是否确认删除音频编号为"' + audioIds + '"的数据项？').then(function() {
    return delAudio(audioIds);
  }).then(() => {
    getList();
    proxy.$modal.msgSuccess("删除成功");
  }).catch(() => {});
}

/** 获取语音模型标签 */
function getVoiceLabel(value) {
  const voice = voiceOptions.value.find(v => v.value === value);
  return voice ? voice.label : value;
}

/** 格式化文件大小 */
function formatFileSize(bytes) {
  if (!bytes || bytes === 0) return '-';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

loadVoices();
loadTtsConfigs();
getList();
</script>

<style scoped>
.mb20 {
  margin-bottom: 20px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
}
.audio-player {
  text-align: center;
}
.audio-name {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 15px;
}
.audio-text {
  margin-top: 15px;
  padding: 10px;
  background-color: #f5f7fa;
  border-radius: 4px;
  font-size: 14px;
  color: #606266;
  max-height: 100px;
  overflow-y: auto;
}
</style>
