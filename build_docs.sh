npm i -g speccy
mkdir -p public
speccy resolve reference/anuto/openapi.yaml -o public/openapi.yaml
cp reference/anuto/index.html public