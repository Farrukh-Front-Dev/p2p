import { useToastStore } from '@/shared/stores/toast';
import { X, CheckCircle, AlertOctagon, Info } from 'lucide-react';

export function ToastContainer() {
  const { toasts, removeToast } = useToastStore();

  if (toasts.length === 0) return null;

  return (
    <div className="fixed top-4 right-4 z-50 flex flex-col gap-2 max-w-sm w-full pointer-events-none">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className={`pointer-events-auto p-4 rounded-2xl flex items-start gap-4 border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] transition-all duration-300 animate-slide-in font-ibm-plex-mono
            ${
              toast.type === 'success'
                ? 'bg-[#2A3442] text-[#43E8A0]'
                : toast.type === 'error'
                ? 'bg-[#2A3442] text-[#FF9B9B]'
                : 'bg-[#2A3442] text-[#38C9E6]'
            }
          `}
        >
          <div className="flex-shrink-0 mt-0.5">
            {toast.type === 'success' && <CheckCircle className="h-5 w-5" />}
            {toast.type === 'error' && <AlertOctagon className="h-5 w-5" />}
            {toast.type === 'info' && <Info className="h-5 w-5" />}
          </div>
          <div className="flex-grow">
            <p className="text-sm font-bold text-white">{toast.text}</p>
          </div>
          <button
            onClick={() => removeToast(toast.id)}
            className="flex-shrink-0 text-[#B0BEC5] hover:text-white transition-colors cursor-pointer"
            aria-label="Yopish"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      ))}
    </div>
  );
}
