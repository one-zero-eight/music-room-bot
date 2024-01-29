# InNoHassle-MusicRoomBot

## Project Installation

**Note that for successful use of this bot, you have to run
the [InNoHassle-MusicRoom](https://github.com/one-zero-eight/InNoHassle-MusicRoom) API.**

1. Install dependencies with [poetry](https://python-poetry.org/docs/).
    ```bash
    poetry install --no-root
    ```

2. Setup environment variables in `.env` file.

   Run
    ```bash
    cp .env.example .env
    ```
   And edit .env


3. Run the bot
    ```bash
    python -m src.main
    ```
   OR using Docker
    1. Create a network called <i>music-room</i>
    ```
   docker network create music-room
    ```
    2. Run bot
   ```
   docker-compose up --build
   ```
