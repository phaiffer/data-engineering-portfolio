import type { ReactNode } from "react";
import { EmptyState } from "./EmptyState";
import { ErrorState } from "./ErrorState";
import { LoadingState } from "./LoadingState";

export function SectionResource<T>({
  resource,
  emptyMessage,
  loadingMessage,
  children,
}: {
  resource: {
    data: T | null;
    error: string | null;
    isLoading: boolean;
  };
  emptyMessage: string;
  loadingMessage: string;
  children: (data: T) => ReactNode;
}) {
  if (resource.isLoading) {
    return <LoadingState message={loadingMessage} />;
  }

  if (resource.error) {
    return <ErrorState message={resource.error} />;
  }

  if (
    resource.data === null ||
    (Array.isArray(resource.data) && resource.data.length === 0)
  ) {
    return <EmptyState message={emptyMessage} />;
  }

  return <>{children(resource.data)}</>;
}
