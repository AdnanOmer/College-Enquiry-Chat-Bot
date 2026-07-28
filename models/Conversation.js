const { getDB } = require("../config/db");

async function saveConversation(userMessage, botResponse) {
  try {
    const db = getDB();
    const conversations = db.collection("conversations");

    await conversations.insertOne({
      userMessage,
      botResponse,
      createdAt: new Date(),
    });

    console.log("[Conversation] Saved successfully");
  } catch (err) {
    console.warn("[Conversation] Could not save:", err.message);
  }
}

module.exports = { saveConversation };
