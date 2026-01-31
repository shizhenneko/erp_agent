<template>
  <div class="sql-viewer" v-if="sql">
    <div class="sql-header">
      <div class="header-left">
        <el-icon class="header-icon"><Document /></el-icon>
        <span class="header-title">生成的 SQL 语句</span>
      </div>
      <div class="header-actions">
        <el-button
          type="primary"
          size="small"
          :icon="CopyDocument"
          @click="copySQL"
        >
          复制
        </el-button>
        <el-button
          type="default"
          size="small"
          :icon="isExpanded ? ArrowUp : ArrowDown"
          @click="toggleExpand"
        >
          {{ isExpanded ? '收起' : '展开' }}
        </el-button>
      </div>
    </div>

    <el-collapse-transition>
      <div v-show="isExpanded" class="sql-content">
        <pre class="sql-code"><code>{{ sql }}</code></pre>
      </div>
    </el-collapse-transition>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { Document, CopyDocument, ArrowUp, ArrowDown } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  sql: {
    type: String,
    default: ''
  },
  autoExpand: {
    type: Boolean,
    default: false
  }
})

const isExpanded = ref(false)

onMounted(() => {
  if (props.autoExpand) {
    isExpanded.value = true
  }
})

watch(() => props.sql, (newVal) => {
  if (newVal && props.autoExpand) {
    isExpanded.value = true
  }
})

const copySQL = async () => {
  try {
    await navigator.clipboard.writeText(props.sql)
    ElMessage.success('SQL 已复制到剪贴板')
  } catch (error) {
    ElMessage.error('复制失败，请手动复制')
  }
}

const toggleExpand = () => {
  isExpanded.value = !isExpanded.value
}
</script>

<style scoped>
.sql-viewer {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
  overflow: hidden;
}

.sql-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: #fafafa;
  border-bottom: 1px solid #ebeef5;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-icon {
  font-size: 18px;
  color: #67c23a;
}

.header-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.sql-content {
  padding: 20px;
  background: #fafafa;
}

.sql-code {
  margin: 0;
  padding: 16px;
  background: white;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', monospace;
  font-size: 13px;
  line-height: 1.6;
  color: #303133;
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-all;
}

.sql-code code {
  font-family: inherit;
}
</style>
