import request from '@/utils/request'

export interface WorkSettings {
  id: number
  user_id: number
  start_time: string
  end_time: string
}

export interface WorkSettingsUpdate {
  start_time: string
  end_time: string
}

export interface WorkItem {
  id: number
  user_id: number
  type: 'memo' | 'plan' | 'progress'
  content: string
  status: 'pending' | 'done'
  percentage: number
  created_at: string
}

export interface WorkItemCreate {
  type: 'memo' | 'plan' | 'progress'
  content: string
  status?: 'pending' | 'done'
  percentage?: number
}

export interface WorkItemUpdate {
  content?: string
  status?: 'pending' | 'done'
  percentage?: number
}

// Settings
export const getWorkSettings = () => {
  return request.get<WorkSettings>('/work/settings')
}

export const updateWorkSettings = (data: WorkSettingsUpdate) => {
  return request.put<WorkSettings>('/work/settings', data)
}

// Items
export const getWorkItems = (type?: string) => {
  return request.get<WorkItem[]>('/work/items', { params: { type } })
}

export const createWorkItem = (data: WorkItemCreate) => {
  return request.post<WorkItem>('/work/items', data)
}

export const updateWorkItem = (id: number, data: WorkItemUpdate) => {
  return request.put<WorkItem>(`/work/items/${id}`, data)
}

export const deleteWorkItem = (id: number) => {
  return request.delete<WorkItem>(`/work/items/${id}`)
}

export interface WorkRecord {
  id: number
  user_id: number
  clock_in_time: string
  clock_out_time?: string
  date: string
}

export const clockOut = () => {
  return request.post<WorkRecord>('/work/clock-out')
}

export const getWorkRecords = () => {
  return request.get<WorkRecord[]>('/work/records')
}

export const getTodayWorkRecord = () => {
  return request.get<WorkRecord>('/work/records/today')
}
