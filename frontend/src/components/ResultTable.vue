<template>
  <div class="result-table" v-if="tableData.length > 0">
    <div class="table-header">
      <div class="header-left">
        <el-icon class="header-icon"><Grid /></el-icon>
        <span class="header-title">查询结果</span>
        <el-tag type="success" size="small">
          {{ tableData.length }} 行
        </el-tag>
        <el-tag type="info" size="small">
          {{ columns.length }} 列
        </el-tag>
      </div>
      <div class="header-actions">
        <el-button
          type="primary"
          size="small"
          :icon="Download"
          @click="exportToCSV"
        >
          导出 CSV
        </el-button>
      </div>
    </div>

    <div class="table-content">
      <el-table
        :data="paginatedData"
        :columns="tableColumns"
        border
        stripe
        highlight-current-row
        style="width: 100%"
        :header-cell-style="headerCellStyle"
        :cell-style="cellStyle"
        max-height="600"
        @sort-change="handleSortChange"
      >
        <el-table-column
          type="index"
          label="#"
"
          width="60"
          fixed
        />
        <el-table-column
          v-for="col in columns"
          :key="col"
          :prop="col"
          :label="col"
          :sortable="true"
          show-overflow-tooltip
          min-width="120"
        >
          <template #default="{ row }">
            <span>{{ formatCellValue(row[col]) }}</span>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-if="tableData.length > pageSize"
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100, 500]"
        :total="tableData.length"
        layout="total, sizes, prev, pager, next, jumper"
        background
        class="pagination"
      />
    </div>
  </div>

  <el-empty
    v-else-if="showEmpty"
    description="暂无查询结果数据"
    :image-size="150"
  />
</template>

<script setup>
import { ref, computed } from 'vue'
import { Grid, Download } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  tableData: {
    type: Array,
    default: () => []
  },
  columns: {
    type: Array,
    default: () => []
  },
  showEmpty: {
    type: Boolean,
    default: true
  }
})

const currentPage = ref(1)
const pageSize = ref(20)
const sortProp = ref('')
const sortOrder = ref('')

const tableColumns = computed(() => {
  return props.columns.map(col => ({
    prop: col,
    label: col
  }))
})

const sortedData = computed(() => {
  if (!sortProp.value || !sortOrder.value) {
    return props.tableData
  }

  return [...props.tableData].sort((a, b) => {
    const aVal = a[sortProp.value]
    const bVal = b[sortProp.value]

    if (sortOrder.value === 'ascending') {
      return aVal > bVal ? 1 : -1
    } else {
      return aVal < bVal ? 1 : -1
    }
  })
})

const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return sortedData.value.slice(start, end)
})

const headerCellStyle = () => {
  return {
    backgroundColor: '#f5f7fa',
    color: '#303133',
    fontWeight: '600',
    fontSize: '13px',
    padding: '12px 8px'
  }
}

const cellStyle = () => {
  return {
    fontSize: '13px',
    padding: '10px 8px'
  }
}

const formatCellValue = (value) => {
  if (value === null || value === undefined) {
    return 'NULL'
  }
  if (typeof value === 'number') {
    return value.toLocaleString('zh-CN', { maximumFractionDigits: 2 })
  }
  return String(value)
}

const handleSortChange = ({ prop, order }) => {
  sortProp.value = prop
  sortOrder.value = order
}

const exportToCSV = () => {
  try {
    const headers = props.columns.join(',')
    const rows = props.tableData.map(row => {
      return props.columns.map(col => {
        const value = row[col]
        if (value === null || value === undefined) {
          return ''
        }
        const strValue = String(value)
        if (strValue.includes(',') || strValue.includes('"') || strValue.includes('\n')) {
          return `"${strValue.replace(/"/g, '""')}"`
        }
        return strValue
      }).join(',')
    })
    
    const csvContent = [headers, ...rows].join('\n')
    const bom = '\uFEFF'
    const blob = new Blob([bom + csvContent], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    
    link.href = url
    link.download = `query_result_${Date.now()}.csv`
    link.click()
    
    URL.revokeObjectURL(url)
    ElMessage.success('CSV 文件导出成功')
  } catch (error) {
    console.error('Export failed:', error)
    ElMessage.error('导出失败，请重试')
  }
}
</script>

<style scoped>
.result-table {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
  overflow: hidden;
}

.table-header {
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
  gap: 12px;
}

.header-icon {
  font-size: 18px;
  color: #409eff;
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

.table-content {
  padding: 0;
}

.pagination {
  display: flex;
  justify-content: flex-end;
  padding: 16px 20px;
  background: #fafafa;
  border-top: 1px solid #ebeef5;
}
</style>
