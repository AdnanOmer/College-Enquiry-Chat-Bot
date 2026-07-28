const BaseAgent = require("./baseAgent");

class AdmissionAgent extends BaseAgent {
  constructor() {
    super("Addmission", "عذرًا، لم أجد معلومات عن القبول.");
  }
}

module.exports =  AdmissionAgent;
