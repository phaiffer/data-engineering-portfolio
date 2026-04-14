import { useEffect, useState } from "react";

export type ResourceState<T> = {
  data: T | null;
  error: string | null;
  isLoading: boolean;
};

export function useApiResource<T>(loader: () => Promise<T>): ResourceState<T> {
  const [state, setState] = useState<ResourceState<T>>({
    data: null,
    error: null,
    isLoading: true,
  });

  useEffect(() => {
    let isCurrent = true;

    setState({ data: null, error: null, isLoading: true });
    loader()
      .then((data) => {
        if (isCurrent) {
          setState({ data, error: null, isLoading: false });
        }
      })
      .catch((error: unknown) => {
        if (isCurrent) {
          setState({
            data: null,
            error: error instanceof Error ? error.message : "Unable to load data.",
            isLoading: false,
          });
        }
      });

    return () => {
      isCurrent = false;
    };
  }, [loader]);

  return state;
}
