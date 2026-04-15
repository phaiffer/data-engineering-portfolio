import { useEffect, useState } from "react";
import { apiClient } from "../services/api";
import type {
  DashboardData,
  SectionResource,
} from "../types/api";

const loadingResource = <T,>(): SectionResource<T> => ({
  data: null,
  error: null,
  isLoading: true,
});

const emptyDashboardData = (): DashboardData => ({
  health: loadingResource(),
  kpis: loadingResource(),
  dailyRevenue: loadingResource(),
  categoryPerformance: loadingResource(),
  sellerPerformance: loadingResource(),
  customerStatePerformance: loadingResource(),
  orderStatusSummary: loadingResource(),
  paymentTypeSummary: loadingResource(),
});

async function toResource<T>(loader: () => Promise<T>): Promise<SectionResource<T>> {
  try {
    return {
      data: await loader(),
      error: null,
      isLoading: false,
    };
  } catch (error) {
    return {
      data: null,
      error: error instanceof Error ? error.message : "Unable to load data.",
      isLoading: false,
    };
  }
}

export function useDashboardData(topN: number, dailyOrderStatus: string, refreshKey: number) {
  const [state, setState] = useState<DashboardData>(() => emptyDashboardData());

  useEffect(() => {
    let isCurrent = true;

    setState(emptyDashboardData());

    Promise.all([
      toResource(apiClient.getHealth),
      toResource(apiClient.getKpis),
      toResource(() => apiClient.getDailyRevenue(180, dailyOrderStatus || undefined)),
      toResource(() => apiClient.getCategoryPerformance(topN)),
      toResource(() => apiClient.getSellerPerformance(topN)),
      toResource(() => apiClient.getCustomerStatePerformance(topN)),
      toResource(apiClient.getOrderStatusSummary),
      toResource(apiClient.getPaymentTypeSummary),
    ]).then(
      ([
        health,
        kpis,
        dailyRevenue,
        categoryPerformance,
        sellerPerformance,
        customerStatePerformance,
        orderStatusSummary,
        paymentTypeSummary,
      ]) => {
        if (!isCurrent) {
          return;
        }

        setState({
          health,
          kpis,
          dailyRevenue,
          categoryPerformance,
          sellerPerformance,
          customerStatePerformance,
          orderStatusSummary,
          paymentTypeSummary,
        });
      },
    );

    return () => {
      isCurrent = false;
    };
  }, [topN, dailyOrderStatus, refreshKey]);

  return state;
}
