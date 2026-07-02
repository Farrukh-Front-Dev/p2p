import { SlotStatus } from '@/shared/types/api';
import { Check, AlertTriangle } from 'lucide-react';

interface SlotTimelineProps {
  status: SlotStatus;
  actualStart?: string | null;
  actualEnd?: string | null;
}

export function SlotTimeline({ status, actualStart, actualEnd }: SlotTimelineProps) {
  const steps = [
    { key: 'created', label: 'Slot Yaratildi', desc: 'Siz sheriklar uchun vaqt darchasini ruxsat etdingiz.' },
    { key: 'booked', label: 'Band Qilindi', desc: 'Dars baholovchi talaba tomonidan band qilindi.' },
    { key: 'in_progress', label: 'Dars Boshlandi', desc: 'Ikkala tomon ham darsni "Boshlash" ni bosishdi.' },
    { key: 'completed', label: 'Tugallandi', desc: 'Peer-to-peer baholash va loyiha muhokamasi yakunlandi.' },
  ];

  const getStepIndex = () => {
    switch (status) {
      case 'open':
        return 0;
      case 'booked':
        return 1;
      case 'in_progress':
        return 2;
      case 'completed':
        return 3;
      case 'cancelled':
      case 'absent':
        return -1;
    }
  };

  const activeIndex = getStepIndex();

  return (
    <div className="flex flex-col gap-4 sm:gap-5 p-4 sm:p-5 bg-[#2A3442] border-2 border-black rounded-3xl shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] font-ibm-plex-mono">
      <h3 className="text-xs uppercase font-montserrat font-black tracking-widest text-[#B0BEC5] mb-1 sm:mb-2">
        Baholash Bosqichlari Timeline
      </h3>

      {status === 'cancelled' && (
        <div className="p-3 sm:p-4 rounded-2xl bg-[#4A2D2D] border-2 border-black flex items-start gap-3 mb-2 animate-fade-in shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]">
          <AlertTriangle className="h-5 w-5 text-[#FF9B9B] flex-shrink-0 mt-0.5" />
          <div className="flex flex-col gap-0.5">
            <span className="text-sm font-black text-[#FF9B9B] font-montserrat">Loyiha Bekor Qilindi</span>
            <span className="text-xs text-[#B0BEC5] leading-relaxed">Ushbu slot yaratuvchi tomonidan yoki administrator tomonidan bekor qilindi.</span>
          </div>
        </div>
      )}

      {status === 'absent' && (
        <div className="p-3 sm:p-4 rounded-2xl bg-[#4A2D2D] border-2 border-black flex items-start gap-3 mb-2 animate-fade-in shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]">
          <AlertTriangle className="h-5 w-5 text-[#FF9B9B] flex-shrink-0 mt-0.5" />
          <div className="flex flex-col gap-0.5">
            <span className="text-sm font-black text-[#FF9B9B] font-montserrat">Dars Kelmadi deb Belgilandi</span>
            <span className="text-xs text-[#B0BEC5] leading-relaxed">Baholash vaqtida kelmagan a'zo qayd etildi. Tegishli XP jarimalari yuklandi.</span>
          </div>
        </div>
      )}

      <div className="relative border-l-2 border-black ml-3 pl-5 sm:pl-6 space-y-5 sm:space-y-6">
        {steps.map((step, idx) => {
          const isDone = activeIndex >= idx;
          const isCurrent = activeIndex === idx;

          return (
            <div key={step.key} className="relative group">
              <div
                className={`absolute -left-[29px] sm:-left-[33px] top-1.5 h-5 w-5 rounded-lg border-2 border-black flex items-center justify-center transition-all duration-300 shadow-[1px_1px_0px_0px_rgba(0,0,0,1)]
                  ${isDone ? 'bg-gradient-to-br from-[#38C9E6] to-[#43E8A0]' : 'bg-[#34495E]'}`}
              >
                {isDone && <Check className="h-3 w-3 text-black stroke-[3]" />}
              </div>

              <div className="flex flex-col gap-0.5">
                <span
                  className={`text-sm font-black font-montserrat transition-colors duration-150
                    ${isCurrent ? 'text-[#43E8A0]' : isDone ? 'text-white' : 'text-[#B0BEC5]'}`}
                >
                  {step.label}
                </span>
                <span className="text-xs text-[#B0BEC5] leading-relaxed">{step.desc}</span>

                {step.key === 'in_progress' && actualStart && (
                  <span className="text-[10px] font-ibm-plex-mono text-[#38C9E6] mt-1">
                    Boshlanish vaqti: {new Date(actualStart).toLocaleTimeString('uz-UZ')}
                  </span>
                )}
                {step.key === 'completed' && actualEnd && (
                  <span className="text-[10px] font-ibm-plex-mono text-[#cdbdff] mt-1">
                    Yakunlanish vaqti: {new Date(actualEnd).toLocaleTimeString('uz-UZ')}
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
export default SlotTimeline;
