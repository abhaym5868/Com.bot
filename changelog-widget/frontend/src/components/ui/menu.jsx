import * as React from 'react'
import { Menu as MenuPrimitive } from '@base-ui/react/menu'
import { cn } from '../../lib/utils'
import './coss-ui.css'

export const Menu = MenuPrimitive.Root
export const MenuTrigger = MenuPrimitive.Trigger
export const MenuPortal = MenuPrimitive.Portal
export const MenuGroup = MenuPrimitive.Group

export function MenuPopup({ className, children, sideOffset = 6, ...props }) {
  return (
    <MenuPortal>
      <MenuPrimitive.Positioner sideOffset={sideOffset}>
        <MenuPrimitive.Popup
          className={cn('coss-menu-popup', className)}
          data-slot="menu-popup"
          {...props}
        >
          {children}
        </MenuPrimitive.Popup>
      </MenuPrimitive.Positioner>
    </MenuPortal>
  )
}

export function MenuItem({ className, variant = 'default', children, ...props }) {
  return (
    <MenuPrimitive.Item
      className={cn(
        'coss-menu-item',
        variant === 'destructive' && 'coss-menu-item-danger',
        className
      )}
      data-slot="menu-item"
      {...props}
    >
      {children}
    </MenuPrimitive.Item>
  )
}

export function MenuSeparator({ className, ...props }) {
  return (
    <MenuPrimitive.Separator
      className={cn('coss-menu-separator', className)}
      data-slot="menu-separator"
      {...props}
    />
  )
}
