import * as React from 'react'
import { Tabs as TabsPrimitive } from '@base-ui/react/tabs'
import { cn } from '../../lib/utils'
import './coss-ui.css'

export const Tabs = TabsPrimitive.Root

export function TabsList({ className, ...props }) {
  return (
    <TabsPrimitive.List
      className={cn('coss-tabs-list', className)}
      data-slot="tabs-list"
      {...props}
    />
  )
}

export function TabsTab({ className, ...props }) {
  return (
    <TabsPrimitive.Tab
      className={cn('coss-tabs-tab', className)}
      data-slot="tabs-tab"
      {...props}
    />
  )
}

export function TabsPanel({ className, ...props }) {
  return (
    <TabsPrimitive.Panel
      className={cn('coss-tabs-panel', className)}
      data-slot="tabs-panel"
      {...props}
    />
  )
}
