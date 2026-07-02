interface BadgeProps {
  children: string;
  type?: 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'info' | 'gold';
  className?: string;
}

const styles = {
  primary: 'bg-gradient-to-br from-[#38C9E6] to-[#43E8A0] text-black border-black',
  secondary: 'bg-[#cdbdff] text-black border-black',
  success: 'bg-[#00e676] text-black border-black',
  warning: 'bg-[#ffd740] text-black border-black',
  error: 'bg-[#FF9B9B] text-black border-black',
  info: 'bg-[#40c4ff] text-black border-black',
  gold: 'bg-[#ffd740] text-black border-black',
};

export function Badge({ children, type = 'primary', className = '' }: BadgeProps) {
  return (
    <span
      className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-lg text-[10px] whitespace-nowrap font-extrabold uppercase tracking-widest border-2 shadow-[1px_1px_0px_0px_rgba(0,0,0,1)] font-montserrat
                  ${styles[type]} ${className}`}
    >
      {children}
    </span>
  );
}
export default Badge;
