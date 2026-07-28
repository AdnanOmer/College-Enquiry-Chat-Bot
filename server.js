require('dotenv').config();

const http = require('http');


const app = require('./app');

const server = http.createServer(app);


const express = require('express');

const { connectDB } = require('./config/db');

const chatRoutes = require('./routes/chatRoutes');
 

app.use(express.json()); 
app.use('/', chatRoutes); 



async function startServer() {
    try {
        await connectDB();
        console.log('✅ MongoDB Connected!');
    } catch (err) {
        console.error('❗ MongoDB connection error:', err);
    }
}

startServer();


const PORT = process.env.PORT || 3000;
server.listen(PORT, () => console.log(`🚀 Server running on http://localhost:${PORT}`));


