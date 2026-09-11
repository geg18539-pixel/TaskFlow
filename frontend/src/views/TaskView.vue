<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'

import request from '@/api/request'

type TaskStatus = 'todo' | 'doing' | 'done'

interface TaskItem {
  id: number
  title: string
  description: string | null
  status: TaskStatus
  owner_id: number
  created_at: string
  updated_at: string
}

const loading = ref(false)
const tasks = ref<TaskItem[]>([])

const dialogVisible = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')
const submitting = ref(false)
const editingId = ref<number | null>(null)
const formRef = ref<FormInstance>()

const form = reactive({
  title: '',
  description: '',
  status: 'todo' as TaskStatus,
})

const rules: FormRules = {
  title: [{ required: true, message: '请输入任务标题', trigger: 'blur' }],
  status: [{ required: true, message: '请选择任务状态', trigger: 'change' }],
}

const statusOptions: { label: string; value: TaskStatus }[] = [
  { label: '待办', value: 'todo' },
  { label: '进行中', value: 'doing' },
  { label: '已完成', value: 'done' },
]

const statusMeta: Record<TaskStatus, { label: string; type: 'info' | 'primary' | 'success' }> = {
  todo: { label: '待办', type: 'info' },
  doing: { label: '进行中', type: 'primary' },
  done: { label: '已完成', type: 'success' },
}

function formatTime(value: string) {
  return value ? new Date(value).toLocaleString() : '-'
}

async function fetchTasks() {
  loading.value = true
  try {
    const { data } = await request.get<TaskItem[]>('/tasks')
    tasks.value = data
  } catch (error) {
    ElMessage.error('获取任务列表失败')
  } finally {
    loading.value = false
  }
}

function resetForm() {
  form.title = ''
  form.description = ''
  form.status = 'todo'
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
  dialogVisible.value = true
}

async function submitForm() {
  if (!formRef.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    if (dialogMode.value === 'create') {
      await request.post('/tasks', { ...form })
      ElMessage.success('创建成功')
    } else if (editingId.value !== null) {
      await request.put(`/tasks/${editingId.value}`, { ...form })
      ElMessage.success('更新成功')
    }
    dialogVisible.value = false
    await fetchTasks()
  } catch (error) {
    ElMessage.error('保存失败')
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
    ElMessage.success('删除成功')
    await fetchTasks()
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

onMounted(fetchTasks)
</script>

<template>
  <div class="task-view">
    <div class="toolbar">
      <h2 class="page-title">任务管理</h2>
      <el-button type="primary" @click="openCreate">新建任务</el-button>
    </div>

    <el-table v-loading="loading" :data="tasks" border stripe>
      <el-table-column prop="title" label="标题" min-width="160" />
      <el-table-column label="描述" min-width="220">
        <template #default="{ row }">
          <span>{{ row.description || '-' }}</span>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="120">
        <template #default="{ row }">
          <el-tag :type="statusMeta[row.status as TaskStatus].type">
            {{ statusMeta[row.status as TaskStatus].label }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="创建时间" width="180">
        <template #default="{ row }">
          {{ formatTime(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="160" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
          <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog
      v-model="dialogVisible"
      :title="dialogMode === 'create' ? '新建任务' : '编辑任务'"
      width="500px"
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
        <el-form-item label="状态" prop="status">
          <el-select v-model="form.status" placeholder="请选择状态" class="status-select">
            <el-option
              v-for="item in statusOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
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
}

.page-title {
  margin: 0;
  font-size: 20px;
  color: #303133;
}

.status-select {
  width: 100%;
}
</style>
