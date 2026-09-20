import * as React from 'react'
import { Select as SelectPrimitive } from '@base-ui/react/select'
import { cn } from '../../lib/utils'
import './coss-ui.css'

export const SelectRoot = SelectPrimitive.Root
export const SelectTrigger = SelectPrimitive.Trigger
export const SelectValue = SelectPrimitive.Value
export const SelectPortal = SelectPrimitive.Portal
export const SelectPositioner = SelectPrimitive.Positioner
export const SelectPopup = SelectPrimitive.Popup
export const SelectItem = SelectPrimitive.Item
export const SelectItemText = SelectPrimitive.ItemText
export const SelectItemIndicator = SelectPrimitive.ItemIndicator

/**
 * Coss UI Select primitive component
 * Compliant with Coss UI style system.
 */
export const Select = React.forwardRef(function Select(
  { className, children, ...props },
  ref
) {
  return (
    <select
      ref={ref}
      className={cn('coss-select', className)}
      data-slot="select"
      {...props}
    >
      {children}
    </select>
  )
})
