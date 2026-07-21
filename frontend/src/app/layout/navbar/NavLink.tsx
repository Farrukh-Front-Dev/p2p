import { Link } from 'react-router-dom';
import { ArrowUpRight } from 'lucide-react';

interface NavLinkProps {
  to: string;
  label: string;
  isActive: boolean;
  onClick?: () => void;
}

export function NavLink({ to, label, isActive, onClick }: NavLinkProps) {
  return (
    <Link
      to={to}
      onClick={onClick}
      className={`relative flex items-center gap-2 px-4 py-2 rounded-xl font-extrabold font-montserrat text-base transition-all duration-200 ${
        isActive
          ? 'bg-white/40 backdrop-blur-md text-gray-900 shadow-[2px_2px_0px_0px_rgba(0,0,0,0.2)]'
          : 'text-gray-900 hover:bg-white/20 hover:scale-105 hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,0.1)] group'
      }`}
    >
      {label}
      <ArrowUpRight className="w-4 h-4 transition-transform duration-200 group-hover:translate-x-0.5 group-hover:-translate-y-0.5" />
    </Link>
  );
}

export default NavLink;
