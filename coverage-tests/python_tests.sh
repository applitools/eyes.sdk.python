RESULT=0
npm install
if [ $? -ne 0 ]; then
    RESULT=1
    echo "npm install have failed"
fi
npm run python:generate
if [ $? -ne 0 ]; then
    RESULT=1
    echo "npm run python:generate have failed"
fi
npm run python:run:parallel
if [ $? -ne 0 ]; then
    RESULT=1
    echo "npm run python:run:parallel have failed"
fi
npm run python:report
if [ $? -ne 0 ]; then
    RESULT=1
    echo "npm run python:report have failed"
fi
echo "RESULT = ${RESULT}"
if [ $RESULT -eq 0 ]; then
    exit 0
else
    exit 1
fi
