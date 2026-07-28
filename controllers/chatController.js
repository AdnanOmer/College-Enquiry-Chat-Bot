const CoordinatorAgent = require("../agents/CoordinatorAgent");
const { saveConversation } = require("../models/conversation");

exports.handleChat = async (req, res) => {
  try {
    const { message } = req.body;

    if (!message) {
      return res.status(400).json({ response: "❗ يرجى إدخال رسالة." });
    }

    const coordinator = new CoordinatorAgent();
    const result = await coordinator.processMessage(message); 
    

   
    saveConversation(message, result.response).catch(err => {
      console.warn("[chatController] Could not save conversation:", err.message);
    });

    return res.status(200).json(result);

  } catch (error) {
    console.error("❌ Error in chatController:", error.message);
    return res.status(500).json({
      response: "حدث خطأ أثناء معالجة رسالتك.",
      agent: "system"
    });
  }
};
