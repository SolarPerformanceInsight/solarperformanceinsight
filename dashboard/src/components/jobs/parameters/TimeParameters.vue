<template>
  <div class="time-parameters">
    <h3>Time Parameters</h3>
    <p>Tell us about the time index of your data files.</p>
    <div class="timefield">
      <label for="timezoneSelect"><b>Timezone:</b></label>
      <select
        @change="emitParams"
        v-model="timezone"
        class="timezone"
        name="timezoneSelect"
      >
        <option v-for="tz in timezoneList" :key="tz">{{ tz }}</option>
      </select>
    </div>
    <div class="timefield">
      <b>Time between data points in minutes:</b>
      <input
        @change="emitParams"
        style="width: 50px"
        v-model.number="step"
        type="number"
        min="1"
        max="60"
        step="1"
      />
    </div>
    <div class="timefield">
      <b>Start:</b>
      <datetime
        @close="emitParams"
        placeholder="Click here to set start date"
        type="datetime"
        v-model="start"
        format="y-LL-dd HH:mmZZ"
        :zone="timezone"
        :picker-zone="timezone"
        :max-datetime="end"
      ></datetime>
    </div>
    <div class="timefield">
      <b>End:</b>
      <datetime
        @close="emitParams"
        type="datetime"
        placeholder="Click here to set start date"
        v-model="end"
        :zone="timezone"
        :picker-zone="timezone"
        :min-datetime="start"
        format="y-LL-dd HH:mmZZ"
      ></datetime>
    </div>
  </div>
</template>
<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import Timezones from "@/constants/timezones.json";
import { LocalZone } from "luxon";
import { Datetime as DatePicker } from "vue-datetime";
import "vue-datetime/dist/vue-datetime.css";

Vue.component("datetime", DatePicker);

@Component
export default class JobTimeParameters extends Vue {
  start!: string;
  end!: string;
  timezone!: string;
  step!: number;
  timezoneList: Array<string> = Timezones;

  data() {
    const zone = new LocalZone().name;
    return {
      start: null,
      end: null,
      step: 60,
      timezone: zone
    };
  }
  mounted() {
    this.emitParams();
  }
  emitParams() {
    const timeParams = {
      start: this.start,
      end: this.end,
      step: this.step * 60,
      timezone: this.timezone
    };
    this.$emit("new-timeparams", timeParams);
  }
}
</script>
<style scoped>
.vdatetime {
  display: inline-block;
}
</style>
