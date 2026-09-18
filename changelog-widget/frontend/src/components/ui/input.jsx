import * as React from 'react'
import { cn } from '../../lib/utils'
import './coss-ui.css'

export const Input = React.forwardRef(function Input({ className, type = 'text', ...props }, ref) {
  return (
    <input
      type={type}
      className={cn('coss-input', className)}
      ref={ref}
      data-slot="input"
      {...props}
    />
  )
})
