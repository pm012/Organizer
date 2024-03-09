FROM python:3.12.2

ENV APP_HOME /ORGANIZER
ENV PATH="${PATH}:/root/.poetry/bin"

WORKDIR $APP_HOME

RUN curl -sSL https://install.python-poetry.org | python3 - --git https://github.com/python-poetry/poetry.git@master
ENV PATH="/root/.local/bin:$PATH"

RUN poetry --version

# Copy only the pyproject.toml and poetry.lock files to the working directory
COPY pyproject.toml poetry.lock $APP_HOME/

# Install dependencies using Poetry
RUN poetry install --no-root --no-dev

# Copy the rest of the application code
COPY . .

CMD poetry update && poetry run python BotAssistant/BotAssistant/bot_assistant_launcher.py
