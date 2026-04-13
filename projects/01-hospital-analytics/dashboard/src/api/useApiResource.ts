import { useEffect, useState } from "react";

interface ResourceState<T> {
  data: T | null;
  error: string | null;
  isLoading: boolean;
}

export function useApiResource<T>(loadResource: () => Promise<T>): ResourceState<T> {
  const [state, setState] = useState<ResourceState<T>>({
    data: null,
    error: null,
    isLoading: true,
  });

  useEffect(() => {
    let isMounted = true;

    setState({ data: null, error: null, isLoading: true });

    loadResource()
      .then((data) => {
        if (isMounted) {
          setState({ data, error: null, isLoading: false });
        }
      })
      .catch((error: unknown) => {
        if (isMounted) {
          const message =
            error instanceof Error
              ? error.message
              : "Unable to load this dashboard section.";
          setState({ data: null, error: message, isLoading: false });
        }
      });

    return () => {
      isMounted = false;
    };
  }, [loadResource]);

  return state;
}

