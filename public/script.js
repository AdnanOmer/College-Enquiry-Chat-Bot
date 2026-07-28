const chatBody = document.querySelector(".chat-body");
const messageInput = document.querySelector(".message-input");
const sendMessageButton = document.querySelector("#send-message");
const emojiToggleButton = document.querySelector("#emoji-toggle");
const sendVoiceButton = document.querySelector("#send-voice");

function addMessage(text) {
  let messageContent = "";
  
  
  text = text.trim().replace(/[\u200E\u200F\u202A-\u202E]/g, '');


if (text && text.match(/\.(jpeg|jpg|gif|png|webp)$/i)) {

  messageContent = `
    <img src="header.jpg" alt="" width="50" height="50" />
    <div class="message-text">
      <a href="${text}"><img src="${text}" alt="bot-image" style="max-width:250px; border-radius:8px;" /></a>
    </div>`;
} else if (text && text.match(/^https?:\/\/[^\s]+$/i)) {
  
  messageContent = `
    <img src="header.jpg" alt="" width="50" height="50" />
    <div class="message-text">
      <a href="${text}" target="_blank" style="color:blue; text-decoration:underline;">${text}</a>
    </div>`;
} else {

  messageContent = `
    <img src="header.jpg" alt="" width="50" height="50" />
    <div class="message-text">${text}</div>`;
}

  const thinkingBubble = document.querySelector(".bot-message.thinking");
  if (thinkingBubble) thinkingBubble.remove();

  const messageDiv = createMessageElement(messageContent, "bot-message");
  chatBody.appendChild(messageDiv);
  chatBody.scrollTo({ top: chatBody.scrollHeight, behavior: "smooth" });
}


const userData = {
  message: null,
};

const createMessageElement = (content, ...classes) => {
  const div = document.createElement("div");
  div.classList.add("message", ...classes);
  div.innerHTML = content;
  return div;
};

const handleOutgoingMessage = (e) => {
  if (e) e.preventDefault();
  const text = messageInput.value.trim();
  if (!text) return;

  userData.message = text;
  messageInput.value = "";

  const messageContent = `<div class="message-text">${userData.message}</div>`;
  const outgoingMessageDiv = createMessageElement(messageContent, "user-message");
  chatBody.appendChild(outgoingMessageDiv);
  outgoingMessageDiv.querySelector(".message-text").textContent = userData.message;

  chatBody.scrollTo({ top: chatBody.scrollHeight, behavior: "smooth" });

  setTimeout(() => {
    const messageContent = `
      <img src="header.jpg" alt="" width="50" height="50" />
      <div class="message-text">
        <div class="thinking-indicator">
          <div class="dot"></div>
          <div class="dot"></div>
          <div class="dot"></div>
        </div>
      </div>`;
      
    const incomingMessageDiv = createMessageElement(messageContent, "bot-message", "thinking");
    chatBody.appendChild(incomingMessageDiv);
    chatBody.scrollTo({ top: chatBody.scrollHeight, behavior: "smooth" });
    generateBotResponse(userData.message);
  }, 600);
};

async function generateBotResponse(userMessage) {
  try {
    const response = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: userMessage })
    });

    if (!response.ok) {
      throw new Error("Failed to fetch from server");
    }

    const data = await response.json();
    console.log("🔍 Response from API:", data);

    
    const botText = String(data.response || "عذرًا، لم أتمكن من مساعدتك حالياً.");
    

    addMessage(botText);
  } catch (error) {
    console.error("Error in generateBotResponse:", error);
    addMessage("حدث خطأ أثناء معالجة الرسالة.");
  }
}



sendMessageButton.addEventListener("click", handleOutgoingMessage);

messageInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey && messageInput.value.trim()) {
    handleOutgoingMessage(e);
  }
});


const picker = new EmojiMart.Picker({
  theme: "light",
  skinTonePosition: "none",
  previewPosition: "none",
  onEmojiSelect: (emoji) => {
    const { selectionStart, selectionEnd } = messageInput;
    messageInput.setRangeText(emoji.native, selectionStart, selectionEnd, "end");
    messageInput.focus();
  },
});

let emojiVisible = false;
let emojiContainer = null;

emojiToggleButton.addEventListener("click", (event) => {
  event.stopPropagation();

  if (emojiVisible) {
    emojiContainer?.remove();
    emojiVisible = false;
  } else {
    emojiContainer = document.createElement("div");
    emojiContainer.className = "emoji-picker-container";
    emojiContainer.style.position = "absolute";

    const rect = emojiToggleButton.getBoundingClientRect();
    emojiContainer.style.top = `${rect.top + window.scrollY - 360}px`;
    emojiContainer.style.left = `${rect.left + window.scrollX}px`;

    emojiContainer.appendChild(picker);
    document.body.appendChild(emojiContainer);
    emojiVisible = true;
  }
});


document.addEventListener("click", (event) => {
  if (
    emojiVisible &&
    !emojiToggleButton.contains(event.target) &&
    !emojiContainer?.contains(event.target)
  ) {
    emojiContainer?.remove();
    emojiVisible = false;
  }
});


const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

if (SpeechRecognition) {
  const recognition = new SpeechRecognition();

  recognition.lang = "ar";            
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;

  let isRecording = false;

  sendVoiceButton.addEventListener("mousedown", () => {
    if (!isRecording) {
      recognition.start();
    }
  });

  ["mouseup", "mouseleave", "touchend"].forEach(evt => {
    sendVoiceButton.addEventListener(evt, () => {
      if (isRecording) {
        recognition.stop();
      }
    });
  });

  recognition.addEventListener("start", () => {
    isRecording = true;
    sendVoiceButton.classList.add("recording");
    console.log("🎙️ بدأ التسجيل...");
  });

  recognition.addEventListener("end", () => {
    isRecording = false;
    sendVoiceButton.classList.remove("recording");
    console.log("🛑 انتهى التسجيل.");
  });

  recognition.addEventListener("result", (event) => {
    const speechResult = event.results[0][0].transcript.trim();
    if (speechResult) {
      messageInput.value = speechResult;
      sendMessageButton.click();
    }
  });

  recognition.addEventListener("error", (event) => {
    console.error("حدث خطأ في التعرف على الصوت:", event.error);
    isRecording = false;
    sendVoiceButton.classList.remove("recording");
  });
} else {
  sendVoiceButton.disabled = true;
  sendVoiceButton.title = "ميزة التعرف على الصوت غير مدعومة في متصفحك";
}
