const { MongoClient } = require("mongodb");
const dotenv = require("dotenv");
dotenv.config();

const MONGO_URI = process.env.MONGO_URI;
if (!MONGO_URI) throw new Error("MONGO_URI is not set in .env");

const client = new MongoClient(MONGO_URI);
let db = null;

async function connectDB() {
  if (!db) {
    await client.connect();
    db = client.db("chatbot");
    console.log("[DB] Connected successfully to MongoDB");
  }
  return db;
}

function getDB() {
  if (!db) throw new Error("[DB] Not connected yet. Call connectDB() first.");
  return db;
}

module.exports = { connectDB, getDB };
