import { mergeProps } from '@base-ui/react/merge-props'
import { useRender } from '@base-ui/react/use-render'
import { cn } from '../../lib/utils'
import './coss-ui.css'

export function Card({ className, render, ...props }) {
  const defaultProps = {
    className: cn('coss-card', className),
    'data-slot': 'card',
  }
  return useRender({
    defaultTagName: 'div',
    props: mergeProps(defaultProps, props),
    render,
  })
}

export function CardHeader({ className, render, ...props }) {
  const defaultProps = {
    className: cn('coss-card-header', className),
    'data-slot': 'card-header',
  }
  return useRender({
    defaultTagName: 'div',
    props: mergeProps(defaultProps, props),
    render,
  })
}

export function CardTitle({ className, render, ...props }) {
  const defaultProps = {
    className: cn('coss-card-title', className),
    'data-slot': 'card-title',
  }
  return useRender({
    defaultTagName: 'h3',
    props: mergeProps(defaultProps, props),
    render,
  })
}

export function CardDescription({ className, render, ...props }) {
  const defaultProps = {
    className: cn('coss-card-description', className),
    'data-slot': 'card-description',
  }
  return useRender({
    defaultTagName: 'p',
    props: mergeProps(defaultProps, props),
    render,
  })
}

export function CardContent({ className, render, ...props }) {
  const defaultProps = {
    className: cn('coss-card-content', className),
    'data-slot': 'card-content',
  }
  return useRender({
    defaultTagName: 'div',
    props: mergeProps(defaultProps, props),
    render,
  })
}

export function CardFooter({ className, render, ...props }) {
  const defaultProps = {
    className: cn('coss-card-footer', className),
    'data-slot': 'card-footer',
  }
  return useRender({
    defaultTagName: 'div',
    props: mergeProps(defaultProps, props),
    render,
  })
}
