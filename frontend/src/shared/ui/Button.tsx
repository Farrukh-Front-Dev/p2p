import { ButtonHTMLAttributes, ReactNode } from 'react';

type Variant = 'primary' | 'secondary' | 'ghost' | 'danger';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  children: ReactNode;
}

const variants: Record<Variant, string> = {
  primary: 'bg-gradient-to-br from-[#38C9E6] to-[#43E8A0] text-black font-extrabold border-2 border-black shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] hover:-translate-x-[2px] hover:-translate-y-[2px] active:translate-x-[1px] active:translate-y-[1px] active:shadow-[1px_1px_0px_0px_rgba(0,0,0,1)]',
  secondary: 'bg-[#34495E] text-white border-2 border-black font-extrabold shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] hover:-translate-x-[2px] hover:-translate-y-[2px] active:translate-x-[1px] active:translate-y-[1px] active:shadow-[1px_1px_0px_0px_rgba(0,0,0,1)]',
  ghost: 'bg-transparent text-[#38C9E6] border-2 border-transparent hover:border-black font-bold active:scale-[0.98]',
  danger: 'bg-[#FF9B9B] hover:bg-[#FF8888] text-black font-extrabold border-2 border-black shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] hover:-translate-x-[2px] hover:-translate-y-[2px] active:translate-x-[1px] active:translate-y-[1px] active:shadow-[1px_1px_0px_0px_rgba(0,0,0,1)]',
};

export function Button({
  variant = 'primary',
  className = '',
  children,
  ...props
}: ButtonProps) {
  return (
    <button
      className={`h-11 px-6 rounded-xl text-xs uppercase tracking-wider font-montserrat inline-flex items-center justify-center gap-2
                  transition-all duration-150 disabled:opacity-40 disabled:cursor-not-allowed disabled:transform-none disabled:shadow-none
                  ${variants[variant]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}
export default Button;
