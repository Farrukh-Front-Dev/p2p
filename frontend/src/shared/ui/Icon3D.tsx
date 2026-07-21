import { ReactNode } from 'react';

type GradientType = 'cyan-blue' | 'pink-red' | 'purple-indigo' | 'green-emerald';
type SizeType = 'sm' | 'md' | 'lg';

interface Icon3DProps {
  children: ReactNode;
  gradient?: GradientType;
  size?: SizeType;
  className?: string;
}

const gradients: Record<GradientType, string> = {
  'cyan-blue': 'from-cyan-400 to-blue-500',
  'pink-red': 'from-pink-400 to-red-500',
  'purple-indigo': 'from-purple-400 to-indigo-500',
  'green-emerald': 'from-green-400 to-emerald-500',
};

const sizes: Record<SizeType, string> = {
  sm: 'w-10 h-10',
  md: 'w-12 h-12',
  lg: 'w-14 h-14',
};

export function Icon3D({
  children,
  gradient = 'cyan-blue',
  size = 'md',
  className = '',
}: Icon3DProps) {
  return (
    <div
      className={`
        ${sizes[size]}
        rounded-2xl
        bg-gradient-to-br ${gradients[gradient]}
        flex items-center justify-center
        border-2 border-black
        shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]
        ${className}
      `}
    >
      {children}
    </div>
  );
}

export default Icon3D;
