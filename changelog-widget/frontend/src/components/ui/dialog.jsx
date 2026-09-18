import * as React from 'react'
import { Dialog as DialogPrimitive } from '@base-ui/react/dialog'
import { cn } from '../../lib/utils'
import './coss-ui.css'

export const Dialog = DialogPrimitive.Root
export const DialogTrigger = DialogPrimitive.Trigger
export const DialogPortal = DialogPrimitive.Portal
export const DialogClose = DialogPrimitive.Close

export function DialogBackdrop({ className, ...props }) {
  return (
    <DialogPrimitive.Backdrop
      className={cn('coss-dialog-backdrop', className)}
      data-slot="dialog-backdrop"
      {...props}
    />
  )
}

export function DialogPopup({ className, children, ...props }) {
  return (
    <DialogPortal>
      <DialogBackdrop />
      <div className="coss-dialog-viewport">
        <DialogPrimitive.Popup
          className={cn('coss-dialog-popup', className)}
          data-slot="dialog-popup"
          {...props}
        >
          {children}
        </DialogPrimitive.Popup>
      </div>
    </DialogPortal>
  )
}

export function DialogHeader({ className, ...props }) {
  return <div className={cn('coss-dialog-header', className)} data-slot="dialog-header" {...props} />
}

export function DialogTitle({ className, ...props }) {
  return (
    <DialogPrimitive.Title
      className={cn('coss-dialog-title', className)}
      data-slot="dialog-title"
      {...props}
    />
  )
}

export function DialogDescription({ className, ...props }) {
  return (
    <DialogPrimitive.Description
      className={cn('coss-dialog-description', className)}
      data-slot="dialog-description"
      {...props}
    />
  )
}

export function DialogBody({ className, ...props }) {
  return <div className={cn('coss-dialog-body', className)} data-slot="dialog-body" {...props} />
}

export function DialogFooter({ className, ...props }) {
  return <div className={cn('coss-dialog-footer', className)} data-slot="dialog-footer" {...props} />
}
