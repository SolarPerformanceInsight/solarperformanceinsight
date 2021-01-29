/* istanbul ignore file */
export default function download(filename: string, contents: Blob) {
  if (navigator.msSaveBlob) {
    navigator.msSaveBlob(contents, filename);
  } else {
    const link = document.createElement("a");
    link.href = URL.createObjectURL(contents);
    link.download = filename;
    link.target = "_blank";
    link.style.visibility = "hidden";
    link.dispatchEvent(new MouseEvent("click"));
    link.remove();
  }
}
