import React from 'react'
import { NavLink } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { Sprout, PhoneCall, ShieldCheck } from 'lucide-react'
import LanguageSelector from './LanguageSelector'

export default function Navbar() {
  const { t } = useTranslation()

  return (
    <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-sm border-b border-gray-100 px-4 md:px-8 py-3 flex items-center justify-between">
      {/* Mobile Brand / Desktop Title */}
      <div className="flex items-center gap-3">
        <NavLink to="/home" className="flex md:hidden items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-emerald-600 flex items-center justify-center text-white">
            <Sprout className="w-5 h-5 stroke-[2.5]" />
          </div>
          <span className="font-bold text-lg text-emerald-950">
            Kisan<span className="text-emerald-600">Saarthi</span>
          </span>
        </NavLink>

        <div className="hidden md:flex items-center gap-2">
          <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-800 text-xs font-semibold border border-emerald-200">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
            <span>Official Agritech Assistant</span>
          </div>
          <span className="text-xs text-gray-500 font-medium">Agmarknet & ICAR Connected</span>
        </div>
      </div>

      {/* Right Actions: Helpline & Language */}
      <div className="flex items-center gap-3">
        <a
          href="tel:18001801551"
          className="hidden sm:inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-amber-50 hover:bg-amber-100 text-amber-900 border border-amber-200 text-xs font-semibold transition-colors"
          title="Kisan Call Centre Toll Free"
        >
          <PhoneCall className="w-3.5 h-3.5 text-amber-700" />
          <span>Kisan Helpline: 1800-180-1551</span>
        </a>

        <LanguageSelector variant="select" />
      </div>
    </header>
  )
}
