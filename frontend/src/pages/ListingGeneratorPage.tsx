import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { FileText, Copy, Check, Loader2, Wand2 } from 'lucide-react'
import { listingApi } from '@/services/api'
import { cn } from '@/lib/utils'

const LANGUAGES = [
  { code: 'en', name: 'English (US)' },
  { code: 'de', name: 'German' },
  { code: 'fr', name: 'French' },
  { code: 'es', name: 'Spanish' },
  { code: 'it', name: 'Italian' },
  { code: 'jp', name: 'Japanese' },
]

interface GeneratedListing {
  title: string
  bullet_points: string[]
  description: string
  search_terms: string[]
  subject_matter: string[]
  a_plus_draft: string
  seo_score: number
  character_counts: { title: number; description: number; search_terms: number }
}

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false)
  const copy = async () => {
    await navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }
  return (
    <button onClick={copy} className="text-slate-500 hover:text-white transition-colors">
      {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
    </button>
  )
}

function CharCount({ count, max }: { count: number; max: number }) {
  const pct = count / max
  const color = pct > 0.9 ? 'text-red-400' : pct > 0.7 ? 'text-amber-400' : 'text-slate-500'
  return <span className={cn('text-xs', color)}>{count}/{max}</span>
}

export default function ListingGeneratorPage() {
  const [mode, setMode] = useState<'generate' | 'optimize'>('generate')
  const [keyword, setKeyword] = useState('')
  const [asin, setAsin] = useState('')
  const [language, setLanguage] = useState('en')
  const [productDetails, setProductDetails] = useState('')

  const generateMutation = useMutation({
    mutationFn: () => listingApi.generate({
      keyword,
      language,
      product_details: productDetails ? JSON.parse(productDetails) : undefined,
    }),
  })

  const optimizeMutation = useMutation({
    mutationFn: () => listingApi.optimize({ asin, language }),
  })

  const isPending = generateMutation.isPending || optimizeMutation.isPending
  const listing: GeneratedListing | undefined = mode === 'generate' ? generateMutation.data : optimizeMutation.data
  const error = mode === 'generate' ? generateMutation.error : optimizeMutation.error

  const handleSubmit = () => {
    if (mode === 'generate') generateMutation.mutate()
    else optimizeMutation.mutate()
  }

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <FileText className="w-6 h-6 text-purple-400" />
          Listing Generator
        </h1>
        <p className="text-slate-400 mt-1">AI-generated Amazon listings optimized for search and conversion.</p>
      </div>

      {/* Mode toggle */}
      <div className="flex gap-2 mb-6">
        {(['generate', 'optimize'] as const).map(m => (
          <button
            key={m}
            onClick={() => setMode(m)}
            className={cn(
              'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
              mode === m ? 'bg-purple-600 text-white' : 'bg-slate-800 text-slate-400 hover:text-white',
            )}
          >
            {m === 'generate' ? 'Generate from keyword' : 'Optimize from ASIN'}
          </button>
        ))}
      </div>

      {/* Input form */}
      <div className="p-5 bg-slate-900 rounded-xl border border-slate-800 mb-6 space-y-4">
        {mode === 'generate' ? (
          <>
            <div>
              <label className="text-xs text-slate-400 font-medium mb-1 block">Primary keyword / product description *</label>
              <input
                value={keyword}
                onChange={e => setKeyword(e.target.value)}
                placeholder="e.g. stainless steel insulated water bottle 32oz"
                className="w-full bg-slate-800 border border-slate-700 text-white text-sm rounded-lg px-3 py-2.5 focus:ring-1 focus:ring-purple-500 outline-none placeholder:text-slate-600"
              />
            </div>
            <div>
              <label className="text-xs text-slate-400 font-medium mb-1 block">Additional product details (optional JSON)</label>
              <textarea
                value={productDetails}
                onChange={e => setProductDetails(e.target.value)}
                placeholder='{"price": 24.99, "material": "stainless steel", "capacity": "32oz"}'
                rows={3}
                className="w-full bg-slate-800 border border-slate-700 text-white text-sm rounded-lg px-3 py-2.5 focus:ring-1 focus:ring-purple-500 outline-none placeholder:text-slate-600 font-mono resize-none"
              />
            </div>
          </>
        ) : (
          <div>
            <label className="text-xs text-slate-400 font-medium mb-1 block">ASIN to optimize *</label>
            <input
              value={asin}
              onChange={e => setAsin(e.target.value.toUpperCase())}
              placeholder="B01MFCXDYG"
              maxLength={10}
              className="w-full bg-slate-800 border border-slate-700 text-white text-sm rounded-lg px-3 py-2.5 focus:ring-1 focus:ring-purple-500 outline-none placeholder:text-slate-600 font-mono"
            />
          </div>
        )}

        <div className="flex items-end gap-4">
          <div>
            <label className="text-xs text-slate-400 font-medium mb-1 block">Language</label>
            <select
              value={language}
              onChange={e => setLanguage(e.target.value)}
              className="bg-slate-800 border border-slate-700 text-white text-sm rounded-lg px-3 py-2 focus:ring-1 focus:ring-purple-500 outline-none"
            >
              {LANGUAGES.map(l => (
                <option key={l.code} value={l.code}>{l.name}</option>
              ))}
            </select>
          </div>
          <button
            onClick={handleSubmit}
            disabled={isPending || (mode === 'generate' ? !keyword : !asin)}
            className="flex items-center gap-2 px-6 py-2 bg-purple-600 hover:bg-purple-500 disabled:opacity-50 text-white font-medium rounded-lg transition-colors"
          >
            {isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Wand2 className="w-4 h-4" />}
            {isPending ? 'Generating...' : 'Generate Listing'}
          </button>
        </div>
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-900/30 border border-red-700 rounded-xl text-red-300 text-sm">
          {(error as Error).message}
        </div>
      )}

      {/* Result */}
      {listing && (
        <div className="space-y-4">
          {/* SEO score */}
          <div className="flex items-center justify-between p-4 bg-slate-900 rounded-xl border border-slate-800">
            <div>
              <p className="text-white font-semibold">Listing Generated</p>
              <p className="text-slate-400 text-sm mt-0.5">Review and copy each section to Seller Central</p>
            </div>
            <div className="text-right">
              <p className="text-xs text-slate-500 mb-1">SEO Score</p>
              <p className={cn('text-2xl font-bold', listing.seo_score >= 7 ? 'text-emerald-400' : listing.seo_score >= 5 ? 'text-amber-400' : 'text-red-400')}>
                {listing.seo_score.toFixed(1)}/10
              </p>
            </div>
          </div>

          {/* Title */}
          <div className="p-5 bg-slate-900 rounded-xl border border-slate-800">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-white font-semibold text-sm">Title</h3>
              <div className="flex items-center gap-2">
                <CharCount count={listing.character_counts.title} max={200} />
                <CopyButton text={listing.title} />
              </div>
            </div>
            <p className="text-slate-300 text-sm leading-relaxed">{listing.title}</p>
          </div>

          {/* Bullet points */}
          <div className="p-5 bg-slate-900 rounded-xl border border-slate-800">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-white font-semibold text-sm">Bullet Points (5)</h3>
              <CopyButton text={listing.bullet_points.join('\n')} />
            </div>
            <ul className="space-y-2">
              {listing.bullet_points.map((bp, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-slate-300">
                  <span className="text-purple-400 font-bold mt-0.5">{i + 1}.</span>
                  <span>{bp}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Description */}
          <div className="p-5 bg-slate-900 rounded-xl border border-slate-800">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-white font-semibold text-sm">Description</h3>
              <div className="flex items-center gap-2">
                <CharCount count={listing.character_counts.description} max={2000} />
                <CopyButton text={listing.description} />
              </div>
            </div>
            <p className="text-slate-300 text-sm leading-relaxed whitespace-pre-wrap">{listing.description}</p>
          </div>

          {/* Search terms */}
          <div className="p-5 bg-slate-900 rounded-xl border border-slate-800">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-white font-semibold text-sm">Backend Search Terms</h3>
              <div className="flex items-center gap-2">
                <CharCount count={listing.character_counts.search_terms} max={250} />
                <CopyButton text={listing.search_terms.join(' ')} />
              </div>
            </div>
            <div className="flex flex-wrap gap-2">
              {listing.search_terms.map((t, i) => (
                <span key={i} className="text-xs bg-slate-800 text-slate-300 px-2 py-1 rounded-lg">{t}</span>
              ))}
            </div>
          </div>

          {/* A+ draft */}
          {listing.a_plus_draft && (
            <div className="p-5 bg-slate-900 rounded-xl border border-slate-800">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-white font-semibold text-sm">A+ Content Draft</h3>
                <CopyButton text={listing.a_plus_draft} />
              </div>
              <p className="text-slate-300 text-sm leading-relaxed">{listing.a_plus_draft}</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
