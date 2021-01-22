<!--
Component that displays a button to toggle a help button pop up button. When
used multiple times, only one help button will be shown at a time. Help pop
ups will close when the user clicks away.
-->
<template>
  <div class="help">
    <span v-if="helpText != undefined">
      <button @click="toggleHelp" @hideHelp="hideHelp" tabindex="-1">
        ?
      </button>
      <!-- accessible-hidden class used to keep the help text accessible as a
           target for aria-describedby
        -->
      <div
        v-bind:class="{ 'accessible-hidden': !show }"
        v-on:hide-help="hideHelp"
        v-click-away="hideHelp"
        :id="tagId"
        class="help-wrapper"
      >
        {{ helpText }}
      </div>
    </span>
  </div>
</template>
<script lang="ts">
import { Component, Prop, Vue } from "vue-property-decorator";

// extend HTMLElement interface to tell typescript our custom event is expected
interface HTMLElement {
  clickAway: () => void;
}
Vue.directive("click-away", {
  bind(el: any, binding: any, vnode: any) {
    el.clickAway = function(event: any) {
      if (
        !(el == event.target.nextElementSibling || el.contains(event.target))
      ) {
        vnode.context[binding.expression](event);
      }
    };
    document.body.addEventListener("click", el.clickAway);
  },
  unbind(el: any) {
    document.body.removeEventListener("click", el.clickAway);
  }
});

@Component
export default class HelpPopup extends Vue {
  show!: boolean;

  @Prop() helpText?: string;
  @Prop() tagId!: string;
  data() {
    return {
      show: false
    };
  }
  toggleHelp() {
    this.show = !this.show;
  }

  hideHelp() {
    this.show = false;
  }
}
</script>

<style scoped>
div.help {
  display: inline-block;
  position: relative;
}
.help-wrapper {
  position: absolute;
  padding: 0.5em;
  width: 300px;
  background-color: #fff;
  border: 1px solid black;
  border-radius: 5px;
  box-shadow: 1px 1px 5px #555;
  z-index: 1;
  top: 0;
  left: 100%;
}
</style>
