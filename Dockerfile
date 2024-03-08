FROM python:3.12.2

ENV APP_HOME /ORGANIZER

WORKDIR $APP_HOME

COPY . .

RUN pip install -r $APP_HOME/BotAssistant/requirements.txt

EXPOSE 2828

ENTRYPOINT [ "python", "BotAssistant/BotAssistant/bot_assistant_launcher.py" ]
