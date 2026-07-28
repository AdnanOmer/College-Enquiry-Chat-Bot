const BaseAgent = require("./baseAgent");

class GeneralAgent extends BaseAgent {
  constructor() {
    super("General", "عذرًا، لم أجد إجابة لهذا السؤال العام.");
  }
}
module.exports =  GeneralAgent;



