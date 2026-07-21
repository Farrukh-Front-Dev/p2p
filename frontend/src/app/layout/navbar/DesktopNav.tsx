import { useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { NavLink } from './NavLink';

export function DesktopNav() {
  const location = useLocation();
  const pathname = location.pathname;
  const { t } = useTranslation();

  return (
    <div className="hidden lg:flex items-center justify-center bg-gradient-to-br from-[#38C9E6] to-[#43E8A0] rounded-2xl border-2 border-gray-900 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] px-5 py-2.5 gap-3 font-montserrat">
      <NavLink
        to="/dashboard"
        label={t('nav.home')}
        isActive={pathname.startsWith('/dashboard')}
      />
      <NavLink
        to="/slots"
        label={t('nav.slots')}
        isActive={pathname.startsWith('/slots')}
      />
      <NavLink
        to="/leaderboard"
        label={t('nav.leaderboard')}
        isActive={pathname.startsWith('/leaderboard')}
      />
    </div>
  );
}

export default DesktopNav;
