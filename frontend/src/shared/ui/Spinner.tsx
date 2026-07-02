import { useState, useEffect } from 'react';

interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  fullScreen?: boolean;
}

const SCHOOL21_MESSAGES = [
  "Peer-to-peer tarmog'i yuklanmoqda...",
  "Verter tekshiruv tizimi faollashtirilmoqda...",
  "Faol slotlar va peerlar tekshirilmoqda...",
  "Sizning peer ballaringiz sinxronizatsiya qilinmoqda...",
  "School 21 loyihalar ro'yxati yangilanmoqda...",
  "Reyting jadvali tuzilmoqda...",
];

export function Spinner({ size = 'md', fullScreen = false }: SpinnerProps) {
  const [messageIndex, setMessageIndex] = useState(0);

  useEffect(() => {
    if (!fullScreen) return;
    const interval = setInterval(() => {
      setMessageIndex((prev) => (prev + 1) % SCHOOL21_MESSAGES.length);
    }, 1800);
    return () => clearInterval(interval);
  }, [fullScreen]);

  const sizeClasses = {
    sm: 'w-10 h-10',
    md: 'w-16 h-16',
    lg: 'w-24 h-24',
  };

  const textSizes = {
    sm: 'text-[10px]',
    md: 'text-sm',
    lg: 'text-lg',
  };

  const spinnerEl = (
    <div className={`relative ${sizeClasses[size]} flex items-center justify-center`} role="status" aria-label="Yuklanmoqda...">
      {/* Outer Glow Ring running clockwise */}
      <div
        className="absolute inset-0 rounded-full border-[3px] border-transparent animate-spin"
        style={{
          borderTopColor: '#38C9E6',
          borderRightColor: '#38C9E6',
          animationDuration: '1.2s',
          filter: 'drop-shadow(0 0 4px rgba(56,201,230,0.5))'
        }}
      />
      {/* Inner Ring running counter-clockwise */}
      <div
        className="absolute inset-1.5 rounded-full border-[3px] border-transparent animate-spin"
        style={{
          borderBottomColor: '#43E8A0',
          borderLeftColor: '#43E8A0',
          animationDuration: '0.8s',
          animationDirection: 'reverse',
          filter: 'drop-shadow(0 0 4px rgba(67,232,160,0.5))'
        }}
      />
      {/* Static tech core */}
      <div className="absolute inset-3 rounded-full bg-[#1E2A38] border-2 border-black flex items-center justify-center z-10 font-bold shadow-inner">
        <span className={`${textSizes[size]} font-extrabold text-[#38C9E6] tracking-tighter transition-all hover:scale-110 cursor-default animate-pulse`}>
          21
        </span>
      </div>
    </div>
  );

  if (fullScreen) {
    return (
      <div className="fixed inset-0 z-50 bg-[#1E2A38] bg-opacity-95 backdrop-blur-md flex items-center justify-center flex-col gap-6">
        {/* Subtle grid pattern background */}
        <div className="absolute inset-0 bg-grid-white/[0.02] pointer-events-none" />
        
        <div className="relative">
          {/* Outer futuristic ring frame */}
          <div className="absolute -inset-4 bg-gradient-to-tr from-[#38C9E6]/10 to-[#43E8A0]/10 rounded-full blur-xl animate-pulse" />
          {spinnerEl}
        </div>

        <div className="flex flex-col items-center gap-2 max-w-xs text-center px-4 relative z-10">
          <span className="text-[10px] sm:text-[11px] font-black tracking-[0.2em] text-[#38C9E6] uppercase font-ibm-plex-mono border-b border-black/30 pb-1.5 w-full">
            SCHOOL 21 P2P NETWORK
          </span>
          <p className="text-[11px] font-medium text-gray-400 font-ibm-plex-mono h-8 flex items-center justify-center transition-all duration-300">
            {SCHOOL21_MESSAGES[messageIndex]}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex justify-center items-center py-8">
      {spinnerEl}
    </div>
  );
}

export default Spinner;

