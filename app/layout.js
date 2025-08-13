import './globals.css'

export const metadata = {
  title: 'Voice Dialogue Studio',
  description: 'Professional voice dialogue generation with AI-powered voice cloning',
  keywords: 'voice, dialogue, TTS, AI, Neuphonic, voice cloning, speech synthesis',
  authors: [{ name: 'Voice Dialogue Studio' }],
  creator: 'Voice Dialogue Studio',
  publisher: 'Voice Dialogue Studio',
  icons: {
    icon: '/favicon.ico',
    shortcut: '/favicon-16x16.png',
    apple: '/apple-touch-icon.png',
  },
  manifest: '/site.webmanifest',
}

export const viewport = {
  width: 'device-width',
  initialScale: 1,
  themeColor: '#2563eb',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en" className="h-full">
      <body className="h-full antialiased">
        <div className="min-h-full">
          {children}
        </div>
      </body>
    </html>
  )
} 