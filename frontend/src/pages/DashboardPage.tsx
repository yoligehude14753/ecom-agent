import { Search, TrendingUp, FileText, Star, Eye, Megaphone, ArrowRight, Zap } from 'lucide-react'
import { Link } from 'react-router-dom'
import { cn } from '@/lib/utils'

const cards = [
  {
    to: '/research',
    icon: Search,
    title: 'Product Research',
    description: 'AI-powered product scoring across Amazon Best Sellers categories',
    color: 'from-blue-500/20 to-blue-600/10 border-blue-500/20',
    iconColor: 'text-blue-400',
    stat: 'Score products 0-10',
  },
  {
    to: '/listing',
    icon: FileText,
    title: 'Listing Generator',
    description: 'Generate complete Amazon listings in multiple languages with one click',
    color: 'from-purple-500/20 to-purple-600/10 border-purple-500/20',
    iconColor: 'text-purple-400',
    stat: '6 languages supported',
  },
  {
    to: '/reviews',
    icon: Star,
    title: 'Review Analyzer',
    description: 'Extract pain points, praise and product improvement insights from reviews',
    color: 'from-amber-500/20 to-amber-600/10 border-amber-500/20',
    iconColor: 'text-amber-400',
    stat: 'LLM-powered analysis',
  },
  {
    to: '/monitor',
    icon: Eye,
    title: 'Competitor Monitor',
    description: 'Track price, BSR rank and review changes for any ASIN with alerts',
    color: 'from-emerald-500/20 to-emerald-600/10 border-emerald-500/20',
    iconColor: 'text-emerald-400',
    stat: 'Hourly auto-snapshots',
  },
  {
    to: '/ads',
    icon: Megaphone,
    title: 'Ad Optimizer',
    description: 'Analyze PPC campaigns and get AI keyword bid recommendations',
    color: 'from-rose-500/20 to-rose-600/10 border-rose-500/20',
    iconColor: 'text-rose-400',
    stat: 'Amazon Ads API',
  },
]

export default function DashboardPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-10">
        <div className="flex items-center gap-3 mb-3">
          <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center">
            <Zap className="w-6 h-6 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-white">EcomAgent</h1>
        </div>
        <p className="text-slate-400 text-lg max-w-2xl">
          AI-powered e-commerce automation. Open-source, self-hosted, bring your own LLM key.
        </p>
      </div>

      {/* Workflow hint */}
      <div className="mb-8 p-4 rounded-xl bg-blue-950/50 border border-blue-800/40 flex items-center gap-3 flex-wrap">
        <TrendingUp className="w-5 h-5 text-blue-400 flex-shrink-0" />
        <span className="text-sm text-blue-200 font-medium">Recommended workflow:</span>
        {['Product Research', 'Review Analyzer', 'Listing Generator', 'Competitor Monitor', 'Ad Optimizer'].map(
          (step, i, arr) => (
            <span key={step} className="flex items-center gap-2">
              <span className="text-sm text-blue-300">{step}</span>
              {i < arr.length - 1 && <ArrowRight className="w-4 h-4 text-blue-600" />}
            </span>
          ),
        )}
      </div>

      {/* Module cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
        {cards.map(({ to, icon: Icon, title, description, color, iconColor, stat }) => (
          <Link
            key={to}
            to={to}
            className={cn(
              'group relative rounded-2xl border bg-gradient-to-br p-6 transition-all hover:scale-[1.02] hover:shadow-xl hover:shadow-black/30',
              color,
            )}
          >
            <div className={cn('w-12 h-12 rounded-xl bg-slate-900/60 flex items-center justify-center mb-4', iconColor)}>
              <Icon className="w-6 h-6" />
            </div>
            <h2 className="text-white font-semibold text-lg mb-2">{title}</h2>
            <p className="text-slate-400 text-sm leading-relaxed mb-4">{description}</p>
            <div className="flex items-center justify-between">
              <span className="text-xs text-slate-500 font-mono bg-slate-900/40 px-2 py-1 rounded">{stat}</span>
              <ArrowRight className="w-4 h-4 text-slate-500 group-hover:text-white group-hover:translate-x-1 transition-all" />
            </div>
          </Link>
        ))}
      </div>

      {/* Open source callout */}
      <div className="mt-10 p-5 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between flex-wrap gap-4">
        <div>
          <p className="text-white font-semibold">100% Open Source & Self-Hosted</p>
          <p className="text-slate-400 text-sm mt-1">
            Your data stays local. Bring your own OpenAI / Claude / Gemini / Ollama key.
          </p>
        </div>
        <a
          href="https://github.com/yoligehude14753/ecom-agent"
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-white text-sm font-medium transition-colors"
        >
          View on GitHub
          <ArrowRight className="w-4 h-4" />
        </a>
      </div>
    </div>
  )
}
