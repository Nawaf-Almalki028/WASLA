function sendMessage() {
  const message = userInput.value.trim();
  if (message === "") {
    appendMessage("⚠️ Please type a message first.", "bot");
    return;
  }

  appendMessage(message, "user");
  userInput.value = "";

  fetch(`/support/chatbot/get-response/?message=${encodeURIComponent(message)}`)
    .then(res => res.json())
    .then(data => {
      // بدل ما يطلع JSON خام، نعرض نص الرد
      appendMessage(data.reply, "bot");
    })
    .catch(err => {
      appendMessage("⚠️ Error connecting to server.", "bot");
    });
}
