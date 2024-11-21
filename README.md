# M̶̡̹̤͝ͅÀ̶̝Ľ̸͈̣̀̓Ă̸͖̻̈́̈́̾Ṃ̸̟͛͠ ̵̦̳̃̈͝J̴̢͖̼̕U̶͙̓M̶̳̳̓̈́͆̑Ả̷̢̹̟͚͑̿͝T̶̳̯̬̺͘ ̷͈̞̼̒̀̀D̴̻̈́I̴̞̗͐͆͌͘ ̷̡͕̜͈̀̉̓̚S̴̳͌Ŏ̷̮̼̥̚R̵̙͉̙̾̊̐O̸̼̥͋̽̓N̴̘̦̒͋̀̚G̸̠͍̈́͂

## Introduction

This is a hybrid Next.js 14 + Python template. One great use case of this is to write Next.js apps that use Python AI libraries on the backend, while still having the benefits of Next.js Route Handlers and Server Side Rendering.

## How It Works

The Python/FastAPI server is mapped into to Next.js app under `/api/`.

This is implemented using [`next.config.js` rewrites](https://github.com/digitros/nextjs-fastapi/blob/main/next.config.js) to map any request to `/api/py/:path*` to the FastAPI API, which is hosted in the `/api` folder.

Also, the app/api routes are available on the same domain, so you can use NextJs Route Handlers and make requests to `/api/...`.

On localhost, the rewrite will be made to the `127.0.0.1:8000` port, which is where the FastAPI server is running.

In production, the FastAPI server is hosted as [Python serverless functions](https://vercel.com/docs/concepts/functions/serverless-functions/runtimes/python) on Vercel.

## Getting Started

First, create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Then, install the dependencies:

```bash
bun install
```

Then, run the development server(python dependencies will be installed automatically here):

```bash
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

The FastApi server will be running on [http://127.0.0.1:8000](http://127.0.0.1:8000) – feel free to change the port in `package.json` (you'll also need to update it in `next.config.js`).

## Resources

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.
- [FastAPI Documentation](https://fastapi.tiangolo.com/) - learn about FastAPI features and API.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js/) - your feedback and contributions are welcome!
