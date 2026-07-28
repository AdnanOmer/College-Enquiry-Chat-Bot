const BaseAgent = require("./baseAgent");

class SubjectsAgent extends BaseAgent {
  constructor() {
    super("Subjects", "عذرًا، لم أجد تفاصيل عن المقررات الدراسية.");
  }
}

module.exports = SubjectsAgent;
