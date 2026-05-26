<template>
  <div ref="chartRef" class="checkin-heatmap" />
</template>

<script setup lang="ts">
import * as echarts from "echarts/core";
import { CalendarComponent, TooltipComponent, VisualMapComponent } from "echarts/components";
import { HeatmapChart } from "echarts/charts";
import { CanvasRenderer } from "echarts/renderers";
import { onBeforeUnmount, onMounted, ref, watch } from "vue";
import type { CheckinValue } from "../api/users";

echarts.use([CalendarComponent, HeatmapChart, TooltipComponent, VisualMapComponent, CanvasRenderer]);

const props = defineProps<{
  year: string | number;
  values: CheckinValue[];
}>();

const chartRef = ref<HTMLDivElement | null>(null);
let chart: echarts.ECharts | null = null;
let resizeObserver: ResizeObserver | null = null;

function buildPieces(maxCount: number) {
  // 使用固定的绿色档位，AC 次数较少时热力图也能看出深浅差异。
  if (maxCount <= 1) {
    return [
      { value: 0, color: "#ebedf0" },
      { min: 1, color: "#2ea043" }
    ];
  }

  if (maxCount <= 3) {
    return [
      { value: 0, color: "#ebedf0" },
      { value: 1, color: "#9be9a8" },
      { value: 2, color: "#40c463" },
      { min: 3, color: "#216e39" }
    ];
  }

  return [
    { value: 0, color: "#ebedf0" },
    { value: 1, color: "#9be9a8" },
    { min: 2, max: 3, color: "#40c463" },
    { min: 4, max: 6, color: "#30a14e" },
    { min: 7, color: "#216e39" }
  ];
}

function renderChart() {
  if (!chartRef.value) {
    return;
  }

  if (!chart) {
    chart = echarts.init(chartRef.value);
  }

  const maxCount = Math.max(1, ...props.values.map((item) => item.count));
  chart.setOption({
    animation: false,
    tooltip: {
      trigger: "item",
      formatter: (params: { value?: [string, number]; data?: { value: [string, number] } }) => {
        const value = params.value ?? params.data?.value ?? ["", 0];
        const [date, count] = value;
        if (count > 0) {
          return `${date}<br/>AC 次数：${count}`;
        }
        return `${date}<br/>当天暂无 AC`;
      }
    },
    visualMap: {
      type: "piecewise",
      show: false,
      pieces: buildPieces(maxCount)
    },
    calendar: {
      // 使用 ECharts 日历坐标系实现类似贡献图的布局，不额外引入新图表库。
      top: 12,
      left: 8,
      right: 8,
      cellSize: ["auto", 16],
      range: `${props.year}`,
      itemStyle: {
        borderWidth: 1,
        borderColor: "#ffffff",
        color: "#ebedf0"
      },
      splitLine: {
        show: false
      },
      dayLabel: {
        firstDay: 1,
        margin: 10,
        nameMap: ["", "Mon", "", "Wed", "", "Fri", ""],
        color: "#64748b"
      },
      monthLabel: {
        margin: 10,
        color: "#475569"
      },
      yearLabel: {
        show: false
      }
    },
    series: [
      {
        type: "heatmap",
        coordinateSystem: "calendar",
        data: props.values.map((item) => [item.date, item.count])
      }
    ]
  });
  chart.resize();
}

onMounted(() => {
  renderChart();
  if (chartRef.value) {
    resizeObserver = new ResizeObserver(() => chart?.resize());
    resizeObserver.observe(chartRef.value);
  }
});

watch(
  () => [props.year, props.values],
  () => renderChart(),
  { deep: true }
);

onBeforeUnmount(() => {
  resizeObserver?.disconnect();
  chart?.dispose();
  chart = null;
});
</script>

<style scoped>
.checkin-heatmap {
  width: 100%;
  min-height: 220px;
}
</style>
