import { ReactNode } from 'react';
import { LucideIcon } from 'lucide-react';

interface PageHeaderProps {
  /** Sahifa sarlavhasi (Montserrat, black) */
  title: string;
  /** Sarlavha ostidagi qisqa izoh */
  subtitle?: string;
  /** Chapdagi ikonka (lucide-react) */
  icon?: LucideIcon;
  /** Ikonka rangi (Tailwind class), default teal */
  iconClassName?: string;
  /** O'ng tomondagi harakat tugmalari (masalan "Yaratish") */
  actions?: ReactNode;
}

/**
 * Barcha sahifalar uchun YAGONA sarlavha bloki.
 * DESIGN_SPEC: har bir sahifa root `flex flex-col gap-6 animate-fade-in`
 * ichida birinchi element sifatida `<PageHeader />` ishlatishi kerak.
 */
export function PageHeader({
  title,
  subtitle,
  icon: Icon,
  iconClassName = 'text-[#38C9E6]',
  actions,
}: PageHeaderProps) {
  return (
    <div className="flex items-start justify-between gap-4">
      <div className="flex flex-col gap-1.5">
        <h1 className="text-xl sm:text-2xl font-black text-white flex items-center gap-2 font-montserrat tracking-tight leading-none">
          {Icon && <Icon className={`h-6 w-6 ${iconClassName}`} />}
          {title}
        </h1>
        {subtitle && (
          <p className="text-xs text-[#B0BEC5] leading-relaxed max-w-2xl">{subtitle}</p>
        )}
      </div>
      {actions && <div className="flex items-center gap-3 shrink-0">{actions}</div>}
    </div>
  );
}
export default PageHeader;
