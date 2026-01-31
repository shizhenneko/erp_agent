<template>
  <div class="stream-output">
    <div class="stream-header">
      <el-icon class="header-icon"><Operation /></el-icon>
      <span class="header-title">Agent 思考过程</span>
      <el-tag 
        v-if="streamData.length > 0" 
        type="info" 
        size="small"
      >
        {{ streamData.length }} 步
      </el-tag>
    </div>

    <el-scrollbar max-height="500px">
      <el-timeline v-if="streamData.length > 0">
        <el-timeline-item
          v-for="(item, index) in filteredStreamData"
          :key="index"
          :timestamp="formatTime(item.timestamp)"
          :type="getItemType(item.type)"
          :size="getItemSize(item.type)"
        >
          <div class="timeline-content">
            <div v-if="item.type === 'iteration_start'" class="iteration-start">
              <el-tag type="primary" size="small">第 {{ item.iteration }} 轮迭代</el-tag>
            </div>

            <div v-if="item.type === 'thought'" class="thought">
              <el-icon class="thought-icon"><ChatDotRound /></el-icon>
              <span class="thought-text">{{ item.data.thought }}</span>
            </div>

            <div v-if="item.type === 'action'" class="action">
              <el-icon class="action-icon"><Setting /></el-icon>
              <span class="action-text">动作: {{ item.data.action }}</span>
            </div>

            <div v-if="item.type === 'sql_executing'" class="sql-executing">
              <el-icon class="sql-icon"><DocumentCopy /></el-icon>
              <div class="sql-content">
                <span class="sql-label">执行 SQL:</span>
                <el-input
                  type="textarea"
                  :model-value="item.data.sql"
                  :rows="getSqlRows(item.data.sql)"
                  readonly
                  class="sql-textarea"
                />
              </div>
            </div>

            <div v-if="item.type === 'sql_result'" class="sql-result">
              <el-icon class="result-icon" :class="item.data.result?.success ? 'success' : 'error'">
                <component :is="item.data.result?.success ? 'CircleCheck' : 'CircleClose'" />
              </el-icon>
              <span v-if="item.data.result?.success" class="result-text success">
                查询成功，返回 {{ item.data.result?.row_count ?? 0 }} 行数据
              </span>
              <span v-else class="result-text error">
                查询失败: {{ item.data.result?.error || item.data.error }}
              </span>
            </div>

            <div v-if="item.type === 'answer'" class="answer">
              <el-icon class="answer-icon"><ChatDotSquare /></el-icon>
              <div class="answer-content">
                <span class="answer-label">答案:</span>
                <p class="answer-text">{{ item.data.answer }}</p>
              </div>
            </div>

            <div v-if="item.type === 'final'" class="final">
              <el-icon class="final-icon" :class="item.data?.success ? 'success' : 'error'">
                <component :is="item.data?.success ? 'CircleCheck' : 'CircleClose'" />
              </el-icon>
              <div class="final-content">
                <div class="final-summary">
                  <el-tag :type="item.data?.success ? 'success' : 'danger'" size="large">
                    {{ item.data?.success ? '查询完成' : '查询失败' }}
                  </el-tag>
                </div>
                <div class="final-details">
                  <span>迭代次数: {{ item.data?.iterations }}</span>
                  <el-divider direction="vertical" />
                  <span>总耗时: {{ item.data?.total_time?.toFixed(2) }}秒</span>
                </div>
              </div>
            </div>

            <div v-if="item.type === 'error'" class="error">
              <el-icon class="error-icon"><WarningFilled /></el-icon>
              <span class="error-text">{{ item.data.error || item.error }}</span>
            </div>
          </div>
        </el-timeline-item>
      </el-timeline>

      <el-empty
        v-else
        description="暂无执行记录"
        :image-size="100"
      />
    </el-scrollbar>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import {
  Operation,
  ChatDotRound,
  Setting,
  DocumentCopy,
  ChatDotSquare,
  WarningFilled,
  CircleCheck,
  CircleClose
} from '@element-plus/icons-vue'

const props = defineProps({
  streamData: {
    type: Array,
    default: () => []
  }
})

const filteredStreamData = computed(() => {
  return props.streamData.filter(item => 
    !['start', 'connected', 'analyzing_result', 'continue_iteration'].includes(item.type)
  )
})

const formatTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp * 1000)
  return date.toLocaleTimeString('zh-CN', { 
    hour: '2-digit', 
    minute: '2-digit', 
    second: '2-digit',
    fractionalSecondDigits: 3 
  })
}

const getItemType = (type) => {
  const typeMap = {
    'iteration_start': 'primary',
    'thought': 'info',
    'sql_executing': 'warning',
    'sql_result': 'success',
    'answer': 'primary',
    'final': 'success',
    'error': 'danger'
  }
  return typeMap[type] || 'info'
}

const getItemSize = (type) => {
  const sizeMap = {
    'final': 'large',
    'error': 'large'
  }
  return sizeMap[type] || 'normal'
}

const getSqlRows = (sql) => {
  if (!sql) return 2
  const lines = sql.split('\n').length
  return Math.min(Math.max(lines, 2), 10)
}
</script>

<style scoped>
.stream-output {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  padding: 20px;
  margin-bottom: 20px;
}

.stream-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #ebeef5;
}

.header-icon {
  font-size: 24px;
  color: #409eff;
}

.header-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.timeline-content {
  padding: 8px 0;
}

.iteration-start {
  margin-bottom: 12px;
}

.thought {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  color: #606266;
  background: #f5f7fa;
  padding: 12px;
  border-radius: 4px;
  border-left: 3px solid #909399;
}

.thought-icon {
  font-size: 18px;
  color: #909399;
  flex-shrink: 0;
  margin-top: 2px;
}

.thought-text {
  flex: 1;
  line-height: 1.6;
}

.action {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #606266;
  margin: 8px 0;
}

.action-icon {
  font-size: 16px;
  color: #e6a23c;
}

.sql-executing {
  margin: 12px 0;
}

.sql-icon {
  font-size: 20px;
  color: #e6a23c;
  margin-bottom: 8px;
  display: block;
}

.sql-content {
  background: #fff7e6;
  border: 1px solid #ffd591;
  border-radius: 4px;
  padding: 12px;
}

.sql-label {
  display: block;
  font-weight: 600;
  color: #d46b08;
  margin-bottom: 8px;
}

.sql-textarea {
  margin-top: 8px;
}

.sql-textarea :deep(.el-textarea__inner) {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 13px;
  background: #fafafa;
  color: #303133;
}

.sql-result {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 12px 0;
  font-weight: 500;
}

.result-icon {
  font-size: 20px;
}

.result-icon.success {
  color: #67c23a;
}

.result-icon.error {
  color: #f56c6c;
}

.result-text.success {
  color: #67c23a;
}

.result-text.error {
  color: #f56c6c;
}

.answer {
  margin: 12px 0;
}

.answer-icon {
  font-size: 20px;
  color: #409eff;
  margin-bottom: 8px;
  display: block;
}

.answer-content {
  background: #e6f7ff;
  border: 1px solid #91d5ff;
  border-radius: 4px;
  padding: 16px;
}

.answer-label {
  display: block;
  font-weight: 600;
  color: #096dd9;
  margin-bottom: 12px;
}

.answer-text {
  margin: 0;
  color: #303133;
  line-height: 1.8;
  font-size: 15px;
}

.final {
  margin: 16px 0;
}

.final-icon {
  font-size: 24px;
  margin-bottom: 12px;
  display: block;
}

.final-icon.success {
  color: #67c23a;
}

.final-icon.error {
  color: #f56c6c;
}

.final-content {
  background: #f0f9ff;
  border: 1px solid #b3d8ff;
  border-radius: 4px;
  padding: 16px;
}

.final-summary {
  margin-bottom: 12px;
}

.final-details {
  color: #606266;
  font-size: 14px;
}

.error {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  background: #fef0f0;
  border: 1px solid #fde2e2;
  border-radius: 4px;
  padding: 12px;
}

.error-icon {
  font-size: 20px;
  color: #f56c6c;
  flex-shrink: 0;
}

.error-text {
  color: #f56c6c;
  line-height: 1.6;
}
</style>
