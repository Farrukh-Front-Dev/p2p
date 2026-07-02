import { forwardRef, SelectHTMLAttributes, ReactNode } from 'react';

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  error?: string;
  children: ReactNode;
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(
  ({ label, error, className = '', children, ...props }, ref) => {
    return (
      <div className="flex flex-col gap-1.5 w-full">
        {label && (
          <label className="text-[10px] uppercase tracking-widest font-extrabold text-[#B0BEC5] font-montserrat">
            {label}
          </label>
        )}
        <select
          ref={ref}
          className={`h-11 w-full rounded-xl bg-[#34495E] border-2 px-4 text-sm font-ibm-plex-mono
                     text-white focus:outline-none cursor-pointer
                     focus:border-[#38C9E6] focus:ring-2 focus:ring-[#38C9E6]/20
                     transition-all duration-150 disabled:opacity-50 disabled:cursor-not-allowed
                     ${error ? 'border-[#FF9B9B] focus:border-[#FF9B9B]' : 'border-black focus:border-[#38C9E6]'}
                     ${className}`}
          {...props}
        >
          {children}
        </select>
        {error && <span className="text-xs text-[#FF9B9B] font-bold mt-0.5 font-ibm-plex-mono">{error}</span>}
      </div>
    );
  }
);

Select.displayName = 'Select';
export default Select;
