"use client"

import * as React from "react"
import { ThemeProvider as NextThemesProvider } from "next-themes"
// この行は不要なので削除します
// import { type ThemeProviderProps } from "next-themes/dist/types"

// Reactの機能を使って、インポートしたコンポーネントから直接Propsの型を推論します
type ThemeProviderProps = React.ComponentProps<typeof NextThemesProvider>

export function ThemeProvider({ children, ...props }: ThemeProviderProps) {
  return <NextThemesProvider {...props}>{children}</NextThemesProvider>
}

