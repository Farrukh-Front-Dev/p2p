import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { slotService } from '@/services/slots'
import type { SlotCreate } from '@/types/api'

export function useSlots(params?: { status?: string; date?: string }) {
  return useQuery({
    queryKey: ['slots', params],
    queryFn: () => slotService.list(params),
  })
}

export function useSlot(id: string) {
  return useQuery({
    queryKey: ['slots', id],
    queryFn: () => slotService.get(id),
    enabled: !!id,
  })
}

export function useSlotSearch(project: string) {
  return useQuery({
    queryKey: ['slots', 'search', project],
    queryFn: () => slotService.search(project),
    enabled: !!project,
  })
}

export function useTeachableProjects() {
  return useQuery({
    queryKey: ['projects', 'teachable'],
    queryFn: slotService.teachableProjects,
    staleTime: 5 * 60_000,
  })
}

export function useInProgressProjects() {
  return useQuery({
    queryKey: ['projects', 'in-progress'],
    queryFn: slotService.inProgressProjects,
    staleTime: 5 * 60_000,
  })
}

export function useCreateSlot() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: SlotCreate) => slotService.create(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['slots'] })
      qc.invalidateQueries({ queryKey: ['dashboard'] })
    },
  })
}

export function useBookSlot() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({
      id,
      revieweeProject,
    }: {
      id: string
      revieweeProject?: string
    }) => slotService.book(id, revieweeProject),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['slots'] })
      qc.invalidateQueries({ queryKey: ['dashboard'] })
    },
  })
}

export function useCancelSlot() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, reason }: { id: string; reason?: string }) =>
      slotService.cancel(id, reason),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['slots'] })
      qc.invalidateQueries({ queryKey: ['dashboard'] })
    },
  })
}

export function useStartSlot() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => slotService.start(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['slots'] })
    },
  })
}

export function useFinishSlot() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => slotService.finish(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['slots'] })
      qc.invalidateQueries({ queryKey: ['dashboard'] })
    },
  })
}
