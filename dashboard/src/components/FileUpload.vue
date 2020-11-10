<template>
  <div id="file-upload">
    <form enctype="multipart/form-data">
      <b>Upload System Metadata: </b>
      <input
        type="file"
        :disabled="isLoading"
        accept="application/*"
        @change="processFile"
      /><br />
    </form>
    <span v-if="isLoading">Uploading file...</span>
    <div v-if="errors">
      <ul>
        <li v-for="(error, index) in errors" :key="index">{{ error }}</li>
      </ul>
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";

interface HTMLInputEvent extends Event {
  target: HTMLInputElement & EventTarget;
}

@Component
export default class FileUpload extends Vue {
  errors!: Array<string>;
  isLoading!: boolean;

  data() {
    return {
      isLoading: false,
      errors: []
    };
  }

  setLoading(fileStatus: boolean) {
    this.isLoading = fileStatus;
  }

  processFile(e: HTMLInputEvent) {
    this.setLoading(true);

    if (e.target.files !== null) {
      const fileList = e.target.files;
      if (fileList.length > 1) {
        this.errors.push("Can only accept one file at a time.");
      } else {
        const file = e.target.files[0];
        const reader = new FileReader();

        // Typescript complains about f possibly being null, cant use a regular
        // function becasue need access to this.
        //@ts-ignore
        reader.onload = f => this.$emit("uploadSuccess", f.target.result);
        reader.readAsText(file);

        this.errors = [];
      }
    }
    this.setLoading(false);
  }
}
</script>
