import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

export interface ErrorStateProps {
  title?: string;
  message?: string;
  onRetry?: () => void;
  className?: string;
}

/** Reusable error message with an optional retry action. */
export function ErrorState({ title = 'Something went wrong', message = 'Please try again.', onRetry, className }: ErrorStateProps) {
  return (
    <Alert variant="destructive" role="alert" className={cn(className)}>
      <AlertTitle>{title}</AlertTitle>
      <AlertDescription>{message}</AlertDescription>
      {onRetry ? (
        <Button variant="outline" size="sm" className="mt-3" onClick={onRetry}>
          Try again
        </Button>
      ) : null}
    </Alert>
  );
}
