import * as React from 'react'
import { cn } from '../../lib/utils'
import './coss-ui.css'

export function Separator({ className, orientation = 'horizontal', ...props }) {
  return (
    <div
      role="separator"
      aria-orientation={orientation}
      className={cn(
        orientation === 'horizontal' ? 'coss-menu-separator' : 'w-px h-full bg-[var(--color-border)]',
        className
      )}
      data-slot="separator"
      {...props}
    />
  )
}
