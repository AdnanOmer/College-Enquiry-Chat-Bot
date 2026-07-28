const BaseAgent = require("./baseAgent");

class FeesAgent extends BaseAgent {
  constructor() {
    super("Fees", "عذرًا، لم أجد تفاصيل عن الرسوم الدراسية.");
  }
}

module.exports = FeesAgent;
