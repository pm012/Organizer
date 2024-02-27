from setuptools import setup, find_packages

setup(
    name = "Organizer",
    version="1.0",
    entry_point={
        "console_scripts":["bot-start=BotAssistant.bot_assistant_launcher:main"]
         },
        package=find_packages()
      )