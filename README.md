# M̶̡̹̤͝ͅÀ̶̝Ľ̸͈̣̀̓Ă̸͖̻̈́̈́̾Ṃ̸̟͛͠ ̵̦̳̃̈͝J̴̢͖̼̕U̶͙̓M̶̳̳̓̈́͆̑Ả̷̢̹̟͚͑̿͝T̶̳̯̬̺͘ ̷͈̞̼̒̀̀D̴̻̈́I̴̞̗͐͆͌͘ ̷̡͕̜͈̀̉̓̚S̴̳͌Ŏ̷̮̼̥̚R̵̙͉̙̾̊̐O̸̼̥͋̽̓N̴̘̦̒͋̀̚G̸̠͍̈́͂

## Getting Started

### Prerequisite

- Bun
- Python

### Setup Backend

Create and activate a virtual environment:

Linux/macOS

```bash
cd src/backend/
python3 -m venv venv
source venv/bin/activate
```

Windows

```bash
cd src/backend/
python -m venv venv
.\venv\Scripts\activate
```

### How to start

- Build

```bash
cd src/frontend/
bun build
cd ../backend
bun build
```

- Start

```bash
cd src/frontend/
bun start
cd ../backend
bun start
```

### Run the development server(python dependencies will be installed automatically here):

- simple methode

```bash
cd src/frontend/
bun dev
```

- alternative (recommended)

1. Terminal A

```bash
cd src/frontend/
bun dev
```

2. Terminal B

```bash
cd src/backend/
bun dev:frontend
```

Open [http://localhost:3000](http://localhost:3000)

The FastApi server will be running on [http://localhost:8000](http://localhost:8000)

API docs (Swagger) [http://localhost:8000/docs](http://localhost:8000/docs)
API docs (ReDoc) [http://localhost:8000/redoc](http://localhost:8000/redoc)
