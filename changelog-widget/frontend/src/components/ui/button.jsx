import * as React from 'react'
import { mergeProps } from '@base-ui/react/merge-props'
import { useRender } from '@base-ui/react/use-render'
import { cva } from 'class-variance-authority'
import { cn } from '../../lib/utils'
import './coss-ui.css'

export const buttonVariants = cva('coss-btn', {
  variants: {
    variant: {
      default: 'coss-btn-default',
      secondary: 'coss-btn-secondary',
      outline: 'coss-btn-outline',
      ghost: 'coss-btn-ghost',
      destructive: 'coss-btn-destructive',
      link: 'coss-btn-link',
    },
    size: {
      default: 'coss-btn-default-size',
      sm: 'coss-btn-sm',
      lg: 'coss-btn-lg',
      icon: 'coss-btn-icon',
      'icon-sm': 'coss-btn-icon-sm',
    },
  },
  defaultVariants: {
    variant: 'default',
    size: 'default',
  },
})

export const Button = React.forwardRef(function Button(
  { className, variant = 'default', size = 'default', render, children, loading = false, disabled, type = 'button', ...props },
  ref
) {
  const isDisabled = Boolean(loading || disabled)
  const defaultProps = {
    ref,
    children,
    className: cn(buttonVariants({ variant, size }), className),
    'aria-disabled': isDisabled || undefined,
    'data-loading': loading ? '' : undefined,
    'data-slot': 'button',
    disabled: isDisabled,
    type: render ? undefined : type,
  }

  return useRender({
    defaultTagName: 'button',
    props: mergeProps(defaultProps, props),
    render,
  })
})
