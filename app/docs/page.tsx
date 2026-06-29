'use client'
// app/docs/page.tsx — SecureScan Pro v5.0 · Documentación
//
// Migración i18n: 100% del texto descriptivo ahora usa t('docs.xxx').
// Fix de ortografía incluido: el archivo original tenía decenas de palabras
// sin tildes (tecnologico, Deteccion, codigo, sesion...) — las claves nuevas
// usan español correcto desde el origen.
//
// Los bloques `usage` (comandos CLI), los ejemplos de API (JSON/JS) y el
// árbol de `fileStructure` NO se traducen — son sintaxis universal de
// herramientas y código, igual en cualquier idioma.
//
// Convertido a Client Component (antes Server Component) porque
// useTranslations requiere reactividad inmediata al cambiar de idioma,
// igual que el resto del sitio (sin recarga de página).
//
// Docs Premium: migrado al sistema cyber (CyberCard/CyberPanel/CyberBadge),
// + motion (Home/Scanner/History/Lab), + buscador de herramientas y
// navegación lateral con anclas (nuevo, no existía en la versión anterior).

import { useState, useMemo } from 'react'
import {
  BookOpen,
  Code2,
  Layers,
  Network,
  Search,
  Zap,
  Database,
  Skull,
  FileText,
  ChevronRight,
  ExternalLink,
  Shield,
  Wind,
  Key,
  Target,
  X,
} from 'lucide-react'
import Link from 'next/link'
import { useTranslations } from 'next-intl'
import { motion, useReducedMotion } from 'framer-motion'
import { Input } from '@/components/ui/input'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Header } from '@/components/header'
import { CyberCard }   from '@/components/cyber/CyberCard'
import { CyberPanel }  from '@/components/cyber/CyberPanel'
import { CyberButton } from '@/components/cyber/CyberButton'
import { CyberBadge }  from '@/components/cyber/CyberBadge'
import { cn } from '@/lib/utils'
import {
  fadeIn, slideInUp, staggerContainer, staggerItem, getVariants,
} from '@/lib/motion'

type TFunc = ReturnType<typeof useTranslations>

// ─── Datos de herramientas (texto vía t, comandos fijos) ───────────────────

function getTools(t: TFunc) {
  return [
    {
      id: 'wappalyzer',
      name: 'Wappalyzer',
      icon: Layers,
      description: t('docs.tool1Desc'),
      usage: `# Uso via CLI (wappalyzer-cli)
wappalyzer https://target.com

# Formato JSON
wappalyzer https://target.com --output=json

# Con timeout personalizado
wappalyzer https://target.com --timeout=30`,
      features: [
        t('docs.tool1Feature1'), t('docs.tool1Feature2'), t('docs.tool1Feature3'),
        t('docs.tool1Feature4'), t('docs.tool1Feature5'),
      ],
      documentation: 'https://github.com/wappalyzer/wappalyzer',
    },
    {
      id: 'nmap',
      name: 'Nmap',
      icon: Network,
      description: t('docs.tool2Desc'),
      usage: `# Escaneo de puertos comunes
nmap -sV -sC target.com

# Escaneo agresivo
nmap -A -T4 target.com

# Scripts NSE de vulnerabilidades
nmap --script vuln target.com`,
      features: [
        t('docs.tool2Feature1'), t('docs.tool2Feature2'), t('docs.tool2Feature3'),
        t('docs.tool2Feature4'), t('docs.tool2Feature5'),
      ],
      documentation: 'https://nmap.org/book/man.html',
    },
    {
      id: 'patator',
      name: 'Patator',
      icon: Key,
      description: t('docs.tool3Desc'),
      usage: `# Fuerza bruta HTTP POST
patator http_fuzz url=https://target.com/login method=POST body='user=FILE0&pass=FILE1' 0=users.txt 1=passwords.txt

# Fuerza bruta SSH
patator ssh_login host=target.com user=admin password=FILE0 0=passwords.txt

# Fuerza bruta FTP
patator ftp_login host=target.com user=FILE0 password=FILE1 0=users.txt 1=passwords.txt`,
      features: [
        t('docs.tool3Feature1'), t('docs.tool3Feature2'), t('docs.tool3Feature3'),
        t('docs.tool3Feature4'), t('docs.tool3Feature5'),
      ],
      documentation: 'https://github.com/lanjelot/patator',
    },
    {
      id: 'metasploit',
      name: 'Metasploit',
      icon: Skull,
      description: t('docs.tool4Desc'),
      usage: `# Iniciar msfconsole
msfconsole

# Buscar modulos
msf> search apache

# Usar modulo auxiliar
msf> use auxiliary/scanner/http/apache_userdir_enum

# Configurar y ejecutar
msf> set RHOSTS target.com
msf> run`,
      features: [
        t('docs.tool4Feature1'), t('docs.tool4Feature2'), t('docs.tool4Feature3'),
        t('docs.tool4Feature4'), t('docs.tool4Feature5'),
      ],
      documentation: 'https://docs.metasploit.com/',
    },
    {
      id: 'ffuf',
      name: 'ffuf',
      icon: Wind,
      description: t('docs.tool5Desc'),
      usage: `# Fuerza bruta de directorios
ffuf -u https://target.com/FUZZ -w wordlist.txt

# Fuzzing de parametros GET
ffuf -u https://target.com/page?FUZZ=value -w params.txt

# Descubrimiento de vhosts
ffuf -u https://target.com -H "Host: FUZZ.target.com" -w subdomains.txt`,
      features: [
        t('docs.tool5Feature1'), t('docs.tool5Feature2'), t('docs.tool5Feature3'),
        t('docs.tool5Feature4'), t('docs.tool5Feature5'),
      ],
      documentation: 'https://github.com/ffuf/ffuf',
    },
    {
      id: 'gobuster',
      name: 'Gobuster',
      icon: Search,
      description: t('docs.tool6Desc'),
      usage: `# Fuerza bruta de directorios
gobuster dir -u https://target.com -w wordlist.txt

# Descubrimiento DNS
gobuster dns -d target.com -w subdomains.txt

# VHosts
gobuster vhost -u https://target.com -w vhosts.txt`,
      features: [
        t('docs.tool6Feature1'), t('docs.tool6Feature2'), t('docs.tool6Feature3'),
        t('docs.tool6Feature4'), t('docs.tool6Feature5'),
      ],
      documentation: 'https://github.com/OJ/gobuster',
    },
    {
      id: 'zap',
      name: 'OWASP ZAP',
      icon: Zap,
      description: t('docs.tool7Desc'),
      usage: `# API - Spider tradicional
curl "http://localhost:8080/JSON/spider/action/scan/?url=https://target.com"

# API - Ajax Spider
curl "http://localhost:8080/JSON/ajaxSpider/action/scan/?url=https://target.com"

# API - Active Scan
curl "http://localhost:8080/JSON/ascan/action/scan/?url=https://target.com"

# API - Obtener alertas
curl "http://localhost:8080/JSON/alert/view/alerts/"`,
      features: [
        t('docs.tool7Feature1'), t('docs.tool7Feature2'), t('docs.tool7Feature3'),
        t('docs.tool7Feature4'), t('docs.tool7Feature5'),
      ],
      documentation: 'https://www.zaproxy.org/docs/',
    },
    {
      id: 'nuclei',
      name: 'Nuclei',
      icon: Target,
      description: t('docs.tool8Desc'),
      usage: `# Escaneo con todas las plantillas
nuclei -u https://target.com

# Plantillas por severidad
nuclei -u https://target.com -severity critical,high

# Plantillas especificas
nuclei -u https://target.com -t cves/ -t exposures/

# Con cookie de sesion
nuclei -u https://target.com -H "Cookie: session=abc123"`,
      features: [
        t('docs.tool8Feature1'), t('docs.tool8Feature2'), t('docs.tool8Feature3'),
        t('docs.tool8Feature4'), t('docs.tool8Feature5'),
      ],
      documentation: 'https://docs.projectdiscovery.io/tools/nuclei',
    },
    {
      id: 'sqlmap',
      name: 'SQLMap',
      icon: Database,
      description: t('docs.tool9Desc'),
      usage: `# Escaneo de URL con parametro
sqlmap -u "https://target.com/page?id=1"

# Con cookie de sesion
sqlmap -u "https://target.com/page?id=1" --cookie="session=abc123"

# Formulario POST
sqlmap -u "https://target.com/login" --data="user=admin&pass=test"

# Nivel y riesgo agresivo
sqlmap -u "https://target.com/page?id=1" --level=3 --risk=2`,
      features: [
        t('docs.tool9Feature1'), t('docs.tool9Feature2'), t('docs.tool9Feature3'),
        t('docs.tool9Feature4'), t('docs.tool9Feature5'),
      ],
      documentation: 'https://sqlmap.org/',
    },
    {
      id: 'searchsploit',
      name: 'Searchsploit',
      icon: FileText,
      description: t('docs.tool10Desc'),
      usage: `# Busqueda por servicio y version
searchsploit apache 2.4

# Formato JSON
searchsploit -j wordpress 5.8

# Busqueda exacta
searchsploit -e "Apache 2.4.49"

# Copiar exploit localmente
searchsploit -m exploits/php/webapps/12345.py`,
      features: [
        t('docs.tool10Feature1'), t('docs.tool10Feature2'), t('docs.tool10Feature3'),
        t('docs.tool10Feature4'), t('docs.tool10Feature5'),
      ],
      documentation: 'https://www.exploit-db.com/searchsploit',
    },
  ]
}

function getApiEndpoints(t: TFunc) {
  return [
    {
      method: 'POST',
      endpoint: '/api/scan',
      description: t('docs.endpoint1Desc'),
      body: '{ "target": "https://example.com", "options": { "tools": {...}, "intensity": "normal" } }',
    },
    {
      method: 'GET',
      endpoint: '/api/scan/:jobId/status',
      description: t('docs.endpoint2Desc'),
      response: '{ "status": "running", "steps": [...], "progress": 45 }',
    },
    {
      method: 'GET',
      endpoint: '/api/scan/:scanId/report',
      description: t('docs.endpoint3Desc'),
      params: 'format=html|pdf|json',
    },
    {
      method: 'GET',
      endpoint: '/api/history',
      description: t('docs.endpoint4Desc'),
      response: '{ "scans": [...], "total": 25 }',
    },
  ]
}

function getArchSteps(t: TFunc) {
  return [
    { step: 1,  name: 'Wappalyzer',  desc: t('docs.archStep1')  },
    { step: 2,  name: 'Nmap',         desc: t('docs.archStep2')  },
    { step: 3,  name: 'Patator',      desc: t('docs.archStep3')  },
    { step: 4,  name: 'Metasploit',   desc: t('docs.archStep4')  },
    { step: 5,  name: 'ffuf',         desc: t('docs.archStep5')  },
    { step: 6,  name: 'Gobuster',     desc: t('docs.archStep6')  },
    { step: 7,  name: 'OWASP ZAP',    desc: t('docs.archStep7')  },
    { step: 8,  name: 'Nuclei',       desc: t('docs.archStep8')  },
    { step: 9,  name: 'SQLMap',       desc: t('docs.archStep9')  },
    { step: 10, name: 'Searchsploit', desc: t('docs.archStep10') },
  ]
}

// ─── Componente ───────────────────────────────────────────────────────────────

export default function DocsPage() {
  const t = useTranslations()
  const tools         = getTools(t)
  const apiEndpoints  = getApiEndpoints(t)
  const archSteps     = getArchSteps(t)
  const prefersReduced = useReducedMotion() ?? false
  const sv = (v: Parameters<typeof getVariants>[0]) => getVariants(v, prefersReduced)

  const [search, setSearch] = useState('')

  // Filtro de herramientas — busca por nombre o por feature listada
  const filteredTools = useMemo(() => {
    const q = search.trim().toLowerCase()
    if (!q) return tools
    return tools.filter(tool =>
      tool.name.toLowerCase().includes(q) ||
      tool.description.toLowerCase().includes(q) ||
      tool.features.some(f => f.toLowerCase().includes(q))
    )
  }, [tools, search])

  return (
    <div className="flex min-h-screen flex-col bg-background">
      <Header />

      <main className="flex-1 py-8">
        <div className="container mx-auto space-y-8 px-4">
          <motion.div variants={sv(slideInUp)} initial="hidden" animate="visible">
            <h1 className="flex items-center gap-2 text-2xl font-bold tracking-tight">
              <BookOpen className="h-6 w-6 text-[var(--cyber-accent)]" />
              {t('docs.pageTitle')}
            </h1>
            <p className="mt-1 font-mono text-sm text-muted-foreground">
              {t('docs.pageSubtitle')}
            </p>
          </motion.div>

          <Tabs defaultValue="tools" className="space-y-6">
            <TabsList className="h-auto flex-wrap gap-2 bg-transparent p-0">
              <TabsTrigger
                value="tools"
                className="flex items-center gap-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--card))] px-4 py-2 font-mono text-sm data-[state=active]:border-[var(--cyber-accent)] data-[state=active]:bg-[rgba(var(--cyber-accent-rgb),0.08)] data-[state=active]:text-[var(--cyber-accent)] data-[state=active]:shadow-cyber-sm"
              >
                <Code2 className="h-4 w-4" />
                {t('docs.tabTools')}
              </TabsTrigger>
              <TabsTrigger
                value="api"
                className="flex items-center gap-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--card))] px-4 py-2 font-mono text-sm data-[state=active]:border-[var(--cyber-accent)] data-[state=active]:bg-[rgba(var(--cyber-accent-rgb),0.08)] data-[state=active]:text-[var(--cyber-accent)] data-[state=active]:shadow-cyber-sm"
              >
                <FileText className="h-4 w-4" />
                {t('docs.tabApi')}
              </TabsTrigger>
              <TabsTrigger
                value="architecture"
                className="flex items-center gap-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--card))] px-4 py-2 font-mono text-sm data-[state=active]:border-[var(--cyber-accent)] data-[state=active]:bg-[rgba(var(--cyber-accent-rgb),0.08)] data-[state=active]:text-[var(--cyber-accent)] data-[state=active]:shadow-cyber-sm"
              >
                <Layers className="h-4 w-4" />
                {t('docs.tabArchitecture')}
              </TabsTrigger>
            </TabsList>

            <TabsContent value="tools" className="space-y-6">

              {/* ── Buscador + navegación lateral con anclas ── */}
              <div className="grid grid-cols-1 gap-6 lg:grid-cols-[220px_1fr]">

                {/* Sidebar de índice — ancla a cada herramienta */}
                <motion.aside
                  variants={sv(fadeIn)}
                  initial="hidden"
                  animate="visible"
                  className="hidden lg:block"
                >
                  <div className="sticky top-20 space-y-1 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-3">
                    <p className="mb-2 px-2 font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
                      Índice
                    </p>
                    {tools.map(tool => (
                      <a
                        key={tool.id}
                        href={`#${tool.id}`}
                        className="flex items-center gap-2 rounded-md px-2 py-1.5 font-mono text-xs text-muted-foreground transition-colors hover:bg-[rgba(var(--cyber-accent-rgb),0.08)] hover:text-[var(--cyber-accent)]"
                      >
                        <tool.icon className="h-3.5 w-3.5 shrink-0" />
                        <span className="truncate">{tool.name}</span>
                      </a>
                    ))}
                  </div>
                </motion.aside>

                <div className="space-y-6">
                  {/* Buscador */}
                  <motion.div variants={sv(fadeIn)} initial="hidden" animate="visible" className="relative">
                    <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                    <Input
                      value={search}
                      onChange={e => setSearch(e.target.value)}
                      placeholder={t('docs.searchPlaceholder')}
                      className="border-[hsl(var(--border))] bg-[hsl(var(--card))] pl-9 pr-9 font-mono text-sm"
                    />
                    {search && (
                      <button
                        onClick={() => setSearch('')}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                      >
                        <X className="h-4 w-4" />
                      </button>
                    )}
                    {search && (
                      <p className="mt-2 font-mono text-xs text-muted-foreground">
                        {filteredTools.length} de {tools.length} herramientas
                      </p>
                    )}
                  </motion.div>

                  {filteredTools.length === 0 ? (
                    <div className="rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--card))] py-12 text-center">
                      <Search className="mx-auto mb-3 h-8 w-8 text-muted-foreground/40" />
                      <p className="text-sm text-muted-foreground">
                        {t('docs.searchNoResults', { query: search })}
                      </p>
                    </div>
                  ) : (
                    <motion.div
                      className="space-y-6"
                      variants={sv(staggerContainer)}
                      initial="hidden"
                      animate="visible"
                    >
                      {filteredTools.map((tool) => {
                        const Icon = tool.icon
                        return (
                          <motion.div key={tool.id} variants={sv(staggerItem)}>
                          <CyberCard glow id={tool.id} className="scroll-mt-20">
                            <div className="flex flex-wrap items-start justify-between gap-3">
                              <div className="flex items-center gap-3">
                                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-[rgba(var(--cyber-accent-rgb),0.10)]">
                                  <Icon className="h-5 w-5 text-[var(--cyber-accent)]" />
                                </div>
                                <div>
                                  <p className="font-mono text-base font-bold text-foreground">{tool.name}</p>
                                  <p className="text-sm text-muted-foreground">{tool.description}</p>
                                </div>
                              </div>
                              <CyberButton variant="ghost" size="sm" asChild>
                                <a href={tool.documentation} target="_blank" rel="noopener noreferrer">
                                  <ExternalLink className="h-4 w-4" />
                                </a>
                              </CyberButton>
                            </div>

                            <div className="mt-4 space-y-4">
                              <div>
                                <h4 className="mb-2 font-mono text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                                  {t('docs.featuresLabel')}
                                </h4>
                                <ul className="space-y-1">
                                  {tool.features.map((feature, index) => (
                                    <li key={index} className="flex items-center gap-2 text-sm text-muted-foreground">
                                      <ChevronRight className="h-3 w-3 shrink-0 text-[var(--cyber-accent)]" />
                                      {feature}
                                    </li>
                                  ))}
                                </ul>
                              </div>
                              <div>
                                <h4 className="mb-2 font-mono text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                                  {t('docs.usageLabel')}
                                </h4>
                                <pre className="overflow-x-auto rounded-lg bg-[hsl(var(--muted))]/40 p-4 font-mono text-sm text-foreground">
                                  {tool.usage}
                                </pre>
                              </div>
                            </div>
                          </CyberCard>
                          </motion.div>
                        )
                      })}
                    </motion.div>
                  )}
                </div>
              </div>
            </TabsContent>

            <TabsContent value="api" className="space-y-6">
              <motion.div variants={sv(fadeIn)} initial="hidden" animate="visible">
                <CyberPanel title={t('docs.apiTitle')} subtitle={t('docs.apiSubtitle')}>
                  <div className="space-y-4">
                    {apiEndpoints.map((endpoint, index) => (
                      <div key={index} className="rounded-lg border border-[hsl(var(--border))] p-4">
                        <div className="flex items-center gap-2">
                          <span className={cn(
                            'rounded px-2 py-0.5 font-mono text-[10px] font-bold uppercase tracking-wide',
                            endpoint.method === 'POST'
                              ? 'bg-[rgba(var(--cyber-accent-rgb),0.15)] text-[var(--cyber-accent)]'
                              : 'bg-[hsl(var(--muted))]/60 text-muted-foreground',
                          )}>
                            {endpoint.method}
                          </span>
                          <code className="font-mono text-sm text-foreground">{endpoint.endpoint}</code>
                        </div>
                        <p className="mt-2 text-sm text-muted-foreground">
                          {endpoint.description}
                        </p>
                        {endpoint.body && (
                          <pre className="mt-2 overflow-x-auto rounded bg-[hsl(var(--muted))]/40 p-2 font-mono text-xs text-muted-foreground">
                            {t('docs.bodyLabel')}: {endpoint.body}
                          </pre>
                        )}
                        {endpoint.response && (
                          <pre className="mt-2 overflow-x-auto rounded bg-[hsl(var(--muted))]/40 p-2 font-mono text-xs text-muted-foreground">
                            {t('docs.responseLabel')}: {endpoint.response}
                          </pre>
                        )}
                        {endpoint.params && (
                          <pre className="mt-2 overflow-x-auto rounded bg-[hsl(var(--muted))]/40 p-2 font-mono text-xs text-muted-foreground">
                            {t('docs.paramsLabel')}: {endpoint.params}
                          </pre>
                        )}
                      </div>
                    ))}
                  </div>
                </CyberPanel>
              </motion.div>

              <motion.div variants={sv(fadeIn)} initial="hidden" animate="visible">
                <CyberPanel title={t('docs.exampleTitle')} subtitle={t('docs.exampleSubtitle')}>
                  <pre className="overflow-x-auto rounded-lg bg-[hsl(var(--muted))]/40 p-4 font-mono text-sm text-foreground">
{`// Iniciar escaneo
const response = await fetch('/api/scan', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    target: 'https://example.com',
    options: {
      tools: {
        wappalyzer: true,
        nmap: true,
        patator: true,
        metasploit: false,
        ffuf: true,
        gobuster: true,
        zap: true,
        nuclei: true,
        sqlmap: true,
        searchsploit: true
      },
      intensity: 'normal'
    }
  })
});

const { jobId } = await response.json();

// Polling de estado
const checkStatus = async () => {
  const status = await fetch(\`/api/scan/\${jobId}/status\`);
  return status.json();
};`}
                  </pre>
                </CyberPanel>
              </motion.div>
            </TabsContent>

            <TabsContent value="architecture" className="space-y-6">
              <motion.div variants={sv(fadeIn)} initial="hidden" animate="visible">
                <CyberPanel title={t('docs.archTitle')} subtitle={t('docs.archSubtitle')}>
                  <div className="space-y-4">
                    <div className="flex flex-wrap items-center justify-center gap-2">
                      {archSteps.map((item, index, arr) => (
                        <div key={item.step} className="flex items-center gap-2">
                          <div className="flex flex-col items-center rounded-lg border border-[hsl(var(--border))] p-4 text-center">
                            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-[rgba(var(--cyber-accent-rgb),0.15)] font-mono text-sm font-bold text-[var(--cyber-accent)]">
                              {item.step}
                            </div>
                            <span className="mt-2 font-mono text-sm font-medium text-foreground">{item.name}</span>
                            <span className="text-xs text-muted-foreground">{item.desc}</span>
                          </div>
                          {index < arr.length - 1 && (
                            <ChevronRight className="hidden h-5 w-5 text-muted-foreground lg:block" />
                          )}
                        </div>
                      ))}
                    </div>

                    <div className="rounded-lg border border-[hsl(var(--border))] p-4">
                      <h4 className="mb-3 font-mono text-xs font-semibold uppercase tracking-wide text-muted-foreground">{t('docs.stackTitle')}</h4>
                      <div className="grid gap-4 sm:grid-cols-2">
                        <div>
                          <span className="font-mono text-sm font-medium text-foreground">{t('docs.stackFrontend')}</span>
                          <ul className="mt-1 space-y-1 text-sm text-muted-foreground">
                            <li>Next.js 16 + TypeScript</li>
                            <li>Tailwind CSS + shadcn/ui</li>
                            <li>SWR para data fetching</li>
                          </ul>
                        </div>
                        <div>
                          <span className="font-mono text-sm font-medium text-foreground">{t('docs.stackBackend')}</span>
                          <ul className="mt-1 space-y-1 text-sm text-muted-foreground">
                            <li>Python 3.11 + Flask/FastAPI</li>
                            <li>Celery + Redis para colas</li>
                            <li>Docker para herramientas</li>
                          </ul>
                        </div>
                      </div>
                    </div>
                  </div>
                </CyberPanel>
              </motion.div>

              <motion.div variants={sv(fadeIn)} initial="hidden" animate="visible">
                <CyberPanel title={t('docs.fileStructureTitle')}>
                  <pre className="overflow-x-auto rounded-lg bg-[hsl(var(--muted))]/40 p-4 font-mono text-sm text-foreground">
{`securescan-pro/
├── app/                    # Next.js 16 App Router
│   ├── page.tsx           # Landing page
│   ├── scanner/           # Scanner principal
│   ├── history/           # Historial de scans
│   ├── lab/               # Laboratorio Docker
│   └── docs/              # Documentacion
├── components/            # Componentes React
│   ├── ui/               # shadcn/ui
│   ├── header.tsx
│   ├── scan-form.tsx
│   ├── scan-progress.tsx
│   └── results-dashboard.tsx
├── lib/                   # Utilidades
│   └── scan-context.tsx  # Estado global
├── server/                # Backend Python
│   ├── app.py            # Flask API
│   ├── modules/          # Herramientas
│   │   ├── wappalyzer.py
│   │   ├── nmap_scanner.py
│   │   ├── patator.py
│   │   ├── metasploit.py
│   │   ├── ffuf.py
│   │   ├── gobuster.py
│   │   ├── zap_scanner.py
│   │   ├── nuclei.py
│   │   ├── sqlmap_scanner.py
│   │   └── searchsploit.py
│   └── utils/
│       ├── scoring.py    # CVSS/EPSS
│       └── reporter.py   # Generacion de reportes
└── docker-compose.yml     # Servicios Docker`}
                  </pre>
                </CyberPanel>
              </motion.div>
            </TabsContent>
          </Tabs>

          <motion.div
            className="flex items-center justify-center gap-4 py-8"
            variants={sv(fadeIn)}
            initial="hidden"
            animate="visible"
          >
            <CyberButton variant="primary" asChild icon={<Shield className="h-4 w-4" />}>
              <Link href="/scanner">
                {t('docs.goToScanner')}
              </Link>
            </CyberButton>
            <CyberButton variant="outline" asChild>
              <Link href="/lab">
                {t('docs.configureLab')}
              </Link>
            </CyberButton>
          </motion.div>
        </div>
      </main>
    </div>
  )
}
