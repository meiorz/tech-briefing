import azure.functions as func  # pyright: ignore[reportMissingImports]
import datetime
import json
import logging

app = func.FunctionApp()

@app.timer_trigger(schedule="0 0 14 * * *", arg_name="timer",
                   rung_on_startup=False, use_monitor=False)
def daily_briefing(timer: func. TimerRequest) -> None:
    logging.info("Briefing run started")