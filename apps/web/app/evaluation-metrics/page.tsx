import { redirect } from "next/navigation";

export default function MetricsPage() {
  redirect("/internal/evaluation-metrics");
}
