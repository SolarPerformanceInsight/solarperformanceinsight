<template>
  <div class="help">
    <span v-if="helpText != undefined">
      <button @click.stop="showHelp">
        ?
      </button>
      <div v-if="show" v-click-away="hideHelp" class="help-wrapper">
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
      if (!(el == event.target || el.contains(event.target))) {
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
  data() {
    return {
      show: false
    };
  }
  showHelp() {
    this.show = true;
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
