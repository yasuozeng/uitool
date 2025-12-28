<!--
用例管理页面
提供用例列表展示、搜索筛选、CRUD 操作、批量删除等功能
-->
<template>
  <div class="case-management">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1>用例管理</h1>
      <el-button type="primary" @click="handleCreate">
        <el-icon><Plus /></el-icon>
        新建用例
      </el-button>
    </div>

    <!-- 搜索筛选栏 -->
    <div class="filter-bar">
      <el-input
        v-model="searchName"
        placeholder="搜索用例名称"
        clearable
        style="width: 200px"
        @clear="handleSearch"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>

      <el-select
        v-model="filterPriority"
        placeholder="优先级"
        clearable
        style="width: 150px"
        @change="handleSearch"
      >
        <el-option
          v-for="p in priorities"
          :key="p.value"
          :label="p.label"
          :value="p.value"
        />
      </el-select>

      <el-input
        v-model="filterTags"
        placeholder="标签搜索"
        clearable
        style="width: 150px"
        @clear="handleSearch"
      />

      <el-button type="primary" @click="handleSearch">
        <el-icon><Search /></el-icon>
        搜索
      </el-button>

      <el-button @click="handleReset">
        <el-icon><RefreshLeft /></el-icon>
        重置
      </el-button>
    </div>

    <!-- 批量操作栏 -->
    <div v-if="selectedCases.length > 0" class="batch-bar">
      <span class="selection-info">已选择 {{ selectedCases.length }} 项</span>
      <el-button type="danger" @click="handleBatchDelete">
        <el-icon><Delete /></el-icon>
        批量删除
      </el-button>
      <el-button @click="clearSelection">取消选择</el-button>
    </div>

    <!-- 统计信息 -->
    <div class="stats-bar">
      <el-tag v-for="(count, priority) in priorityStats" :key="priority" :type="getPriorityType(priority)">
        {{ priority }}: {{ count }}
      </el-tag>
      <el-tag type="info">总计: {{ pagination.total }}</el-tag>
    </div>

    <!-- 用例表格 -->
    <el-table
      v-loading="loading"
      :data="cases"
      stripe
      @selection-change="handleSelectionChange"
      class="case-table"
    >
      <el-table-column type="selection" width="50" />
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="name" label="用例名称" min-width="200" show-overflow-tooltip />
      <el-table-column prop="priority" label="优先级" width="100">
        <template #default="{ row }">
          <el-tag :type="getPriorityType(row.priority)" size="small">
            {{ row.priority }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="tags" label="标签" width="150" show-overflow-tooltip />
      <el-table-column prop="step_count" label="步骤数" width="80" align="center" />
      <el-table-column prop="created_at" label="创建时间" width="180">
        <template #default="{ row }">
          {{ formatDate(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="220" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" size="small" link @click="handleEdit(row.id)">
            <el-icon><Edit /></el-icon>
            编辑
          </el-button>
          <el-button type="success" size="small" link @click="handleQuickExecute(row.id)">
            <el-icon><VideoPlay /></el-icon>
            执行
          </el-button>
          <el-button type="danger" size="small" link @click="handleDelete(row.id)">
            <el-icon><Delete /></el-icon>
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.page_size"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @current-change="handlePageChange"
        @size-change="handleSizeChange"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useCaseStore } from '@/store/modules/case'
import { getCases, deleteCase, batchDeleteCases, getPriorities } from '@/api/case'

const router = useRouter()
const caseStore = useCaseStore()

// ========== 响应式数据 ==========
const searchName = ref('')
const filterPriority = ref('')
const filterTags = ref('')
const selectedCases = ref<number[]>([])

// ========== 计算属性 ==========
const cases = computed(() => caseStore.cases)
const pagination = computed(() => caseStore.pagination)
const loading = computed(() => caseStore.loading)
const priorityStats = computed(() => caseStore.priorityStats)

// 获取优先级选项
const priorities = getPriorities()

// ========== 方法 ==========

// 获取优先级对应的标签类型
const getPriorityType = (priority: string) => {
  const p = priorities.find(item => item.value === priority)
  return p?.type || ''
}

// 格式化日期
const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

// 加载用例列表
const loadCases = async () => {
  caseStore.setLoading(true)
  try {
    const response = await getCases({
      name: searchName.value || undefined,
      priority: filterPriority.value || undefined,
      tags: filterTags.value || undefined,
      page: pagination.value.page,
      page_size: pagination.value.page_size
    })
    caseStore.setCases(response.data)
    caseStore.setPagination({
      total: response.total,
      pages: response.pages
    })
  } catch (error) {
    ElMessage.error('加载用例列表失败')
  } finally {
    caseStore.setLoading(false)
  }
}

// 搜索
const handleSearch = () => {
  pagination.value.page = 1
  loadCases()
}

// 重置筛选
const handleReset = () => {
  searchName.value = ''
  filterPriority.value = ''
  filterTags.value = ''
  caseStore.resetFilters()
  loadCases()
}

// 翻页
const handlePageChange = () => {
  loadCases()
}

// 每页数量变化
const handleSizeChange = () => {
  pagination.value.page = 1
  loadCases()
}

// 选择变化
const handleSelectionChange = (selection: any[]) => {
  selectedCases.value = selection.map(item => item.id)
}

// 清除选择
const clearSelection = () => {
  selectedCases.value = []
}

// 新建用例
const handleCreate = () => {
  router.push('/editor')
}

// 编辑用例
const handleEdit = (id: number) => {
  router.push(`/editor/${id}`)
}

// 快速执行（跳转到执行控制台并预选该用例）
const handleQuickExecute = (id: number) => {
  router.push({ path: '/execution', query: { case_ids: String(id) } })
}

// 删除用例
const handleDelete = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定要删除这个用例吗？', '确认删除', {
      type: 'warning'
    })
    await deleteCase(id)
    caseStore.removeCase(id)
    ElMessage.success('删除成功')
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 批量删除
const handleBatchDelete = async () => {
  if (selectedCases.value.length === 0) {
    ElMessage.warning('请先选择要删除的用例')
    return
  }
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedCases.value.length} 个用例吗？`,
      '确认批量删除',
      { type: 'warning' }
    )
    await batchDeleteCases(selectedCases.value)
    caseStore.batchRemoveCases(selectedCases.value)
    selectedCases.value = []
    ElMessage.success('批量删除成功')
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('批量删除失败')
    }
  }
}

// ========== 生命周期 ==========
onMounted(() => {
  loadCases()
})
</script>

<style scoped lang="scss">
.case-management {
  padding: 24px; // 从 20px 增加到 24px
  background: #f0f2f5; // 更新为新的背景色
  min-height: 100vh;

  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding: 18px 22px; // 增加内边距
    background: white;
    border-radius: 8px; // 从 4px 增加到 8px
    box-shadow: 0 1px 6px rgba(0, 0, 0, 0.04); // 添加阴影
    border: 1px solid #f0f0f0; // 添加边框

    h1 {
      margin: 0;
      font-size: 22px; // 从 24px 调整为 22px
      font-weight: 600; // 从 500 增加到 600
      color: #262626; // 更新为新的文本色
    }
  }

  .filter-bar {
    display: flex;
    gap: 16px; // 从 12px 增加到 16px
    margin-bottom: 20px; // 从 16px 增加到 20px
    padding: 18px 22px; // 增加内边距
    background: white;
    border-radius: 8px; // 从 4px 增加到 8px
    border: 1px solid #f0f0f0; // 添加边框
    box-shadow: 0 1px 6px rgba(0, 0, 0, 0.04); // 添加阴影
    transition: box-shadow 0.2s; // 添加过渡效果

    &:hover {
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06); // 悬停时增强阴影
    }
  }

  .batch-bar {
    display: flex;
    align-items: center;
    gap: 16px; // 从 12px 增加到 16px
    margin-bottom: 20px; // 从 16px 增加到 20px
    padding: 14px 18px; // 增加内边距
    background: #e6f4ff; // 更新为新的浅蓝背景色
    border: 1px solid #91caff; // 更新边框色
    border-radius: 8px; // 从 4px 增加到 8px
    box-shadow: 0 1px 6px rgba(22, 119, 255, 0.08); // 添加蓝色阴影

    .selection-info {
      font-weight: 600; // 从 500 增加到 600
      color: #1677ff; // 更新为新的主色
    }
  }

  .stats-bar {
    display: flex;
    gap: 16px; // 从 12px 增加到 16px
    margin-bottom: 20px; // 从 16px 增加到 20px
    padding: 14px 18px; // 增加内边距
    background: white;
    border-radius: 8px; // 从 4px 增加到 8px
    border: 1px solid #f0f0f0; // 添加边框
    box-shadow: 0 1px 6px rgba(0, 0, 0, 0.04); // 添加阴影
  }

  .case-table {
    background: white;
    border-radius: 8px; // 从 4px 增加到 8px
    border: 1px solid #f0f0f0; // 添加边框
    overflow: hidden; // 确保圆角生效
    box-shadow: 0 1px 6px rgba(0, 0, 0, 0.04); // 添加阴影
  }

  .pagination {
    display: flex;
    justify-content: center;
    margin-top: 24px; // 从 20px 增加到 24px
    padding: 18px 22px; // 增加内边距
    background: white;
    border-radius: 8px; // 从 4px 增加到 8px
    border: 1px solid #f0f0f0; // 添加边框
    box-shadow: 0 1px 6px rgba(0, 0, 0, 0.04); // 添加阴影
  }
}
</style>
