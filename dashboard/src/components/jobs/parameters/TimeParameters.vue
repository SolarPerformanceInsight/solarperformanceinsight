<template>
  <div class="time-parameters">
    <b>Start of the calculation period:</b>
    <input @change="emitParams" v-model="start" class="start" />
    <br />
    <b>End of the calculation period:</b>
    <input @change="emitParams" v-model="end" class="end" />
    <br />
    <b>Step:</b>
    <input
      @change="emitParams"
      v-model="step"
      type="number"
      min="1"
      max="60"
      step="1"
    />
    minutes
    <br />
    <b>Timezone:</b>
    <input @change="emitParams" v-model="timezone" class="timezone" />
  </div>
</template>
<script lang="ts">
import { Component, Vue } from "vue-property-decorator";

@Component
export default class JobTimeParameters extends Vue {
  start!: string;
  end!: string;
  timezone!: string;
  step!: number;

  data() {
    return {
      start: "2020-01-01T00:00+00:00",
      end: "2020-02-01T00:00+00:00",
      step: 60,
      timezone: "UTC"
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
