<template>
  <div class="dashboard">
    <div class="header">
      <div class="header-content">
        <div class="header-left">
          <el-icon class="logo-icon"><DataAnalysis /></el-icon>
          <h1 class="title">ERP Agent 智能查询系统</h1>
        </div>
        <div class="header-right">
          <el-tag :type="isConnected ? 'success' : 'danger'" size="large">
            <el-icon class="status-icon">
              <component :is="isConnected ? 'CircleCheckFilled' : 'CircleCloseFilled'" />
            </el-icon>
            {{ isConnected ? '已连接' : '未连接' }}
          </el-tag>
        </div>
      </div>
    </div>

    <div class="main-content">
      <div class="container">
        <QueryInput
          ref="queryInputRef"
          @submit="handleSubmit"
        />

        <div class="output-section">
          <StreamOutput
            v-if="streamData.length > 0 || isProcessing"
            :stream-data="streamData"
          />

          <div v-if="currentSQL" class="sql-section">
            <SQLViewer :sql="currentSQL" :auto-expand="true" />
          </div>

          <div v-if="tableData.length > 0" class="table-section">
            <ResultTable :table-data="tableData" :columns="tableColumns" />
          </div>

          <el-empty
            v-if="!hasResults && !isProcessing"
            description="输入问题后，AI Agent 将自动生成 SQL 并返回答案"
            :image-size="200"
          />
        </div>
      </div>
    </div>

    <div class="footer">
      <p class="footer-text">
        Powered by Kimi-K2 | 基于 ReAct 范式的智能数据查询助手
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { 
  DataAnalysis, 
  CircleCheckFilled, 
  CircleCloseFilled 
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useWebSocket } from '../composables/useWebSocket'

import QueryInput from '../components/QueryInput.vue'
import StreamOutput from '../components/StreamOutput.vue'
import ResultTable from '../components/ResultTable.vue'
import SQLViewer from '../components/SQLViewer.vue'

const {
  isConnected,
  streamData,
  send,
  clearStream
} = useWebSocket()

const queryInputRef = ref(null)
const isProcessing = ref(false)
const currentSQL = ref('')
const tableData = ref([])
const tableColumns = ref([])

const hasResults = computed(() => {
  return streamData.value.length > 0 || tableData.value.length > 0
})

watch(streamData, (newData) => {
  if (!newData || newData.length === 0) return

  const lastItem = newData[newData.length - 1]

  if (lastItem.type === 'start') {
    isProcessing.value = true
    currentSQL.value = ''
    tableData.value = []
    tableColumns.value = []
  }

  if (lastItem.type === 'sql_executing') {
    currentSQL.value = lastItem.data.sql || ''
  }

  if (lastItem.type === 'sql_result' && lastItem.data?.result?.success) {
    const resultData = lastItem.data.result.data || []
    
    if (Array.isArray(resultData) && resultData.length > 0) {
      const firstRow = resultData[0]
      
      if (Array.isArray(firstRow)) {
        tableColumns.value = firstRow.map((_, index) => `column_${index}`)
        tableData.value = resultData.map(row => {
          return row.reduce((acc, val, index) => {
            acc[`column_${index}`] = val
            return acc
          }, {})
        })
      } else if (typeof firstRow === 'object' && firstRow !== null) {
        tableColumns.value = Object.keys(firstRow)
        tableData.value = resultData
      }
    }
  }

  if (lastItem.type === 'final') {
    isProcessing.value = false
    
    if (queryInputRef.value) {
      queryInputRef.value.setLoading(false)
    }

    if (lastItem.data?.success) {
      ElMessage.success('查询完成')
    } else {
      ElMessage.error(`查询失败: ${lastItem.data?.error || '未知错误'}`)
    }
  }

  if (lastItem.type === 'error') {
    isProcessing.value = false
    
    if (queryInputRef.value) {
      queryInputRef.value.setLoading(false)
    }
    
    ElMessage.error(`执行错误: ${lastItem.data.error || lastItem.error}`)
  }
}, { deep: true })

const handleSubmit = async (question) => {
  if (!isConnected.value) {
    ElMessage.error('未连接到服务器，请稍后再试')
    return
  }

  try {
    clearStream()
    
    if (queryInputRef.value) {
      queryInputRef.value.setLoading(true)
    }

    send({
      action: 'query',
      question: question
    })

    ElMessage.info('查询已提交，正在处理...')
  } catch (error) {
    console.error('Submit failed:', error)
    ElMessage.error('提交查询失败')
    
    if (queryInputRef.value) {
      queryInputRef.value.setLoading(false)
    }
  }
}
</script>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.header {
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.logo-icon {
  font-size: 32px;
  color: #409eff;
}

.title {
  font-size: 24px;
  font-weight: 700;
  color: #303133;
  margin: 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-icon {
  margin-right: 4px;
}

.main-content {
  flex: 1;
  padding: 40px 20px;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
}

.output-section {
  margin-top: 24px;
}

.sql-section,
.table-section {
  margin-bottom: 24px;
}

.footer {
  background: white;
  padding: 20px;
  text-align: center;
  border-top: 1px solid #ebeef5;
}

.footer-text {
  margin: 0;
  color: #909399;
  font-size: 13px;
}
</style>
