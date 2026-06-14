import { useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { ThumbsUp, ThumbsDown, Send } from 'lucide-react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Button, Card, Input } from '@/components/ui'
import { reviewService } from '@/services/reviews'
import { toast } from '@/components/ui/Toast'

export function ReviewPage() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const qc = useQueryClient()
  const slotId = searchParams.get('slot') || ''

  const [isPositive, setIsPositive] = useState<boolean | null>(null)
  const [comment, setComment] = useState('')

  const createReview = useMutation({
    mutationFn: () =>
      reviewService.create({
        slot_id: slotId,
        is_positive: isPositive!,
        comment: comment || undefined,
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['slots'] })
      toast.success("Sharh yuborildi! Rahmat.")
      navigate('/slots')
    },
    onError: () => {
      toast.error("Sharh yuborishda xatolik yuz berdi")
    },
  })

  if (!slotId) {
    return (
      <div className="text-center py-12 text-gray-500">
        Slot topilmadi. Slotlar sahifasidan qaytadan urinib ko'ring.
      </div>
    )
  }

  return (
    <div className="max-w-md mx-auto space-y-5">
      <h1 className="text-xl font-bold text-gray-900 dark:text-gray-100 text-center">
        Sharh qoldirish
      </h1>
      <p className="text-sm text-gray-500 text-center">
        Bu session qanday o'tdi?
      </p>

      {/* Rating */}
      <Card padding="lg" className="text-center">
        <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-4">
          Baholang
        </p>
        <div className="flex justify-center gap-4">
          <button
            onClick={() => setIsPositive(true)}
            className={`flex flex-col items-center gap-2 rounded-xl p-6 border-2 transition-all ${
              isPositive === true
                ? 'border-emerald-500 bg-emerald-50 dark:bg-emerald-900/20'
                : 'border-border hover:border-emerald-300'
            }`}
            aria-label="Ijobiy"
          >
            <ThumbsUp className={`h-8 w-8 ${isPositive === true ? 'text-emerald-500' : 'text-gray-400'}`} />
            <span className="text-sm font-medium">Yaxshi</span>
          </button>

          <button
            onClick={() => setIsPositive(false)}
            className={`flex flex-col items-center gap-2 rounded-xl p-6 border-2 transition-all ${
              isPositive === false
                ? 'border-red-500 bg-red-50 dark:bg-red-900/20'
                : 'border-border hover:border-red-300'
            }`}
            aria-label="Salbiy"
          >
            <ThumbsDown className={`h-8 w-8 ${isPositive === false ? 'text-red-500' : 'text-gray-400'}`} />
            <span className="text-sm font-medium">Yomon</span>
          </button>
        </div>
      </Card>

      {/* Comment */}
      <Card>
        <label className="text-sm font-medium text-gray-700 dark:text-gray-300 block mb-2">
          Izoh (ixtiyoriy)
        </label>
        <textarea
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          placeholder="Nimalar yaxshi bo'ldi? Nimani yaxshilash mumkin?"
          className="w-full h-24 rounded-lg border border-border bg-surface px-3 py-2 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500"
          maxLength={500}
        />
        <p className="text-xs text-gray-400 mt-1 text-right">{comment.length}/500</p>
      </Card>

      {/* Submit */}
      <Button
        onClick={() => createReview.mutate()}
        className="w-full"
        disabled={isPositive === null}
        loading={createReview.isPending}
        icon={<Send className="h-4 w-4" />}
      >
        Yuborish
      </Button>
    </div>
  )
}
