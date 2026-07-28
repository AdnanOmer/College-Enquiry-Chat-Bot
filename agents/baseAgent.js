const { getDB } = require("../config/db");

class BaseAgent {
  constructor(category, defaultMessage) {
    this.category = category;
    this.defaultMessage = defaultMessage;
  }

  async getAnswer(question) {
    try {
      const db = getDB();
      const col = db.collection("EDU");
      const result = await col.findOne({ question });

      if (result?.answer) {
        console.log(`[${this.category}Agent] Returning answer from DB`);
        return result.answer;
      } else {
        console.log(`[${this.category}Agent] No answer found for:`, question);
        return this.defaultMessage;
      }
    } catch (error) {
      console.error(`[${this.category}Agent] Error:`, error.message);
      return "حدث خطأ أثناء جلب المعلومات.";
    }
  }
}

module.exports = BaseAgent;
