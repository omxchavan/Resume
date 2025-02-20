import type React from "react"
import { Inter } from "next/font/google"
import { Toaster } from "sonner"

import { AuthProvider } from "@/components/providers/auth-provider"
import Navbar from "@/components/common/navbar"
import "./globals.css"

const inter = Inter({ subsets: ["latin"] })

export const metadata = {
  title: "JobMatch",
  description: "AI-powered job matching platform",
    generator: 'v0.dev'
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <AuthProvider>
          <Navbar />
          {children}
          <Toaster />
        </AuthProvider>
      </body>
    </html>
  )
}



import './globals.css'