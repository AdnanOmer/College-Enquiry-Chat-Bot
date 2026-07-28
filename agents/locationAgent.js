const BaseAgent = require("./baseAgent");

class LocationAgent extends BaseAgent {
  constructor() {
    super("Location", "عذرًا، لم أجد تفاصيل عن الموقع.");
  }
}

module.exports = LocationAgent;
