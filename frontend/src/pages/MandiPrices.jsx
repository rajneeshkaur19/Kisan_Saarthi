import React, { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import {
  TrendingUp,
  MapPin,
  Wheat,
  AlertCircle,
  RefreshCw,
  Building2,
  Info
} from 'lucide-react'
import {
  ResponsiveContainer,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Area,
  AreaChart
} from 'recharts'
import { getMandiPrices } from '../api/client'

export default function MandiPrices() {
  const { t } = useTranslation()
  const [searchParams, setSearchParams] = useSearchParams()

  const defaultCrop = searchParams.get('crop') || 'Wheat'
  const defaultMandi = searchParams.get('mandi') || 'ludhiana'

  const [selectedCrop, setSelectedCrop] = useState(defaultCrop)
  const [selectedMandi, setSelectedMandi] = useState(defaultMandi)
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [errorMsg, setErrorMsg] = useState(null)

  useEffect(() => {
    fetchPrices(selectedCrop, selectedMandi)
  }, [selectedCrop, selectedMandi])

  // Keep URL query params in sync with crop/mandi selection
  useEffect(() => {
    setSearchParams(
      { crop: selectedCrop, mandi: selectedMandi },
      { replace: true }
    )
  }, [selectedCrop, selectedMandi, setSearchParams])

  // When available lists arrive, keep selection valid
  useEffect(() => {
    if (!data) return

    if (data.available_crops?.length) {
      const cropOk = data.available_crops.some(
        (c) => c.toLowerCase() === selectedCrop.toLowerCase()
      )
      if (!cropOk) setSelectedCrop(data.available_crops[0])
    }

    if (data.available_mandis?.length) {
      const mandiOk = data.available_mandis.some(
        (m) => m.id === selectedMandi
      )
      if (!mandiOk) setSelectedMandi(data.available_mandis[0].id)
    }
  }, [data])

  const fetchPrices = async (crop, mandi) => {
    try {
      setLoading(true)
      setErrorMsg(null)
      const res = await getMandiPrices(crop, mandi)
      if (res.status === 'ok') {
        setData(res.data)
      } else {
        setErrorMsg(res.error?.message || 'Failed to fetch prices.')
      }
    } catch (err) {
      setErrorMsg('Could not reach market price service.')
    } finally {
      setLoading(false)
    }
  }

  const record = data?.selected_record
  const isHold = record?.recommendation === 'HOLD'
  const isSell = record?.recommendation === 'SELL'
  const isInsufficient = record?.recommendation === 'INSUFFICIENT DATA'

  return (
    <div className="max-w-4xl mx-auto space-y-6 pb-20 md:pb-8">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2 mb-1">
          <div className="w-8 h-8 rounded-xl bg-green-100 text-green-800 flex items-center justify-center">
            <TrendingUp className="w-5 h-5" />
          </div>
          <h2 className="text-2xl font-extrabold text-gray-900 tracking-tight">
            {t('prices.title')}
          </h2>
        </div>
        <p className="text-sm text-gray-500 pl-10">
          {t('prices.subtitle')}
        </p>
      </div>

      {/* Selectors Bar Matching Wireframe 4 */}
      <div className="bg-white rounded-2xl p-4 md:p-5 border border-gray-200/90 shadow-xs grid grid-cols-1 sm:grid-cols-2 gap-4">
        {/* Mandi Selector */}
        <div>
          <label className="block text-xs font-bold text-gray-700 mb-1.5 flex items-center gap-1.5">
            <MapPin className="w-3.5 h-3.5 text-emerald-700" />
            <span>{t('prices.select_mandi')}</span>
          </label>
          <select
            value={selectedMandi}
            onChange={(e) => setSelectedMandi(e.target.value)}
            className="w-full px-3.5 py-2.5 text-sm bg-gray-50 border border-gray-200 rounded-xl font-medium text-gray-800 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-600 transition-all cursor-pointer"
          >
            {data?.available_mandis?.map((m) => (
              <option key={m.id} value={m.id}>
                {m.name} ({m.state})
              </option>
            )) || (
              <>
                <option value="ludhiana">Ludhiana APMC (Punjab)</option>
                <option value="moga">Moga APMC (Punjab)</option>
                <option value="karnal">Karnal APMC (Haryana)</option>
                <option value="indore">Indore Mandi (Madhya Pradesh)</option>
              </>
            )}
          </select>
        </div>

        {/* Commodity / Crop Selector */}
        <div>
          <label className="block text-xs font-bold text-gray-700 mb-1.5 flex items-center gap-1.5">
            <Wheat className="w-3.5 h-3.5 text-emerald-700" />
            <span>{t('prices.select_crop')}</span>
          </label>
          <select
            value={selectedCrop}
            onChange={(e) => setSelectedCrop(e.target.value)}
            className="w-full px-3.5 py-2.5 text-sm bg-gray-50 border border-gray-200 rounded-xl font-medium text-gray-800 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-600 transition-all cursor-pointer"
          >
            {data?.available_crops?.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            )) || (
              <>
                <option value="Wheat">Wheat</option>
                <option value="Paddy">Paddy</option>
                <option value="Potato">Potato</option>
                <option value="Tomato">Tomato</option>
                <option value="Cotton">Cotton</option>
              </>
            )}
          </select>
        </div>
      </div>

      {loading ? (
        <div className="bg-white rounded-2xl p-12 text-center border border-gray-100 flex flex-col items-center justify-center">
          <RefreshCw className="w-8 h-8 text-emerald-600 animate-spin mb-3" />
          <p className="text-sm font-semibold text-gray-600">
            Retrieving APMC price records...
          </p>
        </div>
      ) : errorMsg ? (
        <div className="p-4 bg-red-50 border border-red-200 rounded-2xl text-red-800 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-red-600 shrink-0" />
          <span>{errorMsg}</span>
        </div>
      ) : record ? (
        <div className="space-y-6">
          {/* Current Price & Sell/Hold Heuristic Card Matching Wireframe 4 */}
          <div className="bg-white rounded-3xl p-6 md:p-8 border border-emerald-100 shadow-sm grid grid-cols-1 md:grid-cols-2 gap-6 items-center">
            {/* Price Column */}
            <div>
              <div className="flex items-center gap-2 text-xs font-semibold text-gray-500 mb-1">
                <Building2 className="w-4 h-4 text-emerald-700" />
                <span>{record.mandi} • {record.district}, {record.state}</span>
              </div>

              <h3 className="text-lg font-bold text-gray-900 mb-1">
                {record.crop} <span className="text-xs text-gray-500 font-normal">({record.variety})</span>
              </h3>

              <div className="flex items-baseline gap-2 my-2">
                <span className="text-3xl md:text-4xl font-black text-emerald-950">
                  ₹ {record.current_price?.toLocaleString('en-IN')}
                </span>
                <span className="text-sm font-semibold text-gray-500">
                  {t('prices.per_quintal')}
                </span>
              </div>

              <div className="flex flex-wrap items-center gap-3 text-xs text-gray-600 mt-3 pt-3 border-t border-gray-100">
                {record.msp_benchmark > 0 && (
                  <span>
                    <strong>{t('prices.msp_benchmark')}:</strong> ₹ {record.msp_benchmark}
                  </span>
                )}
                <span>
                  <strong>{t('prices.daily_arrivals')}:</strong> {record.arrivals_tonnes} {t('prices.tonnes')}
                </span>
              </div>
            </div>

            {/* Recommendation Column Matching Wireframe 4 */}
            <div className={`p-5 rounded-2xl border ${
              isHold
                ? 'bg-emerald-50 border-emerald-200 text-emerald-950'
                : isSell
                ? 'bg-amber-50 border-amber-200 text-amber-950'
                : 'bg-gray-50 border-gray-200 text-gray-900'
            }`}>
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-extrabold uppercase tracking-wider">
                  {t('prices.sell_or_hold')}
                </span>
                <span className={`px-3 py-1 rounded-full text-xs font-black shadow-xs ${
                  isHold
                    ? 'bg-emerald-600 text-white'
                    : isSell
                    ? 'bg-amber-600 text-white'
                    : 'bg-gray-600 text-white'
                }`}>
                  {record.recommendation}
                </span>
              </div>

              <p className="text-xs leading-relaxed font-medium">
                {record.recommendation_reason}
              </p>
            </div>
          </div>

          {/* Recharts Price Trend Chart Matching Wireframe 4 */}
          <div className="bg-white rounded-3xl p-6 border border-gray-200/90 shadow-xs">
            <div className="flex items-center justify-between mb-4">
              <h4 className="text-sm font-bold text-gray-900 flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-emerald-700" />
                <span>{record.crop} {t('prices.price_trend_chart')}</span>
              </h4>
              <span className="text-xs font-semibold text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-lg">
                15-Day Observed Trend
              </span>
            </div>

            {record.history && record.history.length > 0 ? (
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={record.history} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <defs>
                      <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#10b981" stopOpacity={0.25} />
                        <stop offset="95%" stopColor="#10b981" stopOpacity={0.0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                    <XAxis
                      dataKey="date"
                      tick={{ fontSize: 11, fill: '#6b7280' }}
                      stroke="#e5e7eb"
                    />
                    <YAxis
                      domain={['auto', 'auto']}
                      tick={{ fontSize: 11, fill: '#6b7280' }}
                      stroke="#e5e7eb"
                    />
                    <Tooltip
                      formatter={(val) => [`₹ ${val} / quintal`, 'Price']}
                      contentStyle={{ backgroundColor: '#ffffff', borderRadius: '12px', border: '1px solid #e5e7eb', fontSize: '12px' }}
                    />
                    <Area
                      type="monotone"
                      dataKey="price"
                      stroke="#059669"
                      strokeWidth={2.5}
                      fillOpacity={1}
                      fill="url(#priceGradient)"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <div className="p-8 text-center text-xs text-gray-500">
                Insufficient price history points recorded for chart rendering.
              </div>
            )}
          </div>

          {/* Nearby Mandis Comparison Table Matching Wireframe 4 */}
          {record.nearby_comparisons && record.nearby_comparisons.length > 0 && (
            <div className="bg-white rounded-3xl p-6 border border-gray-200/90 shadow-xs">
              <h4 className="text-sm font-bold text-gray-900 mb-4 flex items-center gap-2">
                <MapPin className="w-4 h-4 text-emerald-700" />
                <span>{t('prices.nearby_mandis')}</span>
              </h4>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="border-b border-gray-100 text-gray-400 font-bold uppercase tracking-wider">
                      <th className="py-2.5 px-3">{t('prices.col_mandi')}</th>
                      <th className="py-2.5 px-3">{t('prices.col_distance')}</th>
                      <th className="py-2.5 px-3">{t('prices.col_price')}</th>
                      <th className="py-2.5 px-3">{t('prices.col_trend')}</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-50">
                    {record.nearby_comparisons.map((item, idx) => (
                      <tr key={idx} className="hover:bg-gray-50/80 transition-colors">
                        <td className="py-3 px-3 font-bold text-gray-800">{item.mandi}</td>
                        <td className="py-3 px-3 text-gray-500">{item.distance}</td>
                        <td className="py-3 px-3 font-extrabold text-emerald-950">
                          ₹ {item.price?.toLocaleString('en-IN')}
                        </td>
                        <td className="py-3 px-3">
                          <span className={`inline-block px-2 py-0.5 rounded-md font-bold text-[11px] ${
                            item.trend?.startsWith('+')
                              ? 'bg-emerald-50 text-emerald-700'
                              : item.trend?.startsWith('-')
                              ? 'bg-rose-50 text-rose-700'
                              : 'bg-gray-100 text-gray-600'
                          }`}>
                            {item.trend}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Source Attribution & Disclaimer Banner */}
          <div className="p-4 bg-gray-50 rounded-2xl border border-gray-200 text-[11px] text-gray-500 flex items-start gap-2.5">
            <Info className="w-4 h-4 text-emerald-700 shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold text-gray-700">
                {t('prices.source_label')}: {data?.source} ({data?.source_type})
              </p>
              <p className="mt-0.5">{data?.disclaimer}</p>
            </div>
          </div>
        </div>
      ) : (
        <div className="bg-white rounded-2xl p-10 text-center border border-gray-100 flex flex-col items-center justify-center">
          <AlertCircle className="w-8 h-8 text-gray-400 mb-3" />
          <p className="text-sm font-semibold text-gray-700 mb-1">
            No price record found
          </p>
          <p className="text-xs text-gray-500 max-w-sm">
            No APMC modal rate matched this crop and mandi. Try another combination from the selectors above.
          </p>
          <button
            type="button"
            onClick={() => fetchPrices(selectedCrop, selectedMandi)}
            className="mt-4 px-4 py-2 rounded-xl bg-emerald-700 hover:bg-emerald-800 text-white text-xs font-bold flex items-center gap-2 cursor-pointer"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            Retry
          </button>
        </div>
      )}
    </div>
  )
}
