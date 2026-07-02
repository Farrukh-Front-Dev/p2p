import { useState } from 'react';

interface AvatarProps {
  src?: string | null;
  name?: string | null;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
}

const sizeClasses = {
  sm: 'h-8 w-8 text-xs',
  md: 'h-11 w-11 text-sm',
  lg: 'h-14 w-14 text-base font-bold',
  xl: 'h-20 w-20 text-xl font-bold',
};

export function Avatar({ src, name, size = 'md', className = '' }: AvatarProps) {
  const [hasError, setHasError] = useState(false);
  const initials = name
    ? name.trim().split(/\s+/).slice(0, 2).map((p) => p[0]?.toUpperCase()).join('')
    : 'U';

  const sizeClass = sizeClasses[size];

  return (
    <div className={`flex-shrink-0 rounded-full p-0.5 bg-gradient-to-br from-[#38C9E6] to-[#43E8A0] border-2 border-black ${className}`}>
      <div className={`relative rounded-full overflow-hidden bg-[#34495E] flex items-center justify-center text-[#38C9E6] font-montserrat ${sizeClass}`}>
        {src && !hasError ? (
          <img
            src={src}
            alt={name || 'Avatar'}
            onError={() => setHasError(true)}
            className="h-full w-full object-cover"
            referrerPolicy="no-referrer"
          />
        ) : (
          <span className="font-semibold select-none leading-none">{initials}</span>
        )}
      </div>
    </div>
  );
}
export default Avatar;
