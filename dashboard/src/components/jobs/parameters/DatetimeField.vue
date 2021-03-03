<template>
  <div class="datetime-container">
    <span class="date-fields">
      <span class="date-field-wrapper">
        <input class="datetime-field date-field year" type="number" maxlength="4" placeholder="yyyy">
      </span>
      <span class="date-field-wrapper">
        <input class="datetime-field date-field month" type="number" maxlength="2" min="1" max="12" placeholder="mm">
      </span>
      <span class="date-field-wrapper">
        <input class="datetime-field date-field day" type="number" maxlength="2" min="1" :max="dayMax" placeholder="dd">
      </span>
    </span>
    <span class="time-fields">
      <span class="time-field-wrapper">
        <input class="datetime-field time-field hour" type="number" min="0" max="24" maxlength="2" placeholder="HH">
      </span>
      <span class="time-field-wrapper">
        <input class="datetime-field time-field minute" type="number" min="0" max="60" maxlength="2" placeholder="MM">
      </span>
    </span>
  </div>
</template>
<script lang="ts">
import { Component, Vue, Prop } from "vue-property-decorator";
import Timezones from "@/constants/timezones.json";
import { LocalZone } from "luxon";
import { Datetime as DatePicker } from "vue-datetime";
import "vue-datetime/dist/vue-datetime.css";

Vue.component("datetime", DatePicker);

@Component
export default class DatetimeField extends Vue {
  dayMax!: number;

  data() {
    return {
      dayMax: 30
    };
  }
}
</script>
<style scoped>
.datetime-container {
  font-family: monospace;
  border: 1px solid #ccc;
  width: fit-content;
  padding: 5px;
}
.datetime-field.year {
  width: 2.5em;
}
.datetime-field{
  width: 2em;
  border: 0;
}
span.date-fields, span.time-fields {
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
input[type=number] {
  -moz-appearance: textfield;
}
</style>
