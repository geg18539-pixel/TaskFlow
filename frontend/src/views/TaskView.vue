<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessageBox, type FormInstance, type FormRules } from 'element-plus'

import request from '@/api/request'

type TaskStatus = 'todo' | 'doing' | 'done'
type Priority = 'low' | 'medium' | 'high'

interface TaskItem {
  id: number
  title: string
  description: string | null
  status: TaskStatus
  priority: Priority
  due_date: string | null
  tags: string | null
  owner_id: number
  created_at: string
  updated_at: string
}

interface TaskPage {
  data: TaskItem[]
  total: number
}

const loading = ref(false)
const tasks = ref<TaskItem[]>([])
const total = ref(0)

const query = reactive({
  search: '',
  status: '' as TaskStatus | '',
  page: 1,
  pageSize: 10,
})

const dialogVisible = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')
const submitting = ref(false)
const editingId = ref<number | null>(null)
const formRef = ref<FormInstance>()

const form = reactive({
  title: '',
  description: '',
  status: 'todo' as TaskStatus,
  priority: 'medium' as Priority,
  due_date: null as string | null,
  tags: '',
})

const rules: FormRules = {
  title: [{ required: true, message: '请输入任务标题', trigger: 'blur' }],
  status: [{ required: true, message: '请选择任务状态', trigger: 'change' }],
  priority: [{ required: true, message: '请选择优先级', trigger: 'change' }],
}

const statusOptions: { label: string; value: TaskStatus }[] = [
  { label: '待办', value: 'todo' },
  { label: '进行中', value: 'doing' },
  { label: '已完成', value: 'done' },
]

const priorityOptions: { label: string; value: Priority }[] = [
  { label: '低', value: 'low' },
  { label: '中', value: 'medium' },
  { label: '高', value: 'high' },
]

const statusMeta: Record<TaskStatus, { label: string; type: 'info' | 'primary' | 'success' }> = {
  todo: { label: '待办', type: 'info' },
  doing: { label: '进行中', type: 'primary' },
  done: { label: '已完成', type: 'success' },
}

const priorityMeta: Record<Priority, { label: string; type: 'info' | 'warning' | 'danger' }> = {
  low: { label: '低', type: 'info' },
  medium: { label: '中', type: 'warning' },
  high: { label: '高', type: 'danger' },
}

function formatTime(value: string) {
  return value ? new Date(value).toLocaleString() : '-'
}

function formatDate(value: string | null) {
  return value || '-'
}

function splitTags(value: string | null) {
  if (!value) return []
  return value
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean)
}

async function fetchTasks() {
  loading.value = true
  try {
    const params: Record<string, unknown> = {
      skip: (query.page - 1) * query.pageSize,
      limit: query.pageSize,
    }
    if (query.search.trim()) params.search = query.search.trim()
    if (query.status) params.status = query.status

    const { data } = await request.get<TaskPage>('/tasks', { params })
    tasks.value = data.data
    total.value = data.total
  } catch {
    // surfaced by the axios response interceptor
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  query.page = 1
  fetchTasks()
}

function handleStatusChange() {
  query.page = 1
  fetchTasks()
}

function handleReset() {
  query.search = ''
  query.status = ''
  query.page = 1
  fetchTasks()
}

function handleSizeChange() {
  query.page = 1
  fetchTasks()
}

function resetForm() {
  form.title = ''
  form.description = ''
  form.status = 'todo'
  form.priority = 'medium'
  form.due_date = null
  form.tags = ''
  editingId.value = null
  formRef.value?.clearValidate()
}

function openCreate() {
  dialogMode.value = 'create'
  resetForm()
  dialogVisible.value = true
}

function openEdit(row: TaskItem) {
  dialogMode.value = 'edit'
  editingId.value = row.id
  form.title = row.title
  form.description = row.description ?? ''
  form.status = row.status
  form.priority = row.priority ?? 'medium'
  form.due_date = row.due_date ?? null
  form.tags = row.tags ?? ''
  dialogVisible.value = true
}

function buildPayload() {
  return {
    title: form.title,
    description: form.description.trim() || null,
    status: form.status,
    priority: form.priority,
    due_date: form.due_date || null,
    tags: form.tags.trim() || null,
  }
}

async function submitForm() {
  if (!formRef.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    if (dialogMode.value === 'create') {
      await request.post('/tasks', buildPayload())
      query.page = 1
    } else if (editingId.value !== null) {
      await request.put(`/tasks/${editingId.value}`, buildPayload())
    }
    dialogVisible.value = false
    await fetchTasks()
  } catch {
    // surfaced by the axios response interceptor
  } finally {
    submitting.value = false
  }
}

async function handleDelete(row: TaskItem) {
  try {
    await ElMessageBox.confirm(`确定删除任务「${row.title}」吗？`, '提示', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消',
    })
  } catch {
    return
  }

  try {
    await request.delete(`/tasks/${row.id}`)
    if (tasks.value.length === 1 && query.page > 1) {
      query.page -= 1
    }
    await fetchTasks()
  } catch {
    // surfaced by the axios response interceptor
  }
}

onMounted(fetchTasks)
</script>

<template>
  <div class="task-view">
    <div class="toolbar">
      <div class="toolbar-left">
        <el-input
          v-model="query.search"
          placeholder="搜索任务标题"
          clearable
          class="search-input"
          @keyup.enter="handleSearch"
          @clear="handleSearch"
        />
        <el-select
          v-model="query.status"
          placeholder="全部状态"
          clearable
          class="status-filter"
          @change="handleStatusChange"
        >
          <el-option
            v-for="item in statusOptions"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          />
        </el-select>
        <el-button type="primary" @click="handleSearch">搜索</el-button>
        <el-button @click="handleReset">重置</el-button>
      </div>
      <el-button type="primary" @click="openCreate">新建任务</el-button>
    </div>

    <el-table v-loading="loading" :data="tasks" border stripe>
      <el-table-column prop="title" label="标题" min-width="140" />
      <el-table-column label="描述" min-width="180">
        <template #default="{ row }">
          <span>{{ row.description || '-' }}</span>
        </template>
      </el-table-column>
      <el-table-column label="优先级" width="100">
        <template #default="{ row }">
          <el-tag :type="priorityMeta[row.priority as Priority].type">
            {{ priorityMeta[row.priority as Priority].label }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="110">
        <template #default="{ row }">
          <el-tag :type="statusMeta[row.status as TaskStatus].type">
            {{ statusMeta[row.status as TaskStatus].label }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="截止日期" width="120">
        <template #default="{ row }">
          {{ formatDate(row.due_date) }}
        </template>
      </el-table-column>
      <el-table-column label="标签" min-width="160">
        <template #default="{ row }">
          <el-tag v-for="tag in splitTags(row.tags)" :key="tag" size="small" class="tag-item">
            {{ tag }}
          </el-tag>
          <span v-if="splitTags(row.tags).length === 0">-</span>
        </template>
      </el-table-column>
      <el-table-column label="创建时间" width="180">
        <template #default="{ row }">
          {{ formatTime(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="140" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
          <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination-wrapper">
      <el-pagination
        v-model:current-page="query.page"
        v-model:page-size="query.pageSize"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next, jumper"
        @current-change="fetchTasks"
        @size-change="handleSizeChange"
      />
    </div>

    <el-dialog
      v-model="dialogVisible"
      :title="dialogMode === 'create' ? '新建任务' : '编辑任务'"
      width="520px"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入任务标题" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="请输入任务描述"
          />
        </el-form-item>
        <el-form-item label="优先级" prop="priority">
          <el-select v-model="form.priority" placeholder="请选择优先级" class="full-width">
            <el-option
              v-for="item in priorityOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="form.status" placeholder="请选择状态" class="full-width">
            <el-option
              v-for="item in statusOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="截止日期" prop="due_date">
          <el-date-picker
            v-model="form.due_date"
            type="date"
            value-format="YYYY-MM-DD"
            placeholder="请选择截止日期"
            class="full-width"
          />
        </el-form-item>
        <el-form-item label="标签" prop="tags">
          <el-input v-model="form.tags" placeholder="多个标签用英文逗号分隔，如：前端,紧急" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitForm">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.task-view {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 8px;
}

.toolbar-left {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.search-input {
  width: 220px;
}

.status-filter {
  width: 140px;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
}

.full-width {
  width: 100%;
}

.tag-item {
  margin-right: 4px;
}
</style>
