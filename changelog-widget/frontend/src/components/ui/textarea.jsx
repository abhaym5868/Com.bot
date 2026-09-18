import * as React from 'react'
import { cn } from '../../lib/utils'
import './coss-ui.css'

export const Textarea = React.forwardRef(function Textarea({ className, ...props }, ref) {
  return (
    <textarea
      className={cn('coss-textarea', className)}
      ref={ref}
      data-slot="textarea"
      {...props}
    />
  )
})
