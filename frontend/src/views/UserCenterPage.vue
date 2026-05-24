<template>
  <main class="page page-stack">
    <section class="page-card">
      <div class="page-card__body">
        <p class="page-kicker">个人中心</p>
        <h1 class="page-title">我的练习</h1>
        <p class="page-description">查看账号信息和全年 AC 记录。</p>
      </div>
    </section>

    <div class="user-grid">
      <section class="page-card">
        <div class="page-card__body profile-card__body">
          <div class="section-block__head">
            <h2 class="section-title">账号信息</h2>
            <p class="section-description">当前登录账号。</p>
          </div>

          <div class="profile-list">
            <div class="profile-item">
              <span>用户 ID</span>
              <strong>{{ user.id ?? "-" }}</strong>
            </div>
            <div class="profile-item">
              <span>用户名</span>
              <strong>{{ user.username }}</strong>
            </div>
            <div class="profile-item">
              <span>登录状态</span>
              <strong>已登录</strong>
            </div>
          </div>
        </div>
      </section>

      <section class="page-card">
        <div class="page-card__body heatmap-card__body">
          <div class="heatmap-head">
            <div class="section-block__head">
              <h2 class="section-title">AC 打卡热力图</h2>
              <p class="section-description">
                {{ selectedYear }} 年共有 {{ checkinStats.year_active_days }} 天获得至少一次 AC。
              </p>
            </div>

            <div class="year-toolbar">
              <span class="year-toolbar__label">年份</span>
              <el-select v-model="selectedYear" class="year-select" @change="handleYearChange">
                <el-option
                  v-for="year in yearOptions"
                  :key="year"
                  :label="`${year} 年`"
                  :value="year"
                />
              </el-select>
            </div>
          </div>

          <CheckinHeatmap :year="selectedYear" :values="checkins.values" />

          <div class="checkin-stats">
            <div class="checkin-stat">
              <strong>{{ checkinStats.total_active_days }}</strong>
              <span>累计打卡天数</span>
            </div>
            <div class="checkin-stat">
              <strong>{{ checkinStats.year_active_days }}</strong>
              <span>本年打卡天数</span>
            </div>
            <div class="checkin-stat">
              <strong>{{ checkinStats.last_30_days_active_days }}</strong>
              <span>近 30 天打卡</span>
            </div>
            <div class="checkin-stat">
              <strong>{{ checkinStats.max_streak_days }}</strong>
              <span>最长连续打卡</span>
            </div>
          </div>
        </div>
      </section>
    </div>
  </main>
</template>

<script setup lang="ts">
import { ElMessage } from "element-plus";
import { computed, onMounted, ref } from "vue";
import type { CheckinResponse } from "../api/users";
import { fetchCheckins } from "../api/users";
import CheckinHeatmap from "../components/CheckinHeatmap.vue";
import { useUserStore } from "../stores/user";

const user = useUserStore();
const currentYear = new Date().getFullYear();
const selectedYear = ref(currentYear);
const checkins = ref<CheckinResponse>({
  year: `${currentYear}`,
  available_years: [currentYear],
  values: [],
  stats: {
    total_active_days: 0,
    year_active_days: 0,
    last_30_days_active_days: 0,
    max_streak_days: 0
  }
});

const yearOptions = computed(() =>
  [...(checkins.value.available_years?.length ? checkins.value.available_years : [selectedYear.value])].sort(
    (left, right) => right - left
  )
);

const checkinStats = computed(() => ({
  total_active_days: checkins.value.stats?.total_active_days ?? 0,
  year_active_days: checkins.value.stats?.year_active_days ?? 0,
  last_30_days_active_days: checkins.value.stats?.last_30_days_active_days ?? 0,
  max_streak_days: checkins.value.stats?.max_streak_days ?? 0
}));

async function loadCheckins() {
  try {
    const response = await fetchCheckins({ year: selectedYear.value });
    checkins.value = {
      ...response,
      available_years:
        response.available_years && response.available_years.length > 0
          ? response.available_years
          : [selectedYear.value],
      stats: {
        total_active_days: response.stats?.total_active_days ?? 0,
        year_active_days: response.stats?.year_active_days ?? 0,
        last_30_days_active_days: response.stats?.last_30_days_active_days ?? 0,
        max_streak_days: response.stats?.max_streak_days ?? 0
      }
    };
    if (response.year) {
      selectedYear.value = Number(response.year);
    }
  } catch {
    ElMessage.error("加载失败，请稍后重试。");
  }
}

function handleYearChange() {
  void loadCheckins();
}

onMounted(async () => {
  await user.ensureLoaded();
  await loadCheckins();
});
</script>

<style scoped>
.user-grid {
  display: grid;
  grid-template-columns: minmax(280px, 340px) minmax(0, 1fr);
  gap: 20px;
}

.profile-card__body,
.heatmap-card__body {
  display: grid;
  gap: 18px;
}

.section-block__head {
  display: grid;
  gap: 2px;
}

.profile-list {
  display: grid;
  gap: 12px;
}

.profile-item {
  display: grid;
  gap: 8px;
  padding: 16px;
  border: 1px solid var(--oj-border);
  border-radius: 8px;
  background: var(--oj-surface-soft);
}

.profile-item span {
  color: var(--oj-muted);
  font-size: 13px;
}

.profile-item strong {
  color: var(--oj-text);
  font-size: 16px;
}

.heatmap-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.year-toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
}

.year-toolbar__label {
  color: var(--oj-muted);
  font-size: 13px;
}

.year-select {
  width: 132px;
}

.checkin-stats {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.checkin-stat {
  display: grid;
  gap: 6px;
  padding: 16px;
  border: 1px solid var(--oj-border);
  border-radius: 8px;
  background: var(--oj-surface-soft);
}

.checkin-stat strong {
  color: var(--oj-text);
  font-size: 30px;
  line-height: 1;
}

.checkin-stat span {
  color: var(--oj-muted);
  font-size: 13px;
}

@media (max-width: 980px) {
  .user-grid {
    grid-template-columns: 1fr;
  }

  .checkin-stats {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 760px) {
  .heatmap-head {
    flex-direction: column;
  }

  .year-toolbar {
    flex-wrap: wrap;
  }

  .checkin-stats {
    grid-template-columns: 1fr;
  }
}
</style>
