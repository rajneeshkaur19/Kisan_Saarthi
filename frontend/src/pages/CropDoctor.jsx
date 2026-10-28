import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import {
  UploadCloud,
  Stethoscope,
  AlertTriangle,
  CheckCircle2,
  ShieldAlert,
  TrendingUp,
  Landmark,
  Share2,
  RefreshCw,
  X,
  Sparkles,
  Shield
} from 'lucide-react'
import { diagnoseLeaf, normalizeLang } from '../api/client'

export default function CropDoctor() {
  const { t, i18n } = useTranslation()
  const navigate = useNavigate()
  const currentLang = normalizeLang(i18n.language)

  const [selectedFile, setSelectedFile] = useState(null)
  const [previewUrl, setPreviewUrl] = useState(null)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [errorMsg, setErrorMsg] = useState(null)
  const [activeTab, setActiveTab] = useState('upload') // 'upload' | 'sample'

  const sampleLeaves = [
    {
      id: 'tomato_early_blight',
      label: t('doctor.sample_options.tomato_blight'),
      url: '/samples/tomato_early_blight.jpg',
      crop: 'Tomato'
    },
    {
      id: 'wheat_yellow_rust',
      label: t('doctor.sample_options.wheat_rust'),
      url: '/samples/wheat_yellow_rust.jpg',
      crop: 'Wheat'
    },
    {
      id: 'rice_leaf_blast',
      label: t('doctor.sample_options.rice_blast'),
      url: '/samples/rice_leaf_blast.jpg',
      crop: 'Rice'
    },
    {
      id: 'tomato_healthy',
      label: t('doctor.sample_options.healthy'),
      url: '/samples/tomato_healthy.jpg',
      crop: 'Tomato'
    },
    {
      id: 'unclear_sample',
      label: 'Blurry / Ambiguous Leaf (Uncertainty Test)',
      url: '/samples/unclear_sample.jpg',
      crop: 'Unclear'
    }
  ]

  const handleFileChange = (e) => {
    const file = e.target.files?.[0]
    if (!file) return

    if (!file.type.startsWith('image/')) {
      setErrorMsg('Please select a valid image file (JPG, PNG, WebP).')
      return
    }

    if (file.size > 10 * 1024 * 1024) {
      setErrorMsg('Image size cannot exceed 10MB.')
      return
    }

    setErrorMsg(null)
    setResult(null)
    setSelectedFile(file)
    setPreviewUrl(URL.createObjectURL(file))
  }

  const handleSelectSample = async (sample) => {
    try {
      setLoading(true)
      setErrorMsg(null)
      const res = await fetch(sample.url)
      const blob = await res.blob()
      const file = new File([blob], `${sample.id}.jpg`, { type: 'image/jpeg' })

      setSelectedFile(file)
      setPreviewUrl(sample.url)

      // Run diagnosis
      const diagRes = await diagnoseLeaf(file, currentLang)
      if (diagRes.status === 'ok') {
        setResult(diagRes.data)
      } else {
        setErrorMsg(diagRes.error?.message || 'Inference error.')
      }
    } catch (err) {
      setErrorMsg('Failed to load sample leaf.')
    } finally {
      setLoading(false)
    }
  }

  const handleDiagnose = async () => {
    if (!selectedFile) return
    try {
      setLoading(true)
      setErrorMsg(null)
      const diagRes = await diagnoseLeaf(selectedFile, currentLang)
      if (diagRes.status === 'ok') {
        setResult(diagRes.data)
      } else {
        setErrorMsg(diagRes.error?.message || 'Diagnosis failed.')
      }
    } catch (err) {
      setErrorMsg('Failed to connect to backend diagnosis service.')
    } finally {
      setLoading(false)
    }
  }

  const handleReset = () => {
    setSelectedFile(null)
    setPreviewUrl(null)
    setResult(null)
    setErrorMsg(null)
  }

  const handleShare = async () => {
    if (!result) return

    const shareText = `Crop: ${result.crop}\nDisease: ${result.disease_name}\nConfidence: ${result.confidence_percent}%\nTreatment: ${result.treatment_steps?.[0] || 'See full details'}`

    if (navigator.share) {
      try {
        await navigator.share({
          title: `KisanSaarthi Diagnosis: ${result.disease_name}`,
          text: shareText,
          url: window.location.href
        })
      } catch {
        /* user cancelled */
      }
      return
    }

    try {
      if (navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(shareText)
        alert('Advice summary copied to clipboard!')
      } else {
        alert(shareText)
      }
    } catch {
      alert(shareText)
    }
  }

  return (
    <>
      {/* Demo mode banner if result indicates demo */}
      {result && result.demo_mode && (
        <div className="bg-yellow-100 border border-yellow-300 text-yellow-800 p-3 rounded mb-4">
          <strong>DEMO MODE — AI model not yet validated.</strong>
          <p className="mt-1 text-sm">
            The diagnosis shown below is a simulated example and does not reflect an actual model prediction.
          </p>
        </div>
      )}

      {/* Existing UI */}
      <div className="max-w-4xl mx-auto space-y-6 pb-20 md:pb-8">
        {/* Header */}
        <div>
          <div className="flex items-center gap-2 mb-1">
            <div className="w-8 h-8 rounded-xl bg-emerald-100 text-emerald-800 flex items-center justify-center">
              <Stethoscope className="w-5 h-5" />
            </div>
            <h2 className="text-2xl font-extrabold text-gray-900 tracking-tight">
              {t('doctor.title')}
            </h2>
          </div>
          <p className="text-sm text-gray-500 pl-10">
            {t('doctor.subtitle')}
          </p>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-gray-200">
          <button
            onClick={() => setActiveTab('upload')}
            className={`py-3 px-6 text-sm font-bold border-b-2 transition-colors cursor-pointer ${
              activeTab === 'upload'
                ? 'border-emerald-600 text-emerald-700'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            {t('doctor.tab_upload')}
          </button>
          <button
            onClick={() => setActiveTab('sample')}
            className={`py-3 px-6 text-sm font-bold border-b-2 transition-colors cursor-pointer ${
              activeTab === 'sample'
                ? 'border-emerald-600 text-emerald-700'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            {t('doctor.tab_sample')}
          </button>
        </div>

        {/* Sample Leaves Picker */}
        {activeTab === 'sample' && (
          <div className="bg-emerald-50/70 border border-emerald-100 rounded-2xl p-4">
            <p className="text-xs font-semibold text-emerald-950 uppercase tracking-wide mb-3 flex items-center gap-1.5">
              <Sparkles className="w-4 h-4 text-emerald-600" />
              Select a verified leaf sample to test diagnosis (works offline in demo mode):
            </p>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {sampleLeaves.map((sample) => (
                <button
                  key={sample.id}
                  onClick={() => handleSelectSample(sample)}
                  className="bg-white hover:bg-emerald-50 rounded-xl p-2.5 border border-emerald-200 text-left transition-all hover:shadow-xs group cursor-pointer"
                >
                  <div className="w-full h-24 rounded-lg overflow-hidden mb-2 bg-gray-100">
                    <img
                      src={sample.url}
                      alt={sample.label}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform"
                    />
                  </div>
                  <p className="text-xs font-bold text-gray-800 line-clamp-1">{sample.label}</p>
                  <span className="text-[10px] text-emerald-700 font-semibold">{sample.crop}</span>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Dropzone & Image Preview */}
        <div className="bg-white rounded-2xl p-6 border border-gray-200/90 shadow-xs">
          {!previewUrl ? (
            <label className="border-2 border-dashed border-gray-300 hover:border-emerald-500 rounded-2xl p-8 flex flex-col items-center justify-center cursor-pointer transition-colors bg-gray-50/50 hover:bg-emerald-50/30">
              <div className="w-14 h-14 rounded-2xl bg-emerald-50 text-emerald-700 flex items-center justify-center mb-3">
                <UploadCloud className="w-8 h-8 stroke-[1.8]" />
              </div>
              <p className="text-sm font-bold text-gray-800 mb-1">{t('doctor.dropzone_title')}</p>
              <p className="text-xs text-gray-400">{t('doctor.dropzone_hint')}</p>
              <input
                type="file"
                accept="image/jpeg,image/png,image/webp"
                capture="environment"
                onChange={handleFileChange}
                className="hidden"
              />
            </label>
          ) : (
            <div className="space-y-4">
              <div className="relative max-w-md mx-auto rounded-2xl overflow-hidden border border-gray-200 bg-gray-900 shadow-inner">
                <img
                  src={previewUrl}
                  alt="Selected leaf preview"
                  className="w-full max-h-72 object-contain mx-auto"
                />
                <button
                  onClick={handleReset}
                  className="absolute top-2 right-2 p-1.5 rounded-full bg-black/60 hover:bg-black/80 text-white transition-colors"
                  title="Remove photo"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              <div className="flex flex-wrap items-center justify-center gap-3">
                <label className="px-4 py-2 rounded-xl text-xs font-bold text-gray-700 bg-gray-100 hover:bg-gray-200 transition-colors cursor-pointer">
                  {t('doctor.change_image')}
                  <input
                    type="file"
                    accept="image/jpeg,image/png,image/webp"
                    capture="environment"
                    onChange={handleFileChange}
                    className="hidden"
                  />
                </label>

                <button
                  onClick={handleDiagnose}
                  disabled={loading}
                  className="px-6 py-2.5 rounded-xl bg-emerald-700 hover:bg-emerald-800 text-white text-xs font-bold shadow-md shadow-emerald-900/10 flex items-center gap-2 disabled:opacity-50 cursor-pointer"
                >
                  {loading ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      <span>{t('doctor.analyzing')}</span>
                    </>
                  ) : (
                    <>
                      <Stethoscope className="w-4 h-4" />
                      <span>{t('doctor.diagnose_btn')}</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          )}

          {errorMsg && (
            <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-xl text-red-800 text-xs flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 shrink-0 text-red-600" />
              <span>{errorMsg}</span>
            </div>
          )}
        </div>

        {/* Detection Result Card Matching Wireframe 3 */}
        {result && (
          <div className="bg-white rounded-3xl p-6 md:p-8 border border-emerald-100 shadow-md space-y-6 animate-fadeIn">
            {/* Header row */}
            <div className="flex flex-wrap items-start justify-between gap-4 pb-4 border-b border-gray-100">
              <div>
                <span className="text-[11px] font-bold uppercase tracking-wider text-emerald-800 bg-emerald-50 px-2.5 py-1 rounded-md">
                  {result.crop} • {t('doctor.detection_result')}
                </span>
                <h3 className="text-2xl font-black text-gray-900 mt-2">
                  {result.disease_name}
                </h3>
              </div>
              <div className="text-right">
                <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-900">
                  <CheckCircle2 className="w-4 h-4 text-emerald-700" />
                  <span className="text-xs font-bold">
                    {t('doctor.confidence')}: {result.confidence_percent}%
                  </span>
                </div>
                <p className="text-[10px] text-gray-400 mt-1">
                  {result.demo_mode ? 'Offline demo' : 'AI analysis'}
                </p>
              </div>
            </div>

            {/* Inconclusive Warning if applicable */}
            {result.is_inconclusive && (
              <div className="p-4 bg-amber-50 border border-amber-200 rounded-2xl flex items-start gap-3">
                <AlertTriangle className="w-5 h-5 text-amber-700 shrink-0 mt-0.5" />
                <div>
                  <p className="text-xs font-bold text-amber-900">{t('doctor.inconclusive_title')}</p>
                  <p className="text-xs text-amber-800/90 mt-0.5">{t('doctor.inconclusive_desc')}</p>
                </div>
              </div>
            )}

            {/* Model Confidence & Top Candidates Distribution */}
            {result.top_candidates && result.top_candidates.length > 0 && (
              <div className="p-4 bg-gray-50/80 rounded-2xl border border-gray-100">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[11px] font-bold uppercase tracking-wider text-gray-500">
                    Model Decision Probabilities (Top Candidates)
                  </span>
                  <span className="text-[10px] font-semibold text-emerald-800 bg-emerald-50 px-2 py-0.5 rounded">
                    {result.model_version}
                  </span>
                </div>
                <div className="space-y-2">
                  {result.top_candidates.map((cand, i) => (
                    <div key={i} className="space-y-1">
                      <div className="flex justify-between text-xs font-medium text-gray-700">
                        <span className="truncate max-w-[240px]">{cand.class_key.replace('___', ' - ').replace(/_/g, ' ')}</span>
                        <span className="font-bold text-gray-900">{cand.confidence}%</span>
                      </div>
                      <div className="w-full h-1.5 bg-gray-200 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full transition-all duration-500 ${i === 0 ? 'bg-emerald-600' : 'bg-gray-400'}`}
                          style={{ width: `${Math.min(100, cand.confidence)}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Symptoms */}
            <div>
              <h4 className="text-xs font-bold uppercase tracking-wider text-gray-500 mb-1.5">
                {t('doctor.symptoms')}
              </h4>
              <p className="text-sm text-gray-700 bg-gray-50 p-3.5 rounded-xl border border-gray-100 leading-relaxed">
                {result.symptoms}
              </p>
            </div>

            {/* Treatment Steps */}
            <div>
              <h4 className="text-xs font-bold uppercase tracking-wider text-gray-500 mb-2">
                {t('doctor.treatment_steps')} (ICAR Approved)
              </h4>
              <div className="space-y-2">
                {result.treatment_steps?.map((step, idx) => (
                  <div key={idx} className="flex items-start gap-3 p-3 bg-emerald-50/50 rounded-xl border border-emerald-100">
                    <span className="w-6 h-6 rounded-lg bg-emerald-700 text-white font-bold text-xs flex items-center justify-center shrink-0">
                      {idx + 1}
                    </span>
                    <p className="text-xs text-gray-800 leading-relaxed font-medium">{step}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Prevention */}
            {result.prevention && (
              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-gray-500 mb-2 flex items-center gap-1.5">
                  <Shield className="w-3.5 h-3.5 text-emerald-700" />
                  Prevention
                </h4>
                {Array.isArray(result.prevention) ? (
                  <div className="space-y-2">
                    {result.prevention.map((step, idx) => (
                      <div key={idx} className="flex items-start gap-3 p-3 bg-teal-50/50 rounded-xl border border-teal-100">
                        <span className="w-6 h-6 rounded-lg bg-teal-700 text-white font-bold text-xs flex items-center justify-center shrink-0">
                          {idx + 1}
                        </span>
                        <p className="text-xs text-gray-800 leading-relaxed font-medium">{step}</p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-gray-700 bg-teal-50/50 p-3.5 rounded-xl border border-teal-100 leading-relaxed">
                    {result.prevention}
                  </p>
                )}
              </div>
            )}

            {/* Caution Alert */}
            {result.caution && (
              <div className="p-3.5 bg-rose-50 border border-rose-200 rounded-xl flex items-start gap-2.5 text-rose-900 text-xs">
                <ShieldAlert className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
                <div>
                  <span className="font-bold">{t('doctor.caution')}: </span>
                  <span>{result.caution}</span>
                </div>
              </div>
            )}

            {/* Related Schemes chips */}
            {result.related_schemes && result.related_schemes.length > 0 && (
              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-gray-500 mb-2">
                  Related Schemes
                </h4>
                <div className="flex flex-wrap gap-2">
                  {result.related_schemes.map((scheme, idx) => {
                    const label =
                      typeof scheme === 'string'
                        ? scheme
                        : scheme.short_name || scheme.name || scheme.code || 'Scheme'
                    return (
                      <button
                        key={idx}
                        type="button"
                        onClick={() =>
                          navigate('/schemes', {
                            state: {
                              prefilledCrop: result.crop,
                              sourceDisease: result.disease_name
                            }
                          })
                        }
                        className="text-xs bg-teal-50 hover:bg-teal-100 text-teal-900 border border-teal-200 px-3 py-1.5 rounded-xl font-semibold transition-colors cursor-pointer"
                      >
                        {label}
                      </button>
                    )
                  })}
                </div>
              </div>
            )}

            {/* Action Buttons Matching Wireframe 3 */}
            <div className="pt-4 border-t border-gray-100 flex flex-wrap items-center gap-3">
              <button
                onClick={handleShare}
                className="px-4 py-2.5 rounded-xl bg-emerald-700 hover:bg-emerald-800 text-white text-xs font-bold flex items-center gap-2 shadow-xs cursor-pointer"
              >
                <Share2 className="w-4 h-4" />
                <span>{t('doctor.share_advice')}</span>
              </button>

              <button
                onClick={() => navigate(`/prices?crop=${encodeURIComponent(result.mandi_crop || result.crop)}`)}
                className="px-4 py-2.5 rounded-xl bg-gray-100 hover:bg-gray-200 text-gray-800 text-xs font-bold flex items-center gap-2 transition-colors cursor-pointer"
              >
                <TrendingUp className="w-4 h-4 text-emerald-700" />
                <span>{t('doctor.explore_mandi')}</span>
              </button>

              <button
                onClick={() => navigate('/schemes', {
                  state: {
                    prefilledCrop: result.crop,
                    sourceDisease: result.disease_name
                  }
                })}
                className="px-4 py-2.5 rounded-xl bg-teal-50 hover:bg-teal-100 text-teal-900 text-xs font-bold flex items-center gap-2 border border-teal-200 transition-colors cursor-pointer"
              >
                <Landmark className="w-4 h-4 text-teal-700" />
                <span>{t('doctor.check_schemes')}</span>
              </button>
            </div>
          </div>
        )}
      </div>
    </>
  )
}
