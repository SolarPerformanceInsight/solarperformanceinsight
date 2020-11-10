<template>
  <div class="home">
    <Model msg="model" />
  </div>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import Model from "@/components/Model.vue"; // @ is an alias to /src

@Component({
  components: {
    Model
  }
})
export default class ModelPage extends Vue {}
</script>
