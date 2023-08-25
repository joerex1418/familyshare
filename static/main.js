
// fetch("/path/to/url/endpoint")
// .then((response) => { return response.json(); })
// .then(data => {
//     // do stuff with your JSON data here
// })


function clearAtticPostForm() {

}

function submitNewAtticItem(e) {
  const formData = new FormData();
  const fileInput = document.getElementById("photo-upload")
  
  formData.append("title", document.getElementById("title").value)
  console.log(fileInput.files.length)
  for (let i = 0; i < fileInput.files.length; i++) {
    formData.append(`photo${i+1}`, fileInput.files[i])
  }
  formData.append("belongs-to", document.getElementById("belongs-to").value)
  formData.append("found-in", document.getElementById("found-in").value)
  formData.append("description", document.getElementById("description").value)
  formData.append("last-chance-date", document.getElementById("last-chance-date").value)
  formData.append("photo_count", fileInput.files.length)
  
  fetch(
    "/attic", {
      method: "POST", 
      body: formData
    }
    )
}

document.getElementById("create-attic-post-btn").addEventListener("click", function(e) {
  document.getElementById("modal-container").classList.add("active")
  document.getElementById("attic-post-modal").classList.add("active")
})
document.getElementById("exit-attic-post-modal-btn").addEventListener("click", function(e) {
  document.getElementById("modal-container").classList.remove("active")
  document.getElementById("attic-post-modal").classList.remove("active")
})
document.getElementById("submit-new-attic-item-btn").addEventListener("click", submitNewAtticItem)