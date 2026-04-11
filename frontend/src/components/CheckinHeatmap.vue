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
  month: string;
  values: CheckinValue[];
}>();

const chartRef = ref<HTMLDivElement | null>(null);
let chart: echarts.ECharts | null = null;
let resizeObserver: ResizeObserver | null = null;

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
      formatter: (params: any) => {
        const [date, count] = params.value as [string, number];
        return `${date}<br/>AC: ${count}`;
      }
    },
    visualMap: {
      min: 0,
      max: maxCount,
      calculable: false,
      orient: "horizontal",
      left: "center",
      bottom: 0,
      inRange: {
        color: ["#ecfdf3", "#86efac", "#22c55e", "#15803d"]
      },
      text: ["More", "Less"]
    },
    calendar: {
      top: 24,
      left: 20,
      right: 20,
      cellSize: ["auto", 18],
      range: props.month,
      itemStyle: {
        borderWidth: 1,
        borderColor: "#d9dee7"
      },
      splitLine: {
        show: false
      },
      dayLabel: {
        firstDay: 1,
        nameMap: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
      },
      monthLabel: {
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
  () => [props.month, props.values],
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
  min-height: 260px;
}
</style>
