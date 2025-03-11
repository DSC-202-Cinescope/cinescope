#!/bin/sh

flask_path="/jupyter-data/cinescope/jupyter-code/app.py"

echo "Starting Flask app..."
python $flask_path > /dev/null 2>&1 &

file_hash() {
    md5sum "$flask_path" | awk '{ print $1 }'
}

previous_hash=$(file_hash)

echo "Starting monitor app.py..."

while true; do
  sleep 10
  current_hash=$(file_hash)
  if [ "$current_hash" != "$previous_hash" ]; then
      echo "$flask_path has changed"
      pkill -f "python $flask_path"
      sleep 1
      python $flask_path > /dev/null 2>&1 &
      previous_hash=$current_hash
  fi
done