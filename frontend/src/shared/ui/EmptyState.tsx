import { ReactNode } from 'react';
import { CalendarClock } from 'lucide-react';

interface EmptyStateProps {
  title: string;
  description: string;
  icon?: ReactNode;
  children?: ReactNode;
}

export function EmptyState({
  title,
  description,
  icon,
  children,
}: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-12 px-6 text-center bg-[#2A3442] border-2 border-black rounded-3xl shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
      <div className="h-16 w-16 rounded-2xl bg-gradient-to-br from-[#38C9E6] to-[#43E8A0] border-2 border-black flex items-center justify-center mb-5 text-black shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]">
        {icon || <CalendarClock className="h-7 w-7" />}
      </div>
      <h3 className="text-lg font-extrabold text-white font-montserrat">{title}</h3>
      <p className="text-xs text-[#B0BEC5] mt-2 max-w-sm font-ibm-plex-mono leading-relaxed">{description}</p>
      {children && <div className="mt-6">{children}</div>}
    </div>
  );
}
export default EmptyState;
