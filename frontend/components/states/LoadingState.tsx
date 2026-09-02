import { Skeleton } from '@/components/ui/skeleton';
import { cn } from '@/lib/utils';

export interface LoadingStateProps {
  /** Announced to screen readers while content is loading. */
  label?: string;
  /** Number of skeleton rows to show. */
  rows?: number;
  className?: string;
}

/**
 * Reusable loading placeholder. Renders a small skeleton block sized for a
 * page/section (not a full-screen spinner), so surrounding layout doesn't
 * jump once real content arrives.
 */
export function LoadingState({ label = 'Loading', rows = 3, className }: LoadingStateProps) {
  return (
    <div role="status" aria-live="polite" aria-busy="true" className={cn('w-full space-y-3', className)}>
      <span className="sr-only">{label}</span>
      {Array.from({ length: rows }).map((_, index) => (
        <Skeleton key={index} className="h-4 w-full first:w-2/3" />
      ))}
    </div>
  );
}
