import * as React from 'react'
import { cn } from '../../lib/utils'
import './coss-ui.css'

export function Kbd({ className, children, ...props }) {
  return (
    <kbd className={cn('coss-kbd', className)} data-slot="kbd" {...props}>
      {children}
    </kbd>
  )
}
