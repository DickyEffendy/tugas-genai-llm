# StudyMate AI — Learning Material Analyzer

StudyMate AI adalah aplikasi Generative AI untuk membantu mahasiswa mengolah materi belajar menjadi ringkasan, konsep utama, istilah penting, dan pertanyaan latihan. Aplikasi menggunakan Python dan FastAPI sebagai backend serta Groq API untuk menghasilkan konten pembelajaran dalam format JSON terstruktur.

## 1. Informasi Project

- **Nama project:** StudyMate AI — Learning Material Analyzer
- **Use case:** Learning Material Analyzer
- **Deskripsi:** Pengguna mengirim teks materi pembelajaran. Aplikasi menganalisis teks tersebut dan menghasilkan ringkasan, konsep utama, istilah beserta definisinya, pertanyaan latihan beserta jawaban, dan perkiraan tingkat kesulitan. Tujuannya bukan sekadar menjawab pertanyaan seperti chatbot umum, tetapi mengubah materi menjadi perangkat belajar yang terstruktur.

## 2. Tech Stack

- **Python 3.15.0:** versi yang digunakan pada lingkungan pengerjaan project ini.
- **FastAPI:** membuat REST API dan dokumentasi interaktif.
- **Pydantic:** memvalidasi request dan struktur response.
- **Groq Python SDK (`AsyncGroq`):** mengirim prompt ke model bahasa.
- **Model LLM:** `openai/gpt-oss-120b`, dikonfigurasi melalui `.env`.
- **python-dotenv:** membaca konfigurasi dari file `.env`.
- **Pytest dan HTTPX:** pengujian dasar endpoint dan validasi.

## 3. Alur Aplikasi

Alur aplikasi adalah sebagai berikut:

```text
User Input
    ↓
FastAPI menerima request
    ↓
Pydantic memvalidasi input
    ↓
Aplikasi memilih System Prompt A, B, atau C
    ↓
Request dikirim ke Groq API
    ↓
Respons LLM diparsing dan divalidasi sebagai JSON
    ↓
FastAPI mengembalikan Structured Output
```

Pengguna mengirim teks materi melalui endpoint API. FastAPI menerima request dan Pydantic memeriksa format input serta versi prompt. Aplikasi lalu memilih system prompt yang diminta dan mengirim materi ke Groq API. Respons model diproses menjadi JSON dengan field yang sudah ditentukan. Jika input tidak valid, aplikasi mengembalikan error validasi; jika konfigurasi API atau layanan LLM bermasalah, aplikasi menangani kondisi tersebut melalui status error yang sesuai.

## 4. Struktur Project

```text
tugas-genai-llm/
├── main.py
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
├── sample_input.txt
├── run_experiments.py
├── tests/
│   └── test_api.py
└── experiments/
    └── actual_outputs.json
```

File `.env` digunakan secara lokal untuk menyimpan API key dan **tidak boleh diunggah ke GitHub**. File `.env.example` hanya berisi contoh konfigurasi dan tidak boleh berisi API key asli.

## 5. Instalasi dan Menjalankan Aplikasi

### 5.1. Persiapan environment

Buka terminal di folder project. Di Windows PowerShell, buat virtual environment jika belum tersedia:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Jika PowerShell memblokir aktivasi script, gunakan Command Prompt:

```bat
.venv\Scripts\activate.bat
```

Pastikan virtual environment aktif (biasanya ditandai dengan `(.venv)` di terminal), kemudian periksa versi Python:

```powershell
python --version
python -m pip --version
```

### 5.2. Instal dependency

```powershell
python -m pip install -r requirements.txt
```

### 5.3. Atur API key

1. Salin `.env.example` menjadi file `.env` di folder project.
2. Buka `.env` dan isi `GROQ_API_KEY` dengan API key milik sendiri dari Groq Console.
3. Pastikan nilai `GROQ_MODEL` sesuai model yang digunakan.
4. Simpan file `.env` secara lokal.

Contoh format **tanpa API key asli**:

```dotenv
GROQ_API_KEY=isi_api_key_milikmu
GROQ_MODEL=openai/gpt-oss-120b
```

Jangan menaruh API key asli di `main.py`, README, screenshot, atau repository GitHub.

### 5.4. Jalankan server

Dengan virtual environment aktif, jalankan:

```powershell
fastapi dev main.py
```

Alternatifnya:

```powershell
python -m uvicorn main:app --reload
```

Buka dokumentasi API di `http://127.0.0.1:8000/docs`. Server perlu tetap berjalan di terminal saat endpoint diuji.

## 6. API Endpoint

### `GET /`

Memastikan aplikasi berjalan. Saat diuji, endpoint ini mengembalikan HTTP `200` dengan pesan bahwa StudyMate AI sedang berjalan.

### `GET /health`

Memeriksa status aplikasi, provider, model, dan apakah API key telah dikonfigurasi. Endpoint ini tidak menampilkan nilai API key. Pada pemeriksaan awal, endpoint mengembalikan HTTP `200`; saat itu respons menunjukkan `api_key_configured: false`, sebelum konfigurasi API selesai.

### `POST /analyze`

Menganalisis teks dengan satu versi prompt. Field `prompt_version` menerima nilai `A`, `B`, atau `C`; versi default adalah `C` jika tidak ditentukan.

**Contoh request yang diuji:**

```json
{
  "text": "Machine learning adalah cabang kecerdasan buatan yang memungkinkan komputer mempelajari pola dari data. Model dilatih menggunakan data dan dievaluasi untuk mengetahui kemampuannya membuat prediksi pada data baru.",
  "prompt_version": "C"
}
```

Pengujian manual endpoint ini menghasilkan HTTP `200` dan response JSON dengan field `title`, `summary`, `key_concepts`, `key_terms`, `quiz_questions`, dan `difficulty_level`.

### `POST /experiments`

Menjalankan Prompt A, B, dan C dengan teks input yang sama untuk membandingkan hasilnya. Output eksperimen juga disimpan dalam `experiments/actual_outputs.json` oleh script eksperimen.

**Contoh request:**

```json
{
  "text": "Machine learning adalah cabang kecerdasan buatan yang memungkinkan komputer mempelajari pola dari data. Model dilatih menggunakan data dan dievaluasi untuk mengetahui kemampuannya membuat prediksi pada data baru."
}
```

## 7. Structured Output

Response utama memiliki enam field:

| Field | Fungsi |
|---|---|
| `title` | Judul singkat materi yang dianalisis. |
| `summary` | Ringkasan materi dengan bahasa yang mudah dipahami. |
| `key_concepts` | Daftar konsep utama dari materi. |
| `key_terms` | Daftar istilah penting beserta definisinya. |
| `quiz_questions` | Pertanyaan latihan beserta jawaban. |
| `difficulty_level` | Perkiraan tingkat materi: `pemula`, `menengah`, atau `lanjut`. |

Field tersebut dipilih karena StudyMate AI bertujuan membantu pengguna memahami dan mengulang materi belajar melalui ringkasan, konsep, istilah, dan latihan. Struktur JSON juga memudahkan hasil digunakan kembali oleh aplikasi lain.

### Cuplikan response aktual dari `POST /analyze`

Berikut cuplikan dari respons yang terlihat saat pengujian Swagger. Bagian array dipersingkat agar README tetap ringkas; respons lengkap ditampilkan oleh Swagger saat endpoint dijalankan.

```json
{
  "title": "Pengantar Machine Learning",
  "summary": "Machine learning adalah cabang kecerdasan buatan yang memungkinkan komputer mempelajari pola dari data. Model dilatih menggunakan data dan dievaluasi untuk membuat prediksi pada data baru.",
  "key_concepts": [
    "Machine learning",
    "Model training",
    "Model evaluation",
    "Prediksi pada data baru"
  ],
  "key_terms": [
    {
      "term": "Machine learning",
      "definition": "Cabang kecerdasan buatan yang memungkinkan komputer mempelajari pola dari data."
    },
    {
      "term": "Model",
      "definition": "Representasi yang dilatih menggunakan data untuk melakukan prediksi."
    },
    {
      "term": "Data",
      "definition": "Kumpulan informasi yang digunakan untuk melatih dan mengevaluasi model."
    }
  ],
  "quiz_questions": [
    {
      "question": "Apa yang dimaksud dengan machine learning?",
      "answer": "Cabang kecerdasan buatan yang memungkinkan komputer mempelajari pola dari data."
    }
  ],
  "difficulty_level": "pemula"
}
```

## 8. Eksperimen Prompt

Eksperimen A, B, dan C dijalankan dengan input materi machine learning yang sama. Ketiga eksperimen menggunakan schema JSON yang sama; hal yang dibandingkan adalah kualitas isi yang dihasilkan oleh prompt.

### Input yang digunakan

Input materi menjelaskan machine learning, tahapan umum prosesnya, perbedaan supervised learning dan unsupervised learning, pentingnya kualitas serta evaluasi data, dan beberapa penerapannya. Input yang digunakan untuk menjalankan eksperimen tersimpan dalam `sample_input.txt`.

### Prompt A — Prompt sederhana

```text
Ringkas materi berikut dalam Bahasa Indonesia. Ambil ide-ide utamanya dan buat hasil yang mudah dipahami.
```

**Ringkasan output aktual A:**

- Judul yang dihasilkan: `Pengenalan Machine Learning`.
- Ringkasan menjelaskan machine learning, tahapan pengumpulan dan pembersihan data, pemilihan serta pelatihan model, evaluasi, supervised dan unsupervised learning, serta contoh penerapan.
- Hasil berisi 7 konsep utama, 6 istilah, dan 4 pertanyaan latihan.
- Tingkat kesulitan yang dihasilkan: `menengah`.

**Actual Output A — Hasil JSON dari eksperimen**

```json
{
  "title": "Pengenalan Machine Learning",
  "summary": "Machine learning adalah cabang kecerdasan buatan yang memungkinkan komputer belajar pola dari data tanpa diprogram secara eksplisit. Prosesnya meliputi pengumpulan, pembersihan, pemilihan model, pelatihan, evaluasi, dan penggunaan model untuk prediksi. Pada supervised learning model belajar dari data berlabel, sedangkan unsupervised learning menemukan pola pada data tanpa label. Kualitas data sangat memengaruhi hasil, sehingga model harus dievaluasi pada data yang tidak dipakai saat pelatihan. Machine learning dapat diterapkan pada klasifikasi email, rekomendasi produk, prediksi permintaan, dan deteksi anomali, namun hasilnya dapat terpengaruh oleh bias, data tidak lengkap, atau perubahan pola dunia nyata.",
  "key_concepts": [
    "Proses machine learning: pengumpulan, pembersihan, pemilihan model, pelatihan, evaluasi, dan prediksi",
    "Supervised learning: belajar dari data berlabel",
    "Unsupervised learning: menemukan pola pada data tanpa label",
    "Evaluasi model pada data yang tidak digunakan saat pelatihan",
    "Pengaruh kualitas dan representasi data terhadap akurasi model",
    "Bias data dan perubahan pola dapat menurunkan performa model",
    "Aplikasi umum: klasifikasi email, rekomendasi produk, prediksi permintaan, deteksi anomali"
  ],
  "key_terms": [
    {
      "term": "Machine learning",
      "definition": "Cabang kecerdasan buatan yang memungkinkan komputer mempelajari pola dari data tanpa aturan eksplisit."
    },
    {
      "term": "Supervised learning",
      "definition": "Metode pembelajaran di mana model dilatih menggunakan data yang sudah memiliki label atau jawaban yang benar."
    },
    {
      "term": "Unsupervised learning",
      "definition": "Metode pembelajaran yang mencari struktur atau pola dalam data yang tidak memiliki label."
    },
    {
      "term": "Model",
      "definition": "Representasi matematis atau algoritma yang dipelajari dari data untuk melakukan prediksi atau klasifikasi."
    },
    {
      "term": "Bias data",
      "definition": "Kesalahan sistematis dalam data yang dapat menyebabkan model menghasilkan prediksi yang tidak akurat atau tidak adil."
    },
    {
      "term": "Anomali",
      "definition": "Pola atau kejadian yang menyimpang secara signifikan dari kebiasaan data normal, sering digunakan untuk deteksi penipuan atau kegagalan."
    }
  ],
  "quiz_questions": [
    {
      "question": "Apa perbedaan utama antara supervised learning dan unsupervised learning?",
      "answer": "Supervised learning menggunakan data berlabel untuk melatih model, sedangkan unsupervised learning mencari pola pada data tanpa label."
    },
    {
      "question": "Mengapa penting mengevaluasi model pada data yang tidak digunakan selama pelatihan?",
      "answer": "Untuk menilai kemampuan model dalam menggeneralisasi ke situasi baru dan menghindari overfitting."
    },
    {
      "question": "Sebutkan dua faktor yang dapat menurunkan akurasi model machine learning!",
      "answer": "Bias pada data dan perubahan pola di dunia nyata (concept drift)."
    },
    {
      "question": "Berikan contoh aplikasi machine learning dalam kehidupan sehari-hari.",
      "answer": "Klasifikasi email spam, rekomendasi produk di e-commerce, prediksi permintaan barang, atau deteksi anomali pada transaksi keuangan."
    }
  ],
  "difficulty_level": "menengah"
}
```
Output JSON lengkap untuk eksperimen tersimpan dalam `experiments/actual_outputs.json`.

### Prompt B — Role, Task, dan Context

```text
Peran: Kamu adalah asisten belajar untuk mahasiswa.
Task: Ringkas materi dan identifikasi konsep serta istilah penting.
Context: Materi yang diberikan adalah teks pembelajaran atau catatan kuliah.
Gunakan Bahasa Indonesia yang jelas dan mudah dipahami.
```

**Ringkasan output aktual B:**

- Judul yang dihasilkan: `Pengenalan Machine Learning`.
- Ringkasan membahas machine learning, proses pengolahan data dan model, supervised dan unsupervised learning, evaluasi, serta penerapan machine learning.
- Hasil berisi 7 konsep utama, 9 istilah, dan 4 pertanyaan latihan.
- Dibandingkan Prompt A, hasil B mencakup lebih banyak istilah terkait.

**Actual Output B — Hasil JSON dari eksperimen**

```json
{
  "title": "Pengenalan Machine Learning",
  "summary": "Machine learning (ML) adalah bagian dari kecerdasan buatan yang memungkinkan komputer belajar pola dari data tanpa diprogram secara eksplisit. Proses ML meliputi pengumpulan dan pembersihan data, pemilihan model, pelatihan, evaluasi, dan penggunaan model untuk prediksi. Pada supervised learning model belajar dari data berlabel, sedangkan pada unsupervised learning model mencari pola tanpa label. Kualitas data sangat memengaruhi hasil; model harus dievaluasi pada data yang tidak dipakai saat pelatihan untuk mengukur kemampuan pada situasi baru. ML dapat diterapkan pada klasifikasi email, rekomendasi produk, prediksi permintaan, dan deteksi anomali, namun hasil dapat terpengaruh oleh bias, data tidak lengkap, atau perubahan pola dunia nyata.",
  "key_concepts": [
    "Machine learning sebagai cabang kecerdasan buatan",
    "Tahapan umum machine learning: pengumpulan data, pembersihan data, pemilihan model, pelatihan, evaluasi, dan prediksi",
    "Perbedaan supervised learning (data berlabel) dan unsupervised learning (data tidak berlabel)",
    "Pengaruh kualitas dan representasi data terhadap performa model",
    "Pentingnya evaluasi model pada data yang tidak digunakan selama pelatihan",
    "Berbagai aplikasi machine learning: klasifikasi email, rekomendasi produk, prediksi permintaan, deteksi anomali",
    "Risiko bias, data tidak lengkap, dan perubahan pola yang dapat menurunkan akurasi model"
  ],
  "key_terms": [
    {
      "term": "Machine Learning",
      "definition": "Cabang kecerdasan buatan yang memungkinkan komputer belajar pola dari data tanpa aturan eksplisit."
    },
    {
      "term": "Kecerdasan Buatan (AI)",
      "definition": "Bidang ilmu komputer yang berfokus pada pembuatan sistem yang dapat meniru perilaku cerdas manusia."
    },
    {
      "term": "Supervised Learning",
      "definition": "Metode pembelajaran di mana model dilatih menggunakan data yang sudah memiliki label atau jawaban yang benar."
    },
    {
      "term": "Unsupervised Learning",
      "definition": "Metode pembelajaran di mana model mencari struktur atau pola dalam data yang tidak memiliki label."
    },
    {
      "term": "Model",
      "definition": "Representasi matematis atau algoritma yang dipelajari dari data untuk melakukan prediksi atau klasifikasi."
    },
    {
      "term": "Pelatihan (Training)",
      "definition": "Proses menyesuaikan parameter model menggunakan data pelatihan agar model dapat mengenali pola."
    },
    {
      "term": "Evaluasi",
      "definition": "Pengujian performa model pada data yang tidak pernah dilihat selama pelatihan untuk mengukur kemampuan generalisasi."
    },
    {
      "term": "Bias Data",
      "definition": "Kecenderungan kesalahan dalam data yang dapat menyebabkan model menghasilkan prediksi yang tidak adil atau tidak akurat."
    },
    {
      "term": "Deteksi Anomali",
      "definition": "Penerapan machine learning untuk mengidentifikasi data yang menyimpang secara signifikan dari pola normal."
    }
  ],
  "quiz_questions": [
    {
      "question": "Apa perbedaan utama antara supervised learning dan unsupervised learning?",
      "answer": "Supervised learning menggunakan data berlabel untuk melatih model, sedangkan unsupervised learning mencari pola pada data tanpa label."
    },
    {
      "question": "Mengapa penting untuk mengevaluasi model pada data yang tidak digunakan selama pelatihan?",
      "answer": "Untuk mengukur kemampuan model dalam menggeneralisasi ke situasi baru dan menghindari overfitting."
    },
    {
      "question": "Sebutkan dua faktor yang dapat menurunkan akurasi model machine learning!",
      "answer": "Bias pada data dan data yang tidak lengkap atau tidak representatif."
    },
    {
      "question": "Berikan contoh aplikasi machine learning dalam kehidupan sehari-hari.",
      "answer": "Klasifikasi email spam, rekomendasi produk di e-commerce, prediksi permintaan barang, atau deteksi anomali pada transaksi keuangan."
    }
  ],
  "difficulty_level": "menengah"
}
```

Output JSON lengkap untuk eksperimen tersimpan dalam `experiments/actual_outputs.json`.

### Prompt C — Role, Task, Context, Constraint, dan Output Format

```text
Peran: Kamu adalah asisten belajar akademik yang teliti dan tidak mengarang.
Task: Analisis materi belajar dan ubah menjadi ringkasan, konsep utama,
daftar istilah, dan pertanyaan latihan beserta jawabannya.
Context: Input dapat berupa catatan kuliah, artikel, atau penjelasan konsep.
Gunakan hanya informasi yang didukung oleh teks yang diberikan.
Constraint: Jawab dalam Bahasa Indonesia. Buat ringkasan 2–4 kalimat.
Pilih 3–6 konsep utama jika materi memang cukup informatif.
Definisi istilah dan jawaban kuis harus didukung oleh teks.
Jangan menebak atau menambahkan fakta eksternal seolah-olah berasal dari materi.
Jika teks berisi kata acak, tidak jelas, atau terlalu sedikit informasi,
jelaskan keterbatasannya pada summary dan kosongkan key_concepts, key_terms,
serta quiz_questions.
Output Format: Kembalikan JSON yang sesuai dengan schema API: title, summary,
key_concepts, key_terms, quiz_questions, difficulty_level.
Jangan gunakan Markdown atau code fence.
```

**Ringkasan output aktual C:**

- Hasil eksperimen normal berisi 5 konsep utama, 5 istilah, dan 4 pertanyaan latihan.
- Prompt C mengarahkan model untuk memakai informasi yang didukung teks, membatasi ringkasan, dan tidak membuat konsep jika input tidak informatif.
- Pada pengujian input acak, Prompt C menghasilkan judul `Materi Tidak Dapat Diproses` dan mengembalikan array konsep, istilah, serta pertanyaan latihan yang kosong.

**Actual Output C — Hasil JSON dari eksperimen**

```json
{
  "title": "Pengantar Machine Learning",
  "summary": "Machine learning adalah cabang kecerdasan buatan yang memungkinkan komputer mempelajari pola dari data tanpa aturan khusus. Prosesnya meliputi pengumpulan, pembersihan, pemilihan model, pelatihan, evaluasi, dan prediksi. Terdapat dua pendekatan utama, supervised learning dengan data berlabel dan unsupervised learning tanpa label, serta kualitas data sangat memengaruhi hasil model.",
  "key_concepts": [
    "Machine learning memungkinkan komputer belajar pola dari data tanpa aturan khusus",
    "Tahapan umum machine learning meliputi pengumpulan data, pembersihan data, pemilihan model, pelatihan, evaluasi, dan prediksi",
    "Supervised learning menggunakan data berlabel, sedangkan unsupervised learning mencari pola pada data tanpa label",
    "Evaluasi model harus dilakukan pada data yang tidak dipakai selama pelatihan untuk menilai kemampuan generalisasi",
    "Kualitas data memengaruhi hasil model; bias, data tidak lengkap, dan perubahan pola dapat menurunkan akurasi"
  ],
  "key_terms": [
    {
      "term": "Machine learning",
      "definition": "Cabang kecerdasan buatan yang memungkinkan komputer mempelajari pola dari data tanpa harus diprogram dengan aturan khusus untuk setiap situasi"
    },
    {
      "term": "Supervised learning",
      "definition": "Metode pembelajaran di mana model belajar dari contoh yang memiliki label"
    },
    {
      "term": "Unsupervised learning",
      "definition": "Metode pembelajaran yang mencari pola pada data tanpa label"
    },
    {
      "term": "Bias",
      "definition": "Kecenderungan model menghasilkan prediksi yang tidak akurat karena data yang digunakan memiliki kecenderungan atau kesalahan"
    },
    {
      "term": "Evaluasi model",
      "definition": "Proses menilai kemampuan model pada data yang tidak digunakan selama pelatihan untuk mengukur performa pada situasi baru"
    }
  ],
  "quiz_questions": [
    {
      "question": "Apa yang dimaksud dengan machine learning?",
      "answer": "Cabang kecerdasan buatan yang memungkinkan komputer mempelajari pola dari data tanpa harus diprogram dengan aturan khusus untuk setiap situasi"
    },
    {
      "question": "Sebutkan dua jenis pembelajaran dalam machine learning dan perbedaannya!",
      "answer": "Supervised learning, dimana model belajar dari data berlabel; dan unsupervised learning, dimana model mencari pola pada data tanpa label"
    },
    {
      "question": "Mengapa penting melakukan evaluasi model pada data yang tidak dipakai saat pelatihan?",
      "answer": "Untuk menilai kemampuan model dalam menggeneralisasi ke situasi baru dan memastikan tidak overfitting"
    },
    {
      "question": "Faktor apa saja yang dapat menurunkan akurasi model machine learning menurut teks?",
      "answer": "Bias pada data, data yang tidak lengkap, dan perubahan pola di dunia nyata"
    }
  ],
  "difficulty_level": "menengah"
}
```

Output JSON lengkap untuk eksperimen tersimpan dalam `experiments/actual_outputs.json`.

### Evaluasi Prompt A, B, dan C

Berdasarkan output eksperimen yang dicatat:

- **Prompt A** memberikan cakupan materi yang cukup luas dengan 7 konsep utama, 6 istilah, dan 4 pertanyaan latihan.
- **Prompt B** juga menghasilkan 7 konsep utama dan 4 pertanyaan latihan, tetapi memiliki 9 istilah sehingga cakupan istilahnya lebih luas.
- **Prompt C** menghasilkan 5 konsep utama, 5 istilah, dan 4 pertanyaan latihan. Instruksi constraint-nya lebih jelas, terutama untuk membatasi hasil agar tetap berdasarkan teks sumber dan menangani input yang tidak informatif.

Untuk tujuan StudyMate AI, Prompt C dipilih sebagai kandidat utama karena instruksinya lebih terarah dan memiliki aturan eksplisit untuk mengurangi pengarang-ngarangan. Ini adalah kesimpulan dari pengujian yang dilakukan, bukan jaminan bahwa Prompt C selalu paling baik pada semua materi.

## 9. Failure Case dan Perbaikan

Pengujian dilakukan pada input yang tidak informatif dan pada materi yang berisi pernyataan bertentangan. Tujuannya adalah melihat apakah model membuat konsep yang tidak didukung oleh input atau menjelaskan keterbatasan materi.

### Kasus 1 — Input berupa kata acak

**Input yang diuji:**

```text
asdf qwerty blah blah xyz random words no context just testing nothing about a subject and not an actual lecture
```

**Output awal — Prompt A, HTTP 200:**

```json
{
  "title": "Materi Tidak Tersedia",
  "summary": "Teks yang diberikan tidak dapat dirangkum karena teks tidak mengandung informasi yang bermakna.",
  "key_concepts": [],
  "key_terms": [],
  "quiz_questions": [],
  "difficulty_level": "pemula"
}
```

**Masalah atau peluang perbaikan:** Prompt A sudah menghindari pembuatan konsep dari kata acak, tetapi penjelasannya masih umum dan tidak secara eksplisit menyebut bahwa teks tidak memiliki konteks pembelajaran.

**Perbaikan yang diuji:** Input yang sama diuji kembali menggunakan Prompt C, yang memiliki constraint untuk menjelaskan keterbatasan input dan mengosongkan daftar konsep, istilah, serta pertanyaan jika teks tidak informatif.

**Output setelah perbaikan — Prompt C, HTTP 200:**

```json
{
  "title": "Materi Tidak Dapat Diproses",
  "summary": "Teks yang diberikan hanya berisi rangkaian kata acak tanpa konteks atau informasi yang dapat diidentifikasi sebagai materi pembelajaran, sehingga tidak dapat disarikan konsep, istilah, atau pertanyaan latihan.",
  "key_concepts": [],
  "key_terms": [],
  "quiz_questions": [],
  "difficulty_level": "pemula"
}
```

**Kesimpulan:** Pada input yang sama, Prompt C memberikan penjelasan yang lebih spesifik dan tetap tidak mengarang konsep, istilah, atau pertanyaan latihan. Perbaikan pada kasus ini dilakukan melalui pemilihan prompt; tidak diperlukan perubahan kode tambahan.

### Kasus 2 — Informasi yang bertentangan

Pengujian tambahan menggunakan teks yang memuat pernyataan tidak konsisten tentang supervised learning dan unsupervised learning. Teks menyebutkan supervised learning menggunakan data berlabel, tetapi juga menyatakan bahwa metode tersebut tidak menggunakan label; teks juga menyatakan unsupervised learning menggunakan data berlabel dan semua metode machine learning membutuhkan label.

- **Pengujian awal dengan Prompt A:** HTTP `200`. Aplikasi menghasilkan ringkasan pembelajaran normal, tetapi tidak secara eksplisit menandai kontradiksi pada materi sumber.
- **Pengujian ulang dengan Prompt C:** HTTP `200`. Judul respons menjadi `Supervised vs Unsupervised Learning (Informasi Tidak Konsisten)`. Ringkasan menyebutkan adanya informasi yang tidak konsisten, sementara `key_concepts`, `key_terms`, dan `quiz_questions` kosong.
- **Kesimpulan:** Prompt C lebih tepat untuk kasus ini karena memberi tanda bahwa materi sumber mengandung kontradiksi, alih-alih mengolah seluruh pernyataan seolah-olah konsisten. Pengujian ini tidak membuktikan bahwa Prompt C akan selalu mengenali semua jenis kontradiksi.

## 10. Hasil Pengujian Otomatis dan Manual

### Pengujian otomatis

Perintah yang dijalankan:

```powershell
python -m pytest -q
```

Hasil aktual:

```text
.....                                                                    [100%]
5 passed in 0.33s
```

Artinya, kelima tes yang tersedia berhasil dijalankan. Tes otomatis ini memeriksa perilaku dasar aplikasi, tetapi tidak menggantikan semua kemungkinan pengujian integrasi dengan provider LLM.

### Pengujian manual

- `GET /` berhasil dan mengembalikan HTTP `200`.
- `GET /health` berhasil dan mengembalikan HTTP `200`. Pada pemeriksaan awal, respons menunjukkan API key belum terkonfigurasi; setelah itu endpoint `POST /analyze` berhasil menghasilkan output materi ketika diuji.
- `POST /analyze` berhasil menghasilkan JSON terstruktur dengan HTTP `200`.
- Input acak diuji dengan Prompt A dan Prompt C untuk membandingkan cara keduanya menjelaskan input yang tidak informatif.
- Teks dengan informasi bertentangan diuji dengan Prompt A dan Prompt C untuk membandingkan penanganan kontradiksi.
- Script `python run_experiments.py` dijalankan untuk membandingkan Prompt A, B, dan C menggunakan input yang sama.

## 11. Refleksi Pribadi

Refleksi berikut disusun berdasarkan proses pengerjaan project: menyiapkan virtual environment, menjalankan server, menguji endpoint melalui Swagger, menjalankan eksperimen, dan menyiapkan repository. Silakan sesuaikan kata-katanya jika ada bagian yang tidak mencerminkan pengalamanmu.

1. **Bagian apa yang paling sulit dari project ini?**

   Bagian yang paling sulit adalah menyiapkan lingkungan kerja dan menjalankan aplikasi dengan benar. Saya sempat mengalami kendala saat mengaktifkan virtual environment melalui PowerShell, lalu perlu memastikan server FastAPI berjalan dan endpoint dapat diuji melalui Swagger. Saya juga perlu memahami cara menyimpan API key dengan aman sebelum mengunggah project ke GitHub.

2. **Bagian kode mana yang paling banyak dibantu oleh AI?**

   AI paling banyak membantu saya memahami struktur aplikasi FastAPI, penggunaan system prompt, validasi input dan output, penanganan error, serta langkah pengujian. AI juga membantu menjelaskan pesan error terminal dan menyusun dokumentasi README.

3. **Bagaimana bagian tersebut bekerja?**

   Pengguna mengirim teks dan versi prompt melalui endpoint. FastAPI menerima request, lalu Pydantic memvalidasi input. Aplikasi memilih prompt yang sesuai dan mengirim teks ke Groq API. Respons model kemudian diproses menjadi JSON dengan field yang sudah ditentukan. Hasil tersebut dikembalikan kepada pengguna melalui API.

4. **Apa kekurangan terbesar aplikasi jika digunakan oleh user sungguhan?**

   Kualitas ringkasan dan latihan masih bergantung pada isi materi, instruksi prompt, dan respons model. Walaupun output divalidasi dalam struktur JSON, hal tersebut tidak otomatis menjamin bahwa semua isi selalu benar. Pengguna tetap perlu memeriksa hasil, terutama untuk materi akademik yang penting.

5. **Jika provider LLM diganti, bagian mana yang perlu diubah?**

   Bagian yang perlu disesuaikan terutama client SDK, konfigurasi autentikasi, format request ke provider, nama model, dan cara mengambil serta memproses respons. Schema Pydantic dan endpoint dapat dipertahankan jika provider baru dapat menghasilkan data yang sesuai dengan struktur output yang digunakan.

6. **Apa satu improvement paling penting jika project dilanjutkan?**

   Improvement penting adalah menambahkan validasi kualitas isi yang lebih kuat agar aplikasi lebih konsisten membedakan materi yang jelas, terlalu singkat, dan saling bertentangan. Pengujian tambahan dengan lebih banyak contoh materi juga diperlukan untuk mengetahui batas kemampuan prompt.

## 12. Penggunaan AI

- **AI tools yang digunakan:** ChatGPT sebagai asisten untuk memahami instruksi, mempelajari kode, memperbaiki kendala saat menjalankan aplikasi, dan menyusun dokumentasi.
- **AI membantu bagian apa?** Membantu menjelaskan langkah setup Python dan FastAPI, membaca pesan error PowerShell, memahami endpoint, menyusun dan membandingkan prompt, menafsirkan hasil pengujian, serta merapikan README.
- **Bagian yang saya lakukan atau periksa sendiri:** Saya menjalankan perintah di terminal, mengaktifkan virtual environment, menjalankan server, menguji endpoint melalui Swagger, menjalankan eksperimen Prompt A/B/C, menguji input yang tidak informatif dan kontradiktif, memeriksa hasil `pytest`, serta menyiapkan `.gitignore` dan konfigurasi Git. Saya juga memeriksa output aktual sebelum mendokumentasikannya.

## 13. Pengumpulan ke GitHub

Nama repository yang digunakan untuk pengumpulan adalah `tugas-genai-llm`.

Sebelum push, pastikan:

- File `.env` tidak masuk ke commit atau repository.
- Folder `.venv/` tidak masuk ke repository.
- `.env.example` hanya berisi placeholder dan nama konfigurasi, bukan API key asli.
- `README.md`, `requirements.txt`, `main.py`, `run_experiments.py`, folder `tests/`, dan `experiments/actual_outputs.json` tersedia.

Periksa status Git:

```powershell
git status
```

Jika file belum pernah di-commit, tambahkan dan commit file yang aman:

```powershell
git add .
git status
git commit -m "Initial submission Tugas GenAI Apps"
git branch -M main
```

Lalu hubungkan ke repository GitHub yang sudah dibuat dengan nama `tugas-genai-llm`. Ganti `USERNAME` dengan username GitHub milik sendiri:

```powershell
git remote add origin https://github.com/USERNAME/tugas-genai-llm.git
git push -u origin main
```

Jika remote sudah ada, periksa terlebih dahulu dengan `git remote -v` agar tidak menambahkan remote yang sama dua kali.

## 14. Checklist Sebelum Submit

- [x] Server berhasil dijalankan dan dokumentasi `/docs` dapat dibuka.
- [x] `POST /analyze` berhasil dipanggil dan menghasilkan JSON terstruktur.
- [x] Prompt A, B, dan C telah dijalankan dengan input eksperimen yang sama.
- [x] Hasil eksperimen aktual disimpan dalam `experiments/actual_outputs.json`.
- [x] Failure case input acak diuji dengan Prompt A dan Prompt C.
- [x] Pengujian tambahan dilakukan pada teks yang berisi informasi bertentangan.
- [x] Tes otomatis berhasil: `5 passed in 0.33s`.
- [x] Repository GitHub sudah dibuat dan source code sudah di-push.
- [x] Periksa sekali lagi bahwa `.env` dan API key asli tidak ada di repository GitHub.

**Catatan:** Status checklist GitHub tetap belum dicentang sampai push benar-benar selesai dan repository diperiksa. Pastikan juga isi refleksi pribadi benar-benar sesuai dengan pengalamanmu sebelum menyerahkan tugas.
