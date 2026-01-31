<template>
  <div class="query-input">
    <div class="input-header">
      <el-icon class="header-icon"><ChatLineRound /></el-icon>
      <span class="header-title">自然语言查询</span>
      <el-badge v-if="isLoading" :value="1" class="loading-badge">
        <el-icon class="loading-icon"><Loading /></el-icon>
      </el-badge>
    </div>

    <div class="input-content">
      <el-input
        v-model="question"
        type="textarea"
        :rows="4"
        placeholder="请输入您的查询问题，例如：&#10;• 有多少在职员工？&#10;• 每个部门有多少人？&#10;• 工资最高的前10名员工是谁？&#10;• 从去年到今年涨薪幅度最大的10位员工是谁？"
        :disabled="isLoading"
        @keydown.ctrl.enter="handleSubmit"
        @keydown.meta.enter="handleSubmit"
        class="query-textarea"
      />
    </div>

    <div class="input-footer">
      <div class="hint-text">
        <el-icon><Key /></el-icon>
        <span>Ctrl + Enter 快捷提交</span>
      </div>
      <el-button
        type="primary"
        size="large"
        :loading="isLoading"
        :disabled="!question.trim() || isLoading"
        @click="handleSubmit"
        class="submit-btn"
      >
        <template v-if="isLoading">查询中...</template>
        <template v-else>提交查询</template>
      </el-button>
    </div>

    <div class="quick-queries">
      <div class="quick-queries-title">快速查询示例：</div>
      <el-space wrap>
        <el-tag
          v-for="(example, index) in quickExamples"
          :key="index"
          type="info"
          effect="plain"
          :hit="selectedExample === index"
          @click="selectQuickExample(index)"
          class="quick-tag"
          :disabled="isLoading"
        >
          {{ example }}
        </el-tag>
      </el-space>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ChatLineRound, Loading, Key } from '@element-plus/icons-vue'

const emit = defineEmits(['submit'])

const question = ref('')
const isLoading = ref(false)
const selectedExample = ref(-1)

const quickExamples = [
  '有多少在职员工？',
  '每个部门有多少人？',
  '工资最高的前10名员工是谁？',
  '今年新入职了多少人？',
  '有没有拖欠工资的情况？'
]

const setLoading = (loading) => {
  isLoading.value = loading
}

const handleSubmit = () => {
  if (!question.value.trim() || isLoading.value) {
    return
  }

  emit('submit', question.value.trim())
}

const selectQuickExample = (index) => {
  if (isLoading.value) return
  
  selectedExample.value = index
  question.value = quickExamples[index]
  selectedExample.value = -1
}

watch(question, (newVal) => {
  if (!newVal.trim()) {
    selectedExample.value = -1
  }
})

defineExpose({
  setLoading,
  clearInput: () => {
    question.value = ''
  }
})
</script>

<style scoped>
.query-input {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  padding: 24px;
  margin-bottom: 20px;
}

.input-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.header-icon {
  font-size: 24px;
  color: #409eff;
}

.header-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  flex: 1;
}

.loading-badge {
  margin-left: auto;
}

.loading-icon {
  font-size: 20px;
  animation: rotate 1.5s linear infinite;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.input-content {
  margin-bottom: 16px;
}

.query-textarea {
  width: 100%;
}

.query-textarea :deep(.el-textarea__inner) {
  font-size: 15px;
  line-height: 1.6;
  padding: 16px;
  resize: vertical;
  min-height: 100px;
}

.input-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.hint-text {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #909399;
  font-size: 13px;
}

.submit-btn {
  padding: 12px 32px;
  font-size: 15px;
  font-weight: 500;
}

.quick-queries {
  border-top: 1px solid #ebeef5;
  padding-top: 16px;
}

.quick-queries-title {
  font-size: 14px;
  color: #606266;
  margin-bottom: 12px;
}

.quick-tag {
  cursor: pointer;
  transition: all 0.3s;
  user-select: none;
  padding: 8px 16px;
  font-size: 13px;
}

.quick-tag:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.2);
}

.quick-tag.is-hit {
  background-color: #409eff;
  color: white;
  border-color: #409eff;
}
</style>
