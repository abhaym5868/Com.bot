import * as React from 'react'
import { Dialog as DialogPrimitive } from '@base-ui/react/dialog'
import { cn } from '../../lib/utils'
import './coss-ui.css'

export const Sheet = DialogPrimitive.Root
export const SheetTrigger = DialogPrimitive.Trigger
export const SheetPortal = DialogPrimitive.Portal
export const SheetClose = DialogPrimitive.Close

export function SheetBackdrop({ className, ...props }) {
  return (
    <DialogPrimitive.Backdrop
      className={cn('coss-sheet-backdrop', className)}
      data-slot="sheet-backdrop"
      {...props}
    />
  )
}

export function SheetContent({ className, children, ...props }) {
  return (
    <SheetPortal>
      <SheetBackdrop />
      <DialogPrimitive.Popup
        className={cn('coss-sheet-content', className)}
        data-slot="sheet-content"
        {...props}
      >
        {children}
      </DialogPrimitive.Popup>
    </SheetPortal>
  )
}

export function SheetHeader({ className, ...props }) {
  return <div className={cn('coss-sheet-header', className)} data-slot="sheet-header" {...props} />
}

export function SheetTitle({ className, ...props }) {
  return (
    <DialogPrimitive.Title
      className={cn('coss-sheet-title', className)}
      data-slot="sheet-title"
      {...props}
    />
  )
}

export function SheetDescription({ className, ...props }) {
  return (
    <DialogPrimitive.Description
      className={cn('coss-sheet-description', className)}
      data-slot="sheet-description"
      {...props}
    />
  )
}

export function SheetBody({ className, ...props }) {
  return <div className={cn('coss-sheet-body', className)} data-slot="sheet-body" {...props} />
}
