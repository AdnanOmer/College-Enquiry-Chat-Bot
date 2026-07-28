const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const path = require('path'); 

const chatRoutes = require('./routes/chatRoutes');

const app = express();


app.use(cors());
app.use(helmet());
app.use(
  helmet.contentSecurityPolicy({
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'", "https://cdn.jsdelivr.net"],
      styleSrc: ["'self'", "https://cdn.jsdelivr.net", "https://fonts.googleapis.com", "'unsafe-inline'"],
      fontSrc: ["'self'", "https://fonts.gstatic.com"],
      connectSrc: ["'self'", "https://cdn.jsdelivr.net"],
      imgSrc: ["'self'", "data:","https://new.mashreq.edu.sd", "https://i.ibb.co"],
      mediaSrc: ["'self'", "data:"]
    }
  })
);


app.use(express.json());


app.use(express.static(path.join(__dirname, 'public'))); 


app.use('/chat', chatRoutes);


app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});


app.use((err, req, res, next) => {
  console.error('[Error Middleware]', err);
  res.status(500).json({ error: 'Something went wrong' });
});

module.exports = app;
