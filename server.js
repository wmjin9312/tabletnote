const express = require('express');
const { spawn } = require('child_process');
const multer = require('multer');
const cors = require('cors');
const Papa = require('papaparse');
const fs = require('fs');
const app = express();
const port = 3000;
const mysql = require('mysql2');
const path = require('path');

app.use(cors());
app.use(express.static('public'));

const upload = multer({ dest: 'uploads/' });

app.get('/', (req, res) => {
  res.send('Hello, this is the default page.');
});

app.get('/upload', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'tablet.html'));
});

app.get('/run-yolo', (req, res) => {
  const pythonProcess = spawn('python', ['test1_v99.py']);
  let dataString = '';

  pythonProcess.stdout.on('data', (data) => {
    dataString += data.toString();
  });

  pythonProcess.stderr.on('data', (data) => {
    dataString += data.toString();
  });

  pythonProcess.on('close', (code) => {
    if (code === 0) {
      res.send(dataString);
    } else {
      res.status(500).send(dataString);
    }
  });
});

app.get('/run-ocr', (req, res) => {
  const pythonProcess = spawn('python', ['test2_v99.py']);
  let dataString = '';

  pythonProcess.stdout.on('data', (data) => {
    dataString += data.toString();
  });

  pythonProcess.stderr.on('data', (data) => {
    dataString += data.toString();
  });

  pythonProcess.on('close', (code) => {
    if (code === 0) {
      res.send(dataString);
    } else {
      res.status(500).send(dataString);
    }
  });
});

app.get('/run-category', (req, res) => {
  const pythonProcess = spawn('python', ['test3_v99.py']);
  let dataString = '';

  pythonProcess.stdout.on('data', (data) => {
    dataString += data.toString();
  });

  pythonProcess.stderr.on('data', (data) => {
    dataString += data.toString();
  });

  pythonProcess.on('close', (code) => {
    if (code === 0) {
      res.send(dataString);
    } else {
      res.status(500).send(dataString);
    }
  });
});

const db = mysql.createConnection({
  host: '127.0.0.1',
  user: 'root',
  password: '0000',
  database: 'testdb' // 사용할 데이터베이스 이름을 설정하세요
});

db.connect(err => {
  if (err) {
    console.error('Database connection failed: ' + err.stack);
    return;
  }

  console.log('Connected to database.');
});

app.post('/upload', upload.single('file'), (req, res) => {
  const file = req.file;
  if (!file) {
    return res.status(400).send('No file uploaded.');
  }
  const filePath = file.path;

    // 파일 읽기 및 파싱
    ret = []
    const fileData = fs.readFileSync(filePath, 'utf8');
    Papa.parse(fileData, {
      header: true,
      complete: (results) => {
        // 결과 데이터를 데이터베이스에 삽입
        results.data.forEach(row => {
  
          if(row.total_img_path){
            const query = 'INSERT INTO img_info (total_img_path, ocr_textfile_path, exam_class, subject, category_type) VALUES (?, ?, ?, ?, ?)';
            const values = [row.total_img_path, row.ocr_textfile_path, row.exam_class, row.subject, row.category_type];
            console.log('subcsv :', values)
            // 쿼리에 실제 값 삽입하여 로그 출력
            const filledQuery = query.replace(/\?/g, (match, i) => `'${values[i]}'`);
            console.log("Executing query:", filledQuery);
    
            // 실제 데이터베이스 쿼리 실행
            db.query(query, values, (err, result) => {
              if (err) {
                console.error('Failed to insert data', err);
              }
            });
            ret.push(row)
          }
        });
  
        res.json({ message: "Data uploaded and database updated", data: ret });
      }
    });
  });

app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});
