#!/bin/bash

echo "Generating endpoint config..."
python2 lib/endpoints/endpointscfg.py get_openapi_spec main.RoadkillApi --hostname roadkill911-180223.appspot.com

echo "Deploying endpoint config..."
gcloud service-management deploy roadkillv1openapi.json

echo "Updating app.yaml..."
CONFIGS=$(gcloud service-management configs list --service=roadkill911-180223.appspot.com
)

TOKENS=()

for i in $CONFIGS
do
  TOKENS+=("$i")
done

REVISION="${TOKENS[2]}"

cat app_templ.yaml > app.yaml
echo "  ENDPOINTS_SERVICE_VERSION: $REVISION" >> app.yaml

echo "Deploying app..."
gcloud app deploy
