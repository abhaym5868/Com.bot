import * as React from 'react'
import { cva } from 'class-variance-authority'
import { cn } from '../../lib/utils'
import './coss-ui.css'

export const badgeVariants = cva('coss-badge', {
  variants: {
    variant: {
      default: 'coss-badge-default',
      secondary: 'coss-badge-secondary',
      outline: 'coss-badge-outline',
      success: 'coss-badge-success',
      destructive: 'coss-badge-destructive',
      warning: 'coss-badge-warning',
    },
  },
  defaultVariants: {
    variant: 'default',
  },
})

export function Badge({ className, variant, children, ...props }) {
  return (
    <span className={cn(badgeVariants({ variant }), className)} data-slot="badge" {...props}>
      {children}
    </span>
  )
}
