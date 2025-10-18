import { useEffect, useMemo, useRef, useState } from 'react'
import { buildWsUrl } from '../api/client'

type Message = {
  id: string
  sender: 'bot' | 'user' | 'system'
  content: string
}

export default function ChatWidget({ open, onClose, wsPath, initialStatus }: { open: boolean; onClose: () => void; wsPath?: string; initialStatus?: string }) {
  const [messages, setMessages] = useState<Message[]>([])
  const [value, setValue] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)
  const wsRef = useRef<WebSocket | null>(null)

  useEffect(() => {
    if (!open) {
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) wsRef.current.close()
      wsRef.current = null
      setMessages([])
      return
    }
    if (!wsPath) {
      const text = initialStatus || 'Идёт оценка портфолио…'
      setMessages([{ id: 'm0', sender: 'system', content: text }])
      setIsTyping(true)
      return
    }
    const url = buildWsUrl(wsPath)
    const ws = new WebSocket(url)
    wsRef.current = ws

    ws.onopen = () => {
      setMessages([{ id: 'm0', sender: 'system', content: 'Чат подключён. Ожидайте сообщения бота…' }])
      setIsTyping(true)
    }
    ws.onmessage = (ev) => {
      try {
        const data = JSON.parse(ev.data)
        if (data.type === 'welcome') {
          const base: Message = { id: crypto.randomUUID(), sender: 'system', content: 'Спасибо за отклик! Сессия создана.' }
          const extras: Message[] = Array.isArray(data.mismatches) && data.mismatches.length > 0
            ? [{ id: crypto.randomUUID(), sender: 'system', content: `Несоответствия: ${data.mismatches.join(', ')}` }]
            : []
          setMessages((prev) => [...prev, base, ...extras])
        } else if (data.type === 'analysis_status') {
          const msg: Message = { id: crypto.randomUUID(), sender: 'system', content: (data.message as string) || 'Идёт оценка портфолио…' }
          setMessages((prev) => [...prev, msg])
        } else if (data.type === 'bot_typing') {
          setIsTyping(!!data.value)
        } else if (data.type === 'question') {
          const msg: Message = { id: crypto.randomUUID(), sender: 'bot', content: data.text }
          setMessages((prev) => [...prev, msg])
          setIsTyping(false)
        } else if (data.type === 'analysis_update') {
          const content = typeof data.message === 'string' && data.message.trim().length > 0
            ? data.message
            : (typeof data.score !== 'undefined' ? `Обновлённый скор: ${data.score}` : 'Спасибо, учёл ваш ответ.')
          const msg: Message = { id: crypto.randomUUID(), sender: 'system', content }
          setMessages((prev) => [...prev, msg])
          setIsTyping(false)
        } else if (data.type === 'final_summary') {
          const content = typeof data.message === 'string' && data.message.trim().length > 0
            ? data.message
            : (typeof data.summary_text === 'string' && data.summary_text.trim().length > 0
              ? `Итог: ${data.summary_text}`
              : 'Спасибо! Мы передадим ваши ответы рекрутеру.')
          const msg: Message = { id: crypto.randomUUID(), sender: 'system', content }
          setMessages((prev) => [...prev, msg])
          setIsTyping(false)
        } else if (data.type === 'error') {
          const msg: Message = { id: crypto.randomUUID(), sender: 'system', content: `Ошибка: ${data.message}` }
          setMessages((prev) => [...prev, msg])
          setIsTyping(false)
        }
      } catch (err) {
      }
    }
    ws.onclose = () => {
      setMessages((prev) => [...prev, { id: crypto.randomUUID(), sender: 'system', content: 'Соединение закрыто.' }])
    }

    return () => {
      ws.close()
      wsRef.current = null
    }
  }, [open, wsPath])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const canSend = useMemo(() => value.trim().length > 0 && !isTyping, [value, isTyping])

  const send = () => {
    if (!canSend) return
    const text = value.trim()
    setValue('')
    setMessages((prev) => [...prev, { id: crypto.randomUUID(), sender: 'user', content: text }])
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: 'answer', text }))
    }
  }

  if (!open) return null

  return (
    <div className="fixed bottom-5 right-5 w-[380px] h-[520px] rounded-xl shadow-2xl bg-white flex flex-col overflow-hidden">
      <div className="flex items-center justify-between px-3 py-2 bg-gradient-to-r from-blue-600 to-sky-500 text-white">
        <div className="text-sm font-semibold">SmartBot</div>
        <div className="flex items-center gap-2">
          <span className="text-xs bg-green-500/90 px-2 py-0.5 rounded">Онлайн</span>
          <button onClick={onClose} aria-label="Закрыть" className="w-7 h-7 rounded hover:bg-white/20">
            ×
          </button>
        </div>
      </div>
      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {messages.map((m) => (
          <div key={m.id} className={`flex ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[85%] rounded-xl px-3 py-2 text-sm ${m.sender === 'user' ? 'bg-blue-50' : m.sender === 'system' ? 'bg-gray-100 italic text-gray-700' : 'bg-gray-100'}`}>
              {m.content}
            </div>
          </div>
        ))}
        {isTyping && (
          <div className="flex justify-start">
            <div className="max-w-[85%] rounded-xl px-3 py-2 text-sm bg-gray-100 text-gray-700 italic">печатает…</div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>
      <div className="p-3 space-y-2 border-t">
        <textarea
          placeholder="Напишите ответ…"
          value={value}
          onChange={(e) => setValue(e.currentTarget.value)}
          rows={3}
          className="w-full border rounded-md p-2 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          onClick={send}
          disabled={!canSend}
          className="bg-blue-600 text-white px-3 py-1.5 rounded disabled:opacity-50 hover:bg-blue-700"
        >
          Отправить
        </button>
      </div>
    </div>
  )
}
