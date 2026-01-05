import request from '@/utils/request'

export interface TrendPoint {
  time: string
  value: number
}

export const getInvestmentTrend = (type: 'gold' | 'nasdaq') => {
  return request.get<TrendPoint[]>('/investment/trend', {
    params: { type }
  })
}
