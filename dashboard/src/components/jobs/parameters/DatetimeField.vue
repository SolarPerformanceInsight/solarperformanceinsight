<template>
  <div class="datetime-component inline">
    <div
      class="date-fields datetime-container inline"
      v-bind:class="{ invalid: currentDate && !currentDate.isValid }"
    >
      <span class="date-fields">
        <span class="date-field-wrapper">
          <input
            class="datetime-field date-field year"
            type="number"
            maxlength="4"
            max="2037"
            min="1901"
            placeholder="YYYY"
            v-model="year"
          />
        </span>
        <span class="date-field-wrapper">
          <input
            class="datetime-field date-field month"
            type="number"
            maxlength="2"
            min="1"
            max="12"
            placeholder="MM"
            v-model="month"
          />
        </span>
        <span class="date-field-wrapper">
          <input
            class="datetime-field date-field day"
            type="number"
            maxlength="2"
            min="1"
            :max="dayMax"
            placeholder="DD"
            v-model="day"
          />
        </span>
      </span>
    </div>
    <div
      class="date-fields datetime-container inline"
      v-bind:class="{ invalid: currentDate && !currentDate.isValid }"
    >
      <span class="time-fields">
        <span class="time-field-wrapper">
          <input
            class="datetime-field time-field hour"
            type="number"
            min="0"
            max="24"
            maxlength="2"
            placeholder="HH"
            v-model="hour"
          />
        </span>
        <span class="time-field-wrapper">
          <input
            class="datetime-field time-field minute"
            type="number"
            min="0"
            max="60"
            maxlength="2"
            placeholder="MM"
            v-model="minute"
          />
        </span>
      </span>
    </div>
    <help v-if="helpText" :helpText="helpText" />
    <div v-if="currentDate && currentDate.invalid" class="warning-text inline">
      {{ currentDate.invalid.explanation }}
    </div>
  </div>
</template>
<script lang="ts">
import { Component, Vue, Prop, Watch } from "vue-property-decorator";
import { DateTime } from "luxon";

@Component
export default class DatetimeField extends Vue {
  @Prop() timezone!: string;
  @Prop() helpText!: string;
  year!: number;
  month!: number;
  day!: number;
  hour!: number;
  minute!: number;

  data() {
    return {
      year: "",
      month: "",
      day: "",
      hour: "",
      minute: ""
    };
  }
  get currentDate() {
    let current: DateTime | null;
    try {
      current = DateTime.fromObject({
        year: this.year,
        month: this.month,
        day: this.day,
        hour: this.hour,
        minute: this.minute,
        zone: this.timezone
      });
    } catch {
      current = null;
    }
    return current;
  }
  get dayMax() {
    return this.currentDate ? this.currentDate.daysInMonth : 31;
  }
  @Watch("currentDate")
  emitTimeParams() {
    this.$emit("update-datetime", this.currentDate);
  }
}
</script>
<style scoped>
.inline {
  display: inline-block;
}
.datetime-container.invalid {
  border: 1px solid red;
}
input {
  font-family: monospace;
}
.datetime-container {
  border: 1px solid #ccc;
  width: fit-content;
  padding: 5px;
}
.datetime-field.year {
  width: 2.5em;
}
.datetime-field {
  width: 1.5em;
  border: 0;
  text-align: right;
}
span.date-fields,
span.time-fields {
  display: inline-block;
}
span.date-field-wrapper:not(:last-child)::after {
  content: "/";
}
span.time-field-wrapper:first-child::after {
  content: ":";
}
/* Remove adjustment up/down arrows from number fields */
input::-webkit-outer-spin-button,
input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
input[type="number"] {
  -moz-appearance: textfield;
}
.datetime-component {
  margin-top: 0.5em;
}
</style>
