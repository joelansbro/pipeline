gnome-terminal --title="Celery" -e "python3 -m celery --app celeryBroker worker --loglevel=INFO -B -s ./data/beat.schedule"

gnome-terminal --title="Inbound Flask API" -e "python3 inboundAPI.py"