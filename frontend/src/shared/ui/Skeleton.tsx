interface SkeletonProps {
  className?: string;
  variant?: 'rect' | 'circle' | 'text';
}

export function Skeleton({ className = '', variant = 'rect' }: SkeletonProps) {
  return (
    <div
      className={`animate-pulse bg-[#34495E] border-2 border-black/25
        ${variant === 'circle' ? 'rounded-full' : variant === 'text' ? 'h-4 rounded-lg' : 'rounded-3xl shadow-[2px_2px_0px_0px_rgba(0,0,0,0.1)]'}
        ${className}`}
      aria-hidden="true"
    />
  );
}
export default Skeleton;
