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
      <datetimefield @update-datetime="setStart" :timezone="timezone" />
    </div>
    <div class="timefield">
      <b>End:</b>
      <datetimefield @update-datetime="setEnd" :timezone="timezone" />
    </div>
    <div v-if="errors">
      <ul>
        <li v-for="(error, key) of errors" :key="key" class="warning-text">
          <b>{{ key }}:</b>
          {{ error }}
        </li>
      </ul>
    </div>
  </div>
</template>
<script lang="ts">
import { Component, Vue, Prop } from "vue-property-decorator";
import DatetimeField from "@/components/jobs/parameters/DatetimeField.vue";
import Timezones from "@/constants/timezones.json";
import { DateTime, LocalZone } from "luxon";
import "vue-datetime/dist/vue-datetime.css";

Vue.component("datetimefield", DatetimeField);

@Component
export default class JobTimeParameters extends Vue {
  @Prop() timeparams!: Record<string, any>;
  start!: string | null;
  end!: string | null;
  timezone!: string;
  step!: number;
  timezoneList: Array<string> = Timezones;
  errors!: Record<string, string>;

  data() {
    const zone = new LocalZone().name;
    return {
      errors: {},
      start: null,
      end: null,
      step: 60,
      timezone: zone
    };
  }
  setDataFields({
    start = null,
    end = null,
    step = 3600,
    timezone = new LocalZone().name
  }) {
    this.start = start;
    this.end = end;
    this.step = step / 60;
    this.timezone = timezone;
  }
  mounted() {
    if (this.timeparams) {
      this.setDataFields(this.timeparams);
    }
    this.emitParams();
  }
  emitParams() {
    if (this.start && this.end && this.start >= this.end) {
      this.errors = { "Start End": "Start must be before End." };
    } else {
      const timeParams = {
        start: this.start,
        end: this.end,
        step: this.step * 60,
        timezone: this.timezone
      };
      delete this.errors["Start End"];
      this.$emit("new-timeparams", timeParams);
    }
  }
  setStart(newStart: DateTime | null) {
    this.start = newStart ? newStart.toISO() : null;
    this.emitParams();
  }
  setEnd(newEnd: DateTime | null) {
    this.end = newEnd ? newEnd.toISO() : null;
    this.emitParams();
  }
}
</script>
<style scoped>
.vdatetime {
  display: inline-block;
}
</style>
