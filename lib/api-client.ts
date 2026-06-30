// lib/api-client.ts
//
// CORRECCIONES APLICADAS:
//   1. SecurityScore: interface completa con todos los campos que devuelve
//      scoring.py (gradeDescription, percentages, exploitImpact, metrics,
//      recommendations, riskLevel). Ya no se pierden datos del backend.
//   2. Grade: tipo expandido para incluir A+, A-, B+, B-, C+, C-, D+.
//   3. RiskLevel: tipo nuevo exportado.
//   4. getScanResults(): el comentario aclaraba que llama a /status; ahora
//      también se exporta el tipo correcto de retorno.

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000'
const API_TOKEN   = process.env.NEXT_PUBLIC_API_TOKEN || ''

// Configuración de retries
const DEFAULT_RETRIES = 3
const RETRY_DELAY = 1000 // ms

interface ApiError {
  error: string
  reason?: string
  allowed_targets?: string[]
}

interface ApiResponse<T> {
  data?: T
  error?: ApiError
}

// ── Tipos de Scan ──────────────────────────────────────────────────────────

// FIX: Tipos completos para circuit_breaker, dry_run, target_validation, retry_config
interface CircuitBreakerConfig {
  enabled?: boolean
  failure_threshold?: number   // fallos antes de abrir el circuito (default 3)
  recovery_timeout?: number    // segundos antes de reintentar (default 60)
}

interface TargetValidationConfig {
  check_dns?: boolean          // verificar resolución DNS (default true)
  check_reachability?: boolean // verificar que el host responde (default true)
  timeout?: number             // segundos para el check (default 10)
}

interface RetryConfig {
  max_retries?: number         // reintentos por herramienta (default 2)
  backoff_factor?: number      // multiplicador de espera entre reintentos (default 1.5)
  retry_on?: string[]          // tipos de error que activan reintento
}

interface ScanStartRequest {
  target: string
  options?: {
    tools?: {
      wappalyzer?: boolean
      nmap?: boolean
      gobuster?: boolean
      zap?: boolean
      searchsploit?: boolean
      metasploit?: boolean
      nuclei?: boolean
      sqlmap?: boolean
      patator?: boolean
      ffuf?: boolean
    }
    parallel?: boolean
    dry_run?: boolean              // simular sin ejecutar herramientas reales
    circuit_breaker?: CircuitBreakerConfig
    target_validation?: TargetValidationConfig
    retry_config?: RetryConfig
  }
}

interface ScanStartResponse {
  jobId: string
  status: 'running' | 'pending'
}

interface ScanStep {
  name: string
  status: 'pending' | 'running' | 'completed' | 'error'
  progress: number
  startTime?: number
  endTime?: number
}

// CORRECCIÓN #2: Grade expandido con todas las variantes que devuelve
// calculate_grade() en scoring.py.
type Grade = 'A+' | 'A' | 'A-' | 'B+' | 'B' | 'B-' | 'C+' | 'C' | 'C-' | 'D+' | 'D' | 'F'

// CORRECCIÓN #3: RiskLevel nuevo, alineado con get_risk_level() en scoring.py.
type RiskLevel = 'COMPROMETIDO' | 'EXPUESTO' | 'VULNERABLE' | 'PROTEGIDO' | 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'MINIMAL'

type SeverityBreakdown = {
  critical: number
  high: number
  medium: number
  low: number
  info: number
}

// CORRECCIÓN #1: SecurityScore con todos los campos del backend.
interface SecurityScore {
  total: number
  grade: Grade
  gradeDescription: string
  breakdown: SeverityBreakdown
  percentages: SeverityBreakdown
  exploitImpact: {
    totalExploits: number
    correlatedExploits: number
    penalty: number
  }
  metrics: {
    totalVulnerabilities: number
    totalExploits: number
    maxCvss: number
    criticalCount: number
    highCount: number
  }
  recommendations: string[]
  riskLevel: RiskLevel
}

interface Technology {
  name: string
  version?: string
  category?: string
  confidence?: number
  error?: string
}

interface Port {
  port?: number
  protocol?: string
  state?: string
  service?: string
  product?: string
  version?: string
  extrainfo?: string
  cpe?: string
  error?: string
}

interface Directory {
  path: string
  status: number
  size?: number
  type?: string
  error?: string
}

interface Vulnerability {
  id?: string
  name: string
  tool?: string
  url?: string
  risk?: 'critical' | 'high' | 'medium' | 'low' | 'info'
  severity?: string
  description?: string
  solution?: string
  cweid?: string
  evidence?: string
  cvss?: number
  error?: string
}

interface Exploit {
  id?: string | number
  type?: string
  platform?: string
  path?: string
  cve?: string
  title?: string
  severity?: string
  cvss?: number
  matchedTerm?: string
  exploit_url?: string
  error?: string
}

interface MetasploitFinding {
  title?: string
  severity?: 'critical' | 'high' | 'medium' | 'low' | 'info'
  cvss?: number
  description?: string
  module?: string
  host?: string
  port?: number
  protocol?: string
  source?: 'metasploit'
  matchedTerm?: string
  error?: string
}

interface ScanStatusResponse {
  id: string
  target: string
  status: 'running' | 'completed' | 'error'
  startTime: string
  endTime?: string
  error?: string
  steps: ScanStep[]
  technologies: Technology[]
  ports: Port[]
  directories: Directory[]
  vulnerabilities: Vulnerability[]
  exploits: Exploit[]
  metasploit: MetasploitFinding[]
  score: SecurityScore
}

interface ScanHistoryResponse {
  scans: ScanStatusResponse[]
  total: number
}

interface ConfigResponse {
  version: string
  allowed_targets: string[]
  available_tools: string[]
  report_formats: string[]
  metasploit?: {
    enabled: boolean
    mode: 'live' | 'simulation'
    host: string
    port: number
  }
}

interface HealthResponse {
  status: string
  version: string
  storage: 'connected' | 'fallback'
  zap_configured: boolean
  tools: string[]
}

// ── Error personalizado ────────────────────────────────────────────────────

export class ApiException extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public response?: ApiError
  ) {
    super(message)
    this.name = 'ApiException'
  }
}

// ── Helpers internos ───────────────────────────────────────────────────────

async function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms))
}

async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {},
  retries: number = DEFAULT_RETRIES
): Promise<ApiResponse<T>> {
  const url = `${API_BASE_URL}${endpoint}`

  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 30000) // 30 s timeout

      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...(API_TOKEN ? { 'X-API-Token': API_TOKEN } : {}),
          ...options.headers,
        },
        signal: controller.signal,
      })

      clearTimeout(timeoutId)

      if (!response.ok) {
        const errorData: ApiError = await response.json().catch(() => ({
          error: `HTTP ${response.status}: ${response.statusText}`
        }))

        // No reintentar en errores 4xx (cliente)
        if (response.status >= 400 && response.status < 500) {
          return { error: errorData }
        }

        throw new Error(errorData.error || `HTTP ${response.status}`)
      }

      const data = await response.json()
      return { data }

    } catch (err) {
      const isLastAttempt = attempt === retries

      if (err instanceof Error) {
        if (err.name === 'AbortError') {
          if (isLastAttempt) return { error: { error: 'Request timeout' } }
        } else if (isLastAttempt) {
          return { error: { error: err.message } }
        }
      }

      // Backoff exponencial antes de reintentar
      if (!isLastAttempt) {
        await sleep(RETRY_DELAY * Math.pow(2, attempt))
      }
    }
  }

  return { error: { error: 'Max retries exceeded' } }
}

// ── Funciones públicas de la API ───────────────────────────────────────────

/**
 * Obtiene la configuración pública y los targets permitidos.
 */
export async function getConfig(): Promise<ApiResponse<ConfigResponse>> {
  return apiRequest<ConfigResponse>('/api/config')
}

/**
 * Health-check liviano para indicadores de UI (ej. Header "Sistema: Online").
 * A diferencia de apiRequest(), usa timeout corto (4s) y SIN reintentos —
 * un polling cada pocos segundos no debe acumular llamadas colgadas ni
 * backoff exponencial si el backend está caído. Nunca lanza: devuelve
 * { data: undefined } en cualquier error de red/timeout.
 */
export async function getHealth(): Promise<ApiResponse<HealthResponse>> {
  try {
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 4000)
    const response = await fetch(`${API_BASE_URL}/api/health`, {
      signal: controller.signal,
    })
    clearTimeout(timeoutId)
    if (!response.ok) return { error: { error: `HTTP ${response.status}` } }
    const data = await response.json()
    return { data }
  } catch (err) {
    return { error: { error: err instanceof Error ? err.message : 'unreachable' } }
  }
}

/**
 * Inicia un nuevo escaneo de seguridad.
 */
export async function startScan(
  target: string,
  options: ScanStartRequest['options'] = {}
): Promise<ApiResponse<ScanStartResponse>> {
  if (!target.trim()) {
    return { error: { error: 'Target URL is required' } }
  }

  // FIX: Defaults explícitos para los 4 campos nuevos — evita KeyError en backend
  return apiRequest<ScanStartResponse>('/api/scan', {
    method: 'POST',
    body: JSON.stringify({
      target,
      options: {
        tools: {
          wappalyzer: true,
          nmap: true,
          gobuster: true,
          zap: true,
          searchsploit: true,
          metasploit: false,
          nuclei: true,
          sqlmap: false,
          patator: false,
          ffuf: true,
          ...options?.tools,
        },
        parallel: options?.parallel ?? true,
        dry_run: options?.dry_run ?? false,
        circuit_breaker: {
          enabled: true,
          failure_threshold: 3,
          recovery_timeout: 60,
          ...options?.circuit_breaker,
        },
        target_validation: {
          check_dns: true,
          check_reachability: true,
          timeout: 10,
          ...options?.target_validation,
        },
        retry_config: {
          max_retries: 2,
          backoff_factor: 1.5,
          retry_on: ['timeout', 'connection_error'],
          ...options?.retry_config,
        },
      },
    }),
  })
}

/**
 * Obtiene el estado y resultados de un escaneo por su ID.
 */
export async function getScanStatus(
  scanId: string
): Promise<ApiResponse<ScanStatusResponse>> {
  if (!scanId) {
    return { error: { error: 'Scan ID is required' } }
  }

  return apiRequest<ScanStatusResponse>(`/api/scan/${scanId}/status`)
}

/**
 * Alias para compatibilidad — el backend no tiene /results, usa /status.
 */
export async function getScanResults(
  scanId: string
): Promise<ApiResponse<ScanStatusResponse>> {
  return getScanStatus(scanId)
}

/**
 * Obtiene el historial de todos los escaneos.
 */
export async function getScanHistory(): Promise<ApiResponse<ScanHistoryResponse>> {
  return apiRequest<ScanHistoryResponse>('/api/history')
}

/**
 * Elimina un escaneo del historial.
 */
export async function deleteScan(
  scanId: string
): Promise<ApiResponse<{ message: string }>> {
  return apiRequest<{ message: string }>(`/api/scan/${scanId}`, {
    method: 'DELETE',
  })
}

/**
 * Descarga el reporte de un escaneo.
 * El endpoint devuelve un archivo binario, no JSON.
 */
export async function downloadReport(
  scanId: string,
  format: 'html' | 'json' | 'pdf' = 'html'
): Promise<{ blob?: Blob; error?: ApiError; filename?: string }> {
  try {
    const response = await fetch(
      `${API_BASE_URL}/api/scan/${scanId}/report?format=${format}`,
      {
        method: 'GET',
        headers: {
          ...(API_TOKEN ? { 'X-API-Token': API_TOKEN } : {}),
        },
      }
    )

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({
        error: 'Failed to generate report'
      }))
      return { error: errorData }
    }

    const blob = await response.blob()
    const filename = `security-report-${scanId}.${format}`

    return { blob, filename }

  } catch (err) {
    return {
      error: {
        error: err instanceof Error ? err.message : 'Network error'
      }
    }
  }
}

/**
 * Dispara la descarga del reporte en el navegador.
 */
export function triggerDownload(blob: Blob, filename: string): void {
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.style.display = 'none'
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  window.URL.revokeObjectURL(url)
  document.body.removeChild(a)
}

// ── Exports de tipos ───────────────────────────────────────────────────────

export type {
  Grade,
  RiskLevel,
  SeverityBreakdown,
  CircuitBreakerConfig,
  TargetValidationConfig,
  RetryConfig,
  ScanStartRequest,
  ScanStartResponse,
  ScanStatusResponse,
  ScanStep,
  SecurityScore,
  Technology,
  Port,
  Directory,
  Vulnerability,
  Exploit,
  MetasploitFinding,
  ScanHistoryResponse,
  ConfigResponse,
  HealthResponse,
}