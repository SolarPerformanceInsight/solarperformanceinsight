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
import { Component, Prop, Vue } from "vue-property-decorator";

@Component
export default class FileUpload extends Vue {
  data() {
    return {
      isLoading: false,
      errors: []
    };
  }
  setLoading(fileStatus) {
    this.isLoading = fileStatus;
  }
  processFile(e) {
    this.setLoading(true);

    const fileList = e.target.files;
    if (fileList.length > 1) {
      this.errors.push("Can only accept one file at a time.");
    } else {
      const file = e.target.files[0];
      const reader = new FileReader();

      reader.onload = f => this.$emit("uploadSuccess", f.target.result);
      reader.readAsText(file);

      this.errors = [];
    }

    this.setLoading(false);
  }
}
</script>
