import React from 'react';
import { NavLink } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  Home,
  Stethoscope,
  TrendingUp,
  Landmark,
  MessageSquare,
  User,
  Sprout
} from 'lucide-react';
import LanguageSelector from './LanguageSelector';

export default function Sidebar() {
  const { t } = useTranslation();

  const navItems = [
    { to: '/home', label: t('nav.home'), icon: Home },
    { to: '/doctor', label: t('nav.crop_doctor'), icon: Stethoscope },
    { to: '/prices', label: t('nav.mandi_prices'), icon: TrendingUp },
    { to: '/schemes', label: t('nav.loan_schemes'), icon: Landmark },
    { to: '/chat', label: t('nav.chatbot'), icon: MessageSquare },
  ];

  return (
    <aside className="hidden md:flex flex-col w-64 bg-[#143d2b] text-white shrink-0 min-h-screen border-r border-[#1e543b]">
      {/* Brand Header */}
      <div className="p-6 border-b border-[#1e543b]">
        <NavLink to="/home" className="flex items-center gap-2.5">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-400 to-green-600 flex items-center justify-center shadow-md">
            <Sprout className="w-6 h-6 text-emerald-950 stroke-[2.5]" />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-1">
              Kisan<span className="text-emerald-400">Saarthi</span>
            </h1>
            <p className="text-[11px] text-emerald-200/70 font-medium">From Farm to Finance</p>
          </div>
        </NavLink>
      </div>

      {/* Navigation links */}
      <nav className="flex-1 p-4 space-y-1.5">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-emerald-600/90 text-white shadow-sm font-semibold'
                    : 'text-emerald-100/80 hover:bg-[#1a4f38] hover:text-white'
                }`
              }
            >
              <Icon className="w-4 h-4 shrink-0" />
              <span>{item.label}</span>
            </NavLink>
          );
        })}
      </nav>

      {/* Language & Profile Footer */}
      <div className="p-4 border-t border-[#1e543b] space-y-3">
        <div className="flex flex-col gap-1.5">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-emerald-300/60 px-1">
            Language / ਭਾਸ਼ਾ
          </span>
          <LanguageSelector variant="select" />
        </div>

        <div className="pt-2 flex items-center gap-3 px-2 py-1.5 rounded-xl bg-[#0f2e20]/60 border border-emerald-900/40">
          <div className="w-8 h-8 rounded-full bg-emerald-700/60 flex items-center justify-center text-emerald-200 font-bold text-xs">
            <User className="w-4 h-4" />
          </div>
          <div className="min-w-0 flex-1">
            <p className="text-xs font-semibold text-white truncate">Sardar Farmer</p>
            <p className="text-[10px] text-emerald-300/70 truncate">Ludhiana, Punjab</p>
          </div>
        </div>
      </div>
    </aside>
  );
}