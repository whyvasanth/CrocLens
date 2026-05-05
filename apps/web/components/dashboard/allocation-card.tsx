"use client";

import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
import { allocationData } from "@/lib/mock-dashboard-data";
import { Card, SectionTitle } from "@/components/dashboard/ui";

export function AllocationCard() {
  return (
    <Card>
      <SectionTitle eyebrow="Cross-asset view" title="Allocation mix" />
      <div className="h-52">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={allocationData}
              dataKey="value"
              nameKey="name"
              innerRadius={58}
              outerRadius={82}
              paddingAngle={3}
            >
              {allocationData.map((entry) => (
                <Cell key={entry.name} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip formatter={(value) => [`${value}%`, "Allocation"]} />
          </PieChart>
        </ResponsiveContainer>
      </div>
      <div className="mt-4 grid grid-cols-2 gap-3">
        {allocationData.map((item) => (
          <div key={item.name} className="flex min-w-0 items-center gap-2 text-sm">
            <span
              className="h-3 w-3 shrink-0 rounded-sm"
              style={{ backgroundColor: item.color }}
            />
            <span className="truncate text-stone-600">{item.name}</span>
            <span className="ml-auto font-semibold text-croc-ink">{item.value}%</span>
          </div>
        ))}
      </div>
    </Card>
  );
}

