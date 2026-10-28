import React from 'react';
import { NavLink } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Home, Stethoscope, TrendingUp, Landmark, MessageSquare } from 'lucide-react';

export default function BottomNav() {
  const { t } = useTranslation();

  const tabs = [
    { to: '/home', label: t('nav.home'), icon: Home },
    { to: '/doctor', label: t('nav.crop_doctor'), icon: Stethoscope },
    { to: '/prices', label: t('nav.mandi_prices'), icon: TrendingUp },
    { to: '/schemes', label: t('nav.loan_schemes'), icon: Landmark },
    { to: '/chat', label: t('nav.chatbot'), icon: MessageSquare },
  ];

  return (
    <nav className="md:hidden fixed bottom-0 left-0 right-0 z-50 bg-white/95 backdrop-blur-md border-t border-emerald-100 shadow-[0_-4px_12px_rgba(0,0,0,0.05)]">
      <div className="grid grid-cols-5 h-16">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          return (
            <NavLink
              key={tab.to}
              to={tab.to}
              className={({ isActive }) =>
                `flex flex-col items-center justify-center gap-1 text-[11px] font-medium transition-colors ${
                  isActive ? 'text-emerald-700 font-bold' : 'text-gray-500 hover:text-emerald-600'
                }`
              }
            >
              {({ isActive }) => (
                <>
                  <div
                    className={`p-1 rounded-full transition-transform ${
                      isActive ? 'bg-emerald-100 text-emerald-800 scale-105' : ''
                    }`}
                  >
                    <Icon className="w-5 h-5" />
                  </div>
                  <span className="truncate max-w-[64px] text-center">{tab.label}</span>
                </>
              )}
            </NavLink>
          );
        })}
      </div>
    </nav>
  );
}