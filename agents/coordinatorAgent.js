const axios = require("axios");
const LocationAgent = require("./locationAgent");
const FeesAgent = require("./feesAgent");
const AdmissionAgent = require("./admissionAgent");
const SubjectsAgent = require("./subjectsAgent");
const GeneralAgent = require("./generalAgent");

class CoordinatorAgent {
  async processMessage(message) {
    try {
      // 🔄 1. استدعاء Flask (TF-IDF classifier)
      const flaskResponse = await axios.post("http://localhost:5000/predict", {
        message,
      });

      const data = flaskResponse.data;
      const { category, question, similarity_score, error } = data;

      // ⚠️ تحقق من وجود خطأ أو غياب التصنيف
      if (error || !category) {
        return { response: "عذرًا، لم أفهم سؤالك. حاول مرة أخرى.", agent: "none" };
      }

      // ⚠️ تحقق من قوة التشابه
      if (typeof similarity_score === "number" && similarity_score < 0.4) {
        return { response: "عذرًا، لم أفهم سؤالك. حاول صياغته بطريقة أخرى.", agent: "none" };
      }

      // 🧠 2. اختيار العميل المناسب
      let agentInstance;
      switch (category) {
        case "location":
          agentInstance = new LocationAgent();
          break;
        case "fees":
          agentInstance = new FeesAgent();
          break;
        case "admission":
          agentInstance = new AdmissionAgent();
          break;
        case "subjects":
          agentInstance = new SubjectsAgent();
          break;
        default:
          agentInstance = new GeneralAgent();
      }

      // 📌 3. البحث عن الجواب من قاعدة البيانات
      console.log(`[CoordinatorAgent] Sending question to ${category} agent`);
      const answer = await agentInstance.getAnswer(question);

      console.log(`[CoordinatorAgent] Answer came from: ${category} agent`);
      return { response: answer, agent: category };
    } catch (error) {
      console.error("[CoordinatorAgent] Error:", error.message);
      return { response: "حدث خطأ أثناء معالجة الرسالة.", agent: "system" };
    }
  }
}

module.exports = CoordinatorAgent;
